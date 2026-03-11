import os
import sys

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class LatchNode:
    inst_name: str
    clock: str
    net_name: str

    fanout: List['LatchNode'] = field(default_factory=list)
    fanin: List['LatchNode']  = field(default_factory=list)

    def add_fanout(self, to_inst: object):
        self.fanout.append(to_inst)

    def add_fanin(self, from_inst: object):
        self.fanin.append(from_inst)

class DirectionalLatchCGraph():
    """
    DirGraph for O(1) lookup
    """
    def __init__(self):  
        self.nodes: Dict[str, LatchNode] = {}
        self.clk_1_inst   = set()
        self.clk_2_inst   = set()
        self.unknown_inst = set()

    def add_node(self, LatchNode: object):
        """
        add node to directed graph
        add distinct insts to set
        checks for unknowns 
        """
        self.nodes[LatchNode.inst_name] = LatchNode
        
        if "clk_1" in LatchNode.clock.lower():
            self.clk_1_inst.add(LatchNode.inst_name)
        elif "clk_2" in LatchNode.clock.lower():
            self.clk_2_inst.add(LatchNode.inst_name)
        else:
            self.unknown_inst.add(LatchNode.inst_name)    
        return
    
    def add_edge(self, start: str, end: str):
        """
        add adjacent nodes
        """
        if start in self.nodes and end in self.nodes:
            self.nodes[start].add_fanout(self.nodes[end])
            self.nodes[end].add_fanin(self.nodes[start])
        return

class BuildLatchGraph():
    def __init__(self, design, env):
        self.design             = design
        self.two_phase_clkgate  = env.two_phase_clkgate
        self.seq_clock_pin_name = env.seq_clock_pin_name
        self.two_phase_clk      = env.two_phase_clk
        self.dgraph             = DirectionalLatchCGraph()
        self.latch_inst_map     = {}
        
    def dfs_latch_fanout(self, start_inst, seen_nets: set) -> set[str]:
        """
        perform dfs on start_inst to first
        latch node
        returns set of start instance sink names
        """
        reachable_latches = set()
        master = start_inst.getMaster()

        for MTerm in master.getMTerms():
            ITerm = start_inst.getITerm(MTerm)

            if str(MTerm.getIoType()) == "OUTPUT":
                net = ITerm.getNet()
                
                if not net:
                    continue

                net_name = net.getName()

                if net_name in seen_nets:
                    continue

                seen_nets.add(net_name)
                fanouts = net.getITerms()

                # find first sequential instance
                for fanout_obj in fanouts:

                    if not fanout_obj.getInst():
                        continue

                    sink_mterm = fanout_obj.getMTerm()
                    
                    if str(sink_mterm.getIoType()) != "INPUT":
                        continue

                    if self.two_phase_clk == 1:
                        if str(sink_mterm.getName()).upper() == self.seq_clock_pin_name:
                            continue
                    else:
                        if str(sink_mterm.getName()).upper() == "CLK":
                            continue            

                    if fanout_obj.getInst().getMaster().isSequential():
                        reachable_latches.add(fanout_obj.getInst().getName())
                    else:
                        # continue traverse through comb logic
                        descend = self.dfs_latch_fanout(fanout_obj.getInst(), seen_nets)
                        reachable_latches.update(descend)

        return reachable_latches

    def dfs_find_clock_domain(self, start_net, cd_nets):
        """
        perform dfs on start_net to first
        either clk 1 or clk 2 net_name
        """
        if not start_net:
            return "unknown"
        
        net_name = start_net.getName()
        
        if net_name == "clk_1":
            return "clk_1"
        elif net_name == "clk_2":
            return "clk_2"
        
        if net_name in cd_nets:
            return "unknown"
        
        cd_nets.add(net_name)
        
        # get output pin connected to this net
        # get that driver instance so we can recursively check its input nets
        for iterm in start_net.getITerms():
            
            if iterm.isOutputSignal():
                driver_inst = iterm.getInst()
            
                if not driver_inst:
                    continue

                driver_inst_master = driver_inst.getMaster()

                # if clock gated design first fanin will always be an and gate
                if self.two_phase_clkgate and "and" in driver_inst_master.getName():
                    b_iterm = driver_inst.getITerm(driver_inst_master.findMTerm("B"))
                    if b_iterm:
                        input_net = b_iterm.getNet()
                        if input_net:
                            result = self.dfs_find_clock_domain(input_net, cd_nets)
                            if result != "unknown":
                                return result
                else:
                    for driver_iterm in driver_inst.getITerms():
                        if driver_iterm.isInputSignal():
                            input_net = driver_iterm.getNet()
                            if input_net:
                                result = self.dfs_find_clock_domain(input_net, cd_nets)
                                if result != "unknown":
                                    return result
        
        return "unknown"
        
    def build(self) -> DirectionalLatchCGraph:
        """
        build directional latch graph by following
        each latch inst output through combinational
        paths
        
        return DirectionalLatchCGraph: object
        """
        update_interval = 1000
        count = 0
        latch_count = 0
        unknown_count = 0

        for inst in self.design.getBlock().getInsts():
            inst_name = inst.getName()
            net_name = None

            count += 1
            if count % update_interval == 0:
                print(f"[TWOCOLOR] Processing instance {count}...\r", end='', flush=True)

            if "FILLER" in inst_name:
                continue
            if "TAP" in inst_name:
                continue
            if "decap" in inst.getMaster().getName():
                continue
            if "ANTENNA" in inst_name:
                continue
            if self.design.isBuffer(inst.getMaster()):
                continue

            master = inst.getMaster()

            if self.design.isSequential(master):
                clock_domain = "unknown"
                
                mterm_outpin = master.findMTerm(self.seq_clock_pin_name)

                if mterm_outpin:
                    iterm_outpin = inst.getITerm(mterm_outpin)

                    if iterm_outpin:
                        net_outpin = iterm_outpin.getNet()
                        
                        if net_outpin:
                            net_name = net_outpin.getName()
                            
                            if self.two_phase_clk == 1:
                                cd_nets = set()
                                clock_domain = self.dfs_find_clock_domain(net_outpin, cd_nets)
                                
                                if clock_domain != "unknown":
                                    latch_count += 1
                                else:
                                    unknown_count += 1
                                    print("[TWOCOLOR][WARNING] Found unconnected instance.")
                                    
                            else:
                                if "clk" in net_name.lower():
                                    clock_domain = "clk"
                                    latch_count += 1
                                else:
                                    unknown_count += 1
                                    print("[TWOCOLOR][WARNING] Found unconnected instance.")
                                    
                if net_name is not None:
                    node = LatchNode(
                        inst_name=inst_name,
                        clock=clock_domain,
                        net_name=net_name
                    )
                    self.dgraph.add_node(node)
                    self.latch_inst_map[inst_name] = inst
                else:
                    print(f"[TWOCOLOR][ERROR] Found undefined net!")
                    print(f"  Instance name:     {inst_name}")
                    print(f"  Master name:       {master.getName()}")
                    print(f"  Clock domain:      {clock_domain}")
                    print(f"  Is sequential:     {self.design.isSequential(master)}")
                    print(f"  Clock pin name:    {self.seq_clock_pin_name}")
                    self.design.evalTclString("exit 0")
        print()

        # perform dfs on each inst through all combantional paths
        # stop search at first adjacent latch
        edge_count = 0
        for start_inst_name, inst_obj in self.latch_inst_map.items():
            seen_nets = set()

            # returns sink names
            fanouts = self.dfs_latch_fanout(inst_obj, seen_nets)

            # start instance fanout
            for fanout_inst_name in fanouts:
                self.dgraph.add_edge(start_inst_name, fanout_inst_name)

                # we also want check incorrect fanouts here for immediate exit
                if self.dgraph.nodes[start_inst_name].clock != self.dgraph.nodes[fanout_inst_name].clock:
                    edge_count += 1

                    if edge_count % 1000 == 0:
                        print(f"\r[TWOCOLOR] Two coloring {edge_count} passed...", end='', flush=True)
                    continue
                else:
                    print()
                    start_node = self.dgraph.nodes[start_inst_name]
                    fanout_node = self.dgraph.nodes[fanout_inst_name]
                    print()
                    print(f"[TWOCOLOR][ERROR] Two color violation found!")
                    print(f"  Start instance:  {start_inst_name}")
                    print(f"    Clock domain:  {start_node.clock}")
                    print(f"    Output net:    {start_node.net_name}")
                    print(f"  Fanout instance: {fanout_inst_name}")
                    print(f"    Clock domain:  {fanout_node.clock}")
                    print(f"    Input net:     {fanout_node.net_name}")
                    print(f"\nBoth latches are on the same clock domain: {start_node.clock}")
                    sys.exit("[TWOCOLOR][ERROR] Two color check failed!")
        print()

        print(f"\nCreated {edge_count} edges\n", end="")
        print(f"\nLATCH: {latch_count} | UNKNOWN: {unknown_count}\n")
        return self.dgraph

def latchgraph(design, env):
    builder = BuildLatchGraph(design, env)
    dgraph = builder.build()
    return dgraph
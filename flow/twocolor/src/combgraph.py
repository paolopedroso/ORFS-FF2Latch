from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class CombNode:
    inst_name: str
    clocked_by: str
    net_name: str

    # track fanouts/ins for comb edges
    fanout: List['CombNode'] = field(default_factory=list)
    fanin: List['CombNode'] = field(default_factory=list)

class DirectionalCombCGraph:
    def __init__(self):
        self.nodes: Dict[str, CombNode] = {} # ["inst", node()]
        self.clk_by_1_inst   = set()
        self.clk_by_2_inst   = set()
        self.unknown_inst    = set()
    
    def add_node():
        pass

    def add_edge():
        pass

from collections import deque
def bfs_comb_faninout(start_inst, design, seen_nets):
    pass

def dfs_comb_fanout(start_inst, design, seen_nets: set) -> set[str]:
    """
    
    """
    for MTerms in start_inst.MTerms():
        pass
    pass

def build_comb_graph(design) -> DirectionalCombCGraph:

    sccgraph = DirectionalCombCGraph()

    # netlist traversal
    comb_inst_map = {}

    comb_count = 0

    for inst in design.getBlock().getInsts():
        inst_name = inst.getName()
        
        if "FILLER" in inst_name:
            continue
        if "TAP" in inst_name:
            continue
        if "decap" in inst.getMaster().getName():
            continue

        # skip antennas and buffers
        if "ANTENNA" in inst_name:
            continue
        if design.isBuffer(inst.getMaster()):
            continue
        
        # we look at every non-sequential cell
        if inst.getMaster().isSequential() == False:
            comb_count += 1

            print(f"CombGraph MASTER {inst.getMaster().getName()} | INST {inst.getName()}")

            

    print(f"Total Comb logic: {comb_count}")

        
def combgraph(design):
    
    build_comb_graph(design)

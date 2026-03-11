import os
import json
from dataclasses import dataclass, asdict, field
# from plot_power import plot_single_power_breakdown

@dataclass
class PowerMetrics:
    internal: float
    switching: float
    leakage: float
    total: float

@dataclass
class PowerReport():
    """Complete power report for a design"""
    sequential: PowerMetrics
    combinational: PowerMetrics
    clock: PowerMetrics
    gated: PowerMetrics
    design_total: PowerMetrics
    
    def to_nested_json(self, filepath, design_name, flow_variant):
        """Save to deeply nested JSON structure"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
        else:
            data = {"designs": {}}
        
        if "designs" not in data:
            data["designs"] = {}
        if design_name not in data["designs"]:
            data["designs"][design_name] = {}
        if "flow_variants" not in data["designs"][design_name]:
            data["designs"][design_name]["flow_variants"] = {}

        data["designs"][design_name]["flow_variants"][flow_variant] = {
            "sequential": asdict(self.sequential),
            "combinational": asdict(self.combinational),
            "clock": asdict(self.clock),
            "gated": asdict(self.gated),
            "design_total": asdict(self.design_total)
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_power_data(self, json_file, design_name, flow_variant=None):
        
        try: 
            if design_name not in json_file["designs"]:
                print(f"Warning: {design_name} not found in {json_file}")
        except: FileNotFoundError
        
        pass

class PowerAnalysis():
    def __init__(self, design, env):
        self.env = env
        self.design = design
        self.flow_home = env.flow_home
        self.flow_variant = env.flow_variant
        self.design_nickname = env.design_nickname
        self.two_phase_clkgate = env.two_phase_clkgate

        self.plot_dir = f"{self.flow_home}/twocolor/plots"
        self.json_dir = f"{env.flow_home}/twocolor/json"
        self.json_power_file = f"{self.json_dir}/power_metrics.json"
        self.report_dir = f"{env.flow_home}/twocolor/reports"
        self.report_power_file = f"{self.report_dir}/report_power_{self.design_nickname}_variant_{self.flow_variant}.rpt"
        self.clock_gating_power_file = f"{self.report_dir}/clock_gating_power_{self.design_nickname}_{self.flow_variant}.rpt"
        
        if not os.path.exists(self.plot_dir):
            os.mkdir(self.plot_dir)

        if not os.path.exists(self.report_dir):
            os.mkdir(self.report_dir)

        if not os.path.exists(self.json_dir):
            os.mkdir(self.json_dir)

    def report_power(self, gated_power):
        seq_internal, seq_switching, seq_leakage, seq_total = 0, 0, 0, 0
        comb_internal, comb_switching, comb_leakage, comb_total = 0, 0, 0, 0
        clock_internal, clock_switching, clock_leakage, clock_total = 0, 0, 0, 0
        total_internal, total_switching, total_leakage, total_total = 0, 0, 0, 0

        if self.two_phase_clkgate:
            gated_internal  = float(gated_power[0])
            gated_switching = float(gated_power[1])
            gated_leakage   = float(gated_power[2])
            gated_total     = float(gated_power[3])
        else:
            gated_internal  = 0
            gated_switching = 0
            gated_leakage   = 0
            gated_total     = 0

        os.makedirs(os.path.dirname(self.report_power_file), exist_ok=True)
        
        self.design.evalTclString(f"report_power > {self.report_power_file}")

        if not os.path.exists(self.report_power_file):
            print("Error: Power report file not created")
            return

        with open(self.report_power_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                power_metrics = line.split()
                
                if len(power_metrics) < 5:
                    continue
                
                row_type = power_metrics[0]
            
                if row_type == "Sequential":
                    seq_internal  = float(power_metrics[1])
                    seq_switching = float(power_metrics[2])
                    seq_leakage   = float(power_metrics[3])
                    seq_total     = float(power_metrics[4])
                    
                elif row_type == "Combinational":
                    comb_internal  = float(power_metrics[1])
                    comb_switching = float(power_metrics[2])
                    comb_leakage   = float(power_metrics[3])
                    comb_total     = float(power_metrics[4])
                    
                elif row_type == "Clock":
                    clock_internal  = float(power_metrics[1])
                    clock_switching = float(power_metrics[2])
                    clock_leakage   = float(power_metrics[3])
                    clock_total     = float(power_metrics[4])
                    
                elif row_type == "Total":
                    total_internal  = float(power_metrics[1])
                    total_switching = float(power_metrics[2])
                    total_leakage   = float(power_metrics[3])
                    total_total     = float(power_metrics[4])
        
        power_report = PowerReport(
            sequential=PowerMetrics(seq_internal, seq_switching, seq_leakage, seq_total),
            combinational=PowerMetrics(comb_internal, comb_switching, comb_leakage, comb_total),
            clock=PowerMetrics(clock_internal, clock_switching, clock_leakage, clock_total),
            gated=PowerMetrics(gated_internal, gated_switching, gated_leakage, gated_total),
            design_total=PowerMetrics(total_internal, total_switching, total_leakage, total_total)
        )

        power_report.to_nested_json(self.json_power_file, self.design_nickname, self.flow_variant)

        # Main power report
        main_power_report = (
            f"\n"
            f"Power Report Summary:\n"
            f"{'-'*60}\n"
            f"Sequential Power:    {power_report.sequential.total:.6e} W\n"
            f"Combinational Power: {power_report.combinational.total:.6e} W\n"
            f"Clock Network Power: {power_report.clock.total:.6e} W\n"
            f"Total Design Power:  {power_report.design_total.total:.6e} W\n"
            f"\n"
            f"Clock + Gated Power:  {(power_report.clock.total - power_report.gated.total):.6e} W + {power_report.gated.total:.6e} W\n"
        )

        # And gater power report
        and_gater_report = (
            f"\n"
            f"And Gater Summary\n"
            f"{'-'*60}\n"
            f"internal: {power_report.gated.internal:.6e} W\n"
            f"switching: {power_report.gated.switching:.6e} W\n"
            f"leakage: {power_report.gated.leakage:.6e} W\n"
            f"total: {power_report.gated.total:.6e} W\n"
        )

        # print to terminal
        self.design.evalTclString("report_power")
        print(main_power_report)
        print(and_gater_report)

        with open(self.report_power_file, 'a') as f:
            print(main_power_report, file=f)
            print(and_gater_report, file=f)

        return {
            "seq_total": power_report.sequential.total,
            "comb_total": power_report.combinational.total,
            "clock_total": power_report.clock.total,
            "total_total": power_report.design_total.total,
            "gated_total": power_report.gated.total
        }
        
    def _get_and_gater_power(self):
        internal, switching, leakage, total = 0, 0, 0, 0
        
        if not self.two_phase_clkgate:
            return [internal, switching, leakage, total]
        
        all_and_gaters = " ".join(self._get_and_gaters())
        curly_braced_str = "{" + all_and_gaters + "}"

        self.design.evalTclString(f"report_power -instances {curly_braced_str} > {self.clock_gating_power_file}")

        if not os.path.exists(self.clock_gating_power_file):
            print("Error: Power report file not created")
            return

        with open(self.clock_gating_power_file, 'r') as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue
                
                if "Internal" in line or "Power" in line or "---" in line:
                    continue

                power_metrics = line.split()
                
                if len(power_metrics) < 4:
                    continue

                internal  += float(power_metrics[0])
                switching += float(power_metrics[1])
                leakage   += float(power_metrics[2])
                total     += float(power_metrics[3])

        return [internal, switching, leakage, total]

    def _get_and_gaters(self):
        """ find all gated logic connected to latch enable """
        gated_latches = 0
        and_gaters = set()

        for inst in self.design.getBlock().getInsts():
            inst_name = inst.getName()

            if "FILLER" in inst_name:
                continue
            if "TAP" in inst_name:
                continue
            if "decap" in inst.getMaster().getName():
                continue
            if "ANTENNA" in inst_name:
                continue

            # add power here
            if self.design.isBuffer(inst.getMaster()):
                if "clk" not in inst_name:
                    continue

            inst_master = inst.getMaster()

            # get all seq logic
            if inst_master.isSequential() == False:
                continue

            latch_mterm_output = inst_master.findMTerm("GATE")

            latch_iterms = inst.getITerm(latch_mterm_output)
            latch_nets = latch_iterms.getNet()

            driver_inst = None
            for iterm in latch_nets.getITerms():
            
                iterm_name = iterm.getName()

                if not iterm_name:
                    continue

                # clk_1 is not gated
                # latches clocked by clk_2 will not have "clk_2"
                # in the net name since its gated
                if "clk_1" in iterm_name or "buf" in iterm_name:
                    continue

                if iterm_name in and_gaters:
                    continue

                # get driver
                if iterm.isOutputSignal():
                    driver_inst = iterm.getInst()
                    break
            
            if not driver_inst:
                continue

            and_gaters.add(driver_inst.getName())
            gated_latches += 1

        print(
        f"Found {gated_latches} gated latches."
        f"")
        return and_gaters

    def do_power_analysis(self):
        switching_activity = 0.1
        self.design.evalTclString(f"set_power_activity -input -activity {float(switching_activity)}")
        print(f"set_power_activity -input -activity {float(switching_activity)}")

        and_gater_power = self._get_and_gater_power()

        power_data = self.report_power(and_gater_power)


        # plot_single_power_breakdown(power_data, self.plot_dir, env.design_nickname, env.flow_variant)
        
def power_analysis(design, env):
    power = PowerAnalysis(design, env)
    power.do_power_analysis()
    return
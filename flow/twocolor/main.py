import os
import odb
import openroad
from openroad import Design, Tech

from src import twocolor_test
from src.env import Environment
from src.plot_latchgraph import PlotLatchGraph
from src.latchgraph import latchgraph
from src.power_analysis import power_analysis
from src.plot_power import plot_power

openroad.openroad_version()

env = Environment()

def load():
    tech = Tech()

    for lef_file in env.all_lef_files:
        if lef_file == 'None':
            continue
        tech.readLef(lef_file)
        print(f"loaded {lef_file}")
    
    for lib_file in env.all_lib_files:
        if lib_file == 'None':
            continue
        tech.readLiberty(lib_file)
        print(f"loaded {lib_file}")

    design = Design(tech)
    design.readDb(env.odb_file)

    design.evalTclString(f"read_spef {env.spef_file}")
    design.evalTclString(f"read_sdc {env.sdc_file}")

    print("Successfully loaded design.")
    
    return tech, design

if __name__ == "__main__":
    tech, design = load()

    if env.run_latchgraph:
        latch_graph = latchgraph(design, env)

        if env.run_test_suite:
            twocolor_test.run_all_tests(latch_graph)
    
    if env.save_plot:
        print(f"Saving plot to {os.environ.get('TC_PLOT_PATH')}")
        latch_plot = PlotLatchGraph(latch_graph, env)
        latch_plot.plot_latchgraph(design,env)
    
    if env.do_power_analysis:
        power_analysis(design, env)
        plot_power(env)


    design.evalTclString("exit 0")
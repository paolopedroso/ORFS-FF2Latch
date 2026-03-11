import os

import networkx as nx
import matplotlib
import matplotlib.pyplot as plt

from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from pathlib import Path

from src.latchgraph import DirectionalLatchCGraph

class PlotLatchGraph:
    def __init__(self, dgraph: DirectionalLatchCGraph, env):
        self.dgraph = dgraph 
        self.two_phase_clk = env.two_phase_clk
        self.output_format = env.output_format
        self.graph_name = env.graph_name
        self.multi_dir_graph = nx.MultiDiGraph()
        self.locations = {}
        self.node_colors = []
        
        self.unidirectional_edges = []
        self.bidirectional_edges = []
        
        self.unidirectional_colors = []
    
    def get_latches_location(self, design):
        dbu_per_micron = design.getBlock().getDbUnitsPerMicron()
        
        for inst_name in self.dgraph.nodes.keys():
            inst = design.getBlock().findInst(inst_name)
            if inst:
                # get x, y axis
                location = inst.getLocation()
                self.locations[inst_name] = (
                    location[0] / dbu_per_micron,
                    location[1] / dbu_per_micron
                )
    
    def add_latchgraph_edges(self):
        """
        Add edges and detect bidirectional connections
        """
        all_edges = set()
        bidirectional_pairs = set()
        
        for inst_name, node in self.dgraph.nodes.items():
            for fanout_node in node.fanout:
                edge = (inst_name, fanout_node.inst_name)
                reverse_edge = (fanout_node.inst_name, inst_name)
                
                all_edges.add(edge)
                
                # Check if reverse edge exists
                if reverse_edge in all_edges:
                    pair = tuple(sorted([inst_name, fanout_node.inst_name]))
                    bidirectional_pairs.add(pair)
        
        processed_bidirectional = set()
        
        for inst_name, node in self.dgraph.nodes.items():
            for fanout_node in node.fanout:
                edge = (inst_name, fanout_node.inst_name)
                pair = tuple(sorted([inst_name, fanout_node.inst_name]))
                
                self.multi_dir_graph.add_edge(inst_name, fanout_node.inst_name)
                
                # Check if this is bidirectional
                if pair in bidirectional_pairs:
                    if pair not in processed_bidirectional:
                        self.bidirectional_edges.append(edge)
                        processed_bidirectional.add(pair)
                else:
                    # color by target clock domain
                    self.unidirectional_edges.append(edge)
                    
                    # TODO: fix
                    if self.two_phase_clk:
                        if node.clock == "clk_1":
                            self.unidirectional_colors.append('#4169E1')
                        elif node.clock == "clk_2":
                            self.unidirectional_colors.append('#DC143C')
                        else:
                            self.unidirectional_colors.append('#95A5A6')
                    else:
                        if fanout_node.clock == "clk":
                            self.unidirectional_colors.append('#DC143C')
                        else:
                            self.unidirectional_colors.append('#95A5A6')        
        return

    def color_latches(self):
        for node_name in self.multi_dir_graph.nodes():
            node = self.dgraph.nodes[node_name]

            if self.two_phase_clk:
                if "clk_1" in node.clock.lower():
                    self.node_colors.append('#4169E1')
                elif "clk_2" in node.clock.lower():
                    self.node_colors.append('#DC143C')
                else:
                    self.node_colors.append('#95A5A6')
            else:
                if "clk" in node.clock.lower():
                    self.node_colors.append('#DC143C')
                else:
                    self.node_colors.append('#95A5A6')              

    def plot(self, save_path=None):
        fig, ax = plt.subplots(figsize=(14, 10))

        nx.draw_networkx_nodes(
            self.multi_dir_graph,
            pos=self.locations,
            node_size=30,
            node_color=self.node_colors,
            alpha=0.5,
            ax=ax
        )

        if self.unidirectional_edges:
            nx.draw_networkx_edges(
                self.multi_dir_graph,
                pos=self.locations,
                edgelist=self.unidirectional_edges,
                edge_color=self.unidirectional_colors,
                arrows=True,
                arrowsize=3,
                width=1.0,
                alpha=0.3,
                arrowstyle='->',
                ax=ax
            )
        
        # color bidirection edges to purple
        if self.bidirectional_edges:
            nx.draw_networkx_edges(
                self.multi_dir_graph,
                pos=self.locations,
                edgelist=self.bidirectional_edges,
                edge_color='#9B59B6',
                arrows=True,
                arrowsize=3,
                width=1.0,
                alpha=0.5,
                arrowstyle='<->',
                ax=ax
            )
        
        legend_elements = [
            Patch(facecolor='#4169E1', label='clk_1 nodes'),
            Patch(facecolor='#DC143C', label='clk_2 nodes'),
            Patch(facecolor='#95A5A6', label='unknown nodes'),
            Line2D([0], [0], color='#4169E1', linewidth=1, label='clk_1 edges'),
            Line2D([0], [0], color='#DC143C', linewidth=1, label='clk_2 edges'),
            Line2D([0], [0], color='#9B59B6', linewidth=1, label='bidirectional'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=12)
        
        ax.set_title(self.graph_name, fontsize=16)
        ax.set_xlabel("X Position (µm)", fontsize=12)
        ax.set_ylabel("Y Position (µm)", fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved plot to {save_path}\n")
            plt.close(fig)

    
    def plot_latchgraph(self, design, env):
        self.get_latches_location(design)
        self.add_latchgraph_edges()
        self.color_latches()

        base_dir = f"{env.flow_home}/twocolor/plots"
        
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        
        file_name = f"latchgraph_{env.design_nickname}_{env.flow_variant}"

        self.plot(f"{base_dir}/{file_name}")

        print(f"Added {self.multi_dir_graph.number_of_edges()} total edges")
        print(f"{len(self.unidirectional_edges)} unidirectional")
        print(f"{len(self.bidirectional_edges)} bidirectional pairs")
        return

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.power_analysis import PowerAnalysis

class PlotPower(PowerAnalysis):
    def __init__(self, design, env):
        super().__init__(design, env)
        
        self.tech_json_file = self.env.tech_json_file
        self.catagories = ['Sequential', 'Combinational', 'Clock Network']
        self.bar_stack = ['Internal', 'Switching', 'Leakage']
        
        try:
            if os.path.exists(self.json_power_file):
                with open(self.json_power_file, 'r') as f:
                    self.json_power_data = json.load(f)
        except: FileNotFoundError

    def plot_all_power_breakdown(self, designs: dict):
            data = []
            index_labels = []

            for design_name, flow_variants in designs.items():

                if design_name not in self.json_power_data['designs']:
                    print(f"Warning: {design_name} not found in {self.json_power_file}.")
                    continue
                
                for variant in flow_variants:

                    if variant not in self.json_power_data['designs'][design_name]['flow_variants']:
                        print(f"Warning: {variant} not found for {design_name}.")
                        continue

                    variant_data = self.json_power_data['designs'][design_name]['flow_variants'][variant]

                    seq_power = variant_data['sequential']['total'] * 1e3
                    comb_power = variant_data['combinational']['total'] * 1e3
                    clock_total = variant_data['clock']['total'] * 1e3
                    gated_power = variant_data['gated']['total'] * 1e3
                    clock_direct = clock_total - gated_power

                    data.append([seq_power, comb_power, clock_direct, gated_power])
                    safe_variant = variant.replace("_", r"\_")
                    safe_design  = design_name.replace("_", r"\_")
                    index_labels.append(f"$\\bf{{{safe_design}\\;{safe_variant}}}$")
                    print(f"Plotting: {design_name} Variant: {variant}")

            # "Bar Chart with multiple labels"
            # https://stackoverflow.com/questions/43545879/bar-chart-with-multiple-labels/43547282#43547282
            df = pd.DataFrame(data,
                            index=index_labels,
                            columns=pd.Index(['Sequential', 'Combinational', 'Clock (Direct)', 'Clock (Gated)']))

            fig, ax = plt.subplots(figsize=(10, 6))

            x = np.arange(len(df.index))
            width = 0.25

            ax.bar(x - width, df['Sequential'], width, label='Sequential', color='#3498db')
            ax.bar(x, df['Combinational'], width, label='Combinational', color='#2ecc71')
            ax.bar(x + width, df['Clock (Direct)'], width, label='Clock (Direct)', color='#9b59b6')
            ax.bar(x + width, df['Clock (Gated)'], width, bottom=df['Clock (Direct)'], label='Clock (Gated)', color='#e74c3c')

            pos = []
            for i in range(len(df.index)):
                pos.extend([x[i] - width, x[i], x[i] + width])

            lab = ['Sequential', 'Combinational', 'Clock'] * len(df.index)
            ax.xaxis.remove_overlapping_locs = False
            ax.set_xticks(pos, minor=True)
            ax.set_xticklabels(lab, minor=True, fontsize=8)

            ax.set_xticks([])
            for i, label in enumerate(df.index):
                ax.text(x[i], -0.12, label, transform=ax.get_xaxis_transform(),
                    ha='center', fontsize=12)

            ax.set_ylabel('Power (mW)', fontsize=12)
            ax.set_title('Power Breakdown Comparison', fontsize=14)
            ax.legend()
            ax.grid(axis='y', alpha=0.3)

            plt.tight_layout()
            output_path = f"{self.plot_dir}/power_breakdown_comparison.png"
            plt.subplots_adjust(bottom=0.15)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"Comparison plot saved to: {output_path}")

    def plot_single_power_breakdown(self, power_data, plot_dir):
        """
        Creates a bar chart showing power breakdown with clock power stacked
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Convert to mW
        seq_power = power_data['seq_total'] * 1e3
        comb_power = power_data['comb_total'] * 1e3
        clock_direct = (power_data['clock_total'] - power_data['gated_total']) * 1e3
        clock_gated = power_data['gated_total'] * 1e3
        
        categories = ['Sequential', 'Combinational', 'Clock Network']
        x_pos = [0, 1, 2]
        
        # Sequential bar
        ax.bar(x_pos[0], seq_power, label='Sequential', color='#3498db', width=0.6)
        
        # Combinational bar
        ax.bar(x_pos[1], comb_power, label='Combinational', color='#2ecc71', width=0.6)
        
        # Clock bar (direct + gated)
        ax.bar(x_pos[2], clock_direct, label='Clock (Direct)', color='#9b59b6', width=0.6)
        ax.bar(x_pos[2], clock_gated, bottom=clock_direct, label='Clock (Gated)', color='#e74c3c', width=0.6)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(categories)
        ax.set_ylabel('Power (mW)', fontsize=12)
        ax.set_title(f'Power Breakdown: {self.design_nickname} (variant: {self.flow_variant})', fontsize=14)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(axis='y', alpha=0.3)
        
        ax.text(x_pos[0], seq_power + seq_power*0.02, f'{seq_power:.2f}', ha='center', fontsize=9)
        ax.text(x_pos[1], comb_power + comb_power*0.02, f'{comb_power:.2f}', ha='center', fontsize=9)
        ax.text(x_pos[2], clock_direct + clock_gated + (clock_direct + clock_gated)*0.02, 
                f'{clock_direct + clock_gated:.2f}', ha='center', fontsize=9)
        
        plt.tight_layout()
        output_path = f"{plot_dir}/power_breakdown_{self.design_nickname}_{self.flow_variant}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Power breakdown plot saved to: {output_path}")

def plot_power(env):
    plotter = PlotPower(design=None, env=env)
    plotter.plot_all_power_breakdown(env.designs_to_plot)
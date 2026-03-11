import os
import json

class Environment():
    def __init__(self):
        self.results_dir         = str(os.environ.get('RESULTS_DIR'))
        self.flow_home           = str(os.environ.get('FLOW_HOME'))
        self.design_name         = str(os.environ.get('DESIGN_NAME', 'gcd'))
        self.design_nickname     = str(os.environ.get('DESIGN_NICKNAME', 'gcd'))
        self.flow_variant        = str(os.environ.get('FLOW_VARIANT', 'base'))
        self.platform            = str(os.environ.get('PLATFORM'))
        self.two_phase_recircmux = int(os.environ.get("TWO_PHASE_RECIRCMUX", 0))
        self.two_phase_clkgate   = int(os.environ.get("TWO_PHASE_CLKGATE", 0))
        self.two_phase_clk       = self.two_phase_clkgate or self.two_phase_recircmux
        self.spef_file           = f"{self.results_dir}/6_final.spef"
        self.sdc_file            = f"{self.results_dir}/6_final.sdc"
        self.tech_json_file      = f"{self.flow_home}/twocolor/tech.json"

        self._set_odb_file_path()
        self._load_lef_lib_files()
        self._load_json_params()


    def _set_odb_file_path(self):
        if self.results_dir:
            if not os.path.isabs(self.results_dir):
                self.results_dir = os.path.abspath(self.results_dir)
            self.odb_file = f"{self.results_dir}/6_final.odb"
            print(f"Using RESULTS_DIR path: {self.odb_file}")
        else:
            raise ValueError("Cannot determine ODB file path")

        if not os.path.isfile(self.odb_file):
            raise FileNotFoundError(f"ODB file not found: {self.odb_file}")

    def _load_lef_lib_files(self):
        self.tech_lef       = _get_paths('TECH_LEF')
        self.sc_lef         = _get_paths('SC_LEF')
        self.additional_lef = _get_paths('ADDITIONAL_LEF')
        self.lib_files      = _get_paths('LIB_FILES')
        self.additional_lib = _get_paths('ADDITIONAL_LIB')

    def _load_json_params(self):
        with open(self.tech_json_file, 'r') as tech_json:
            json_data = json.load(tech_json)

        self.save_plot          = bool(json_data['graph_options']['save_plot'])
        self.output_format      = str(json_data['graph_options']['output_format'])
        self.graph_name         = str(json_data['graph_options']['graph_name'])
        self.seq_clock_pin_name = str(json_data['platforms'][self.platform]['latch_pin_name'])
        self.run_test_suite     = bool(json_data["run_test_suite"])
        self.run_latchgraph     = bool(json_data['latchgraph'])
        self.do_power_analysis  = bool(json_data['power_analysis']['do_power_analysis'])
        self.designs_to_plot    = dict(json_data['power_analysis']['designs_to_plot'])
    
    @property
    def all_lef_files(self) -> list[str]:
        return self.tech_lef + self.sc_lef + self.additional_lef
    
    @property
    def all_lib_files(self) -> list[str]:
        return self.lib_files + self.additional_lib


def _get_paths(env_var: str) -> list[str]:
    value = os.environ.get(env_var, '')
    return [p for p in value.split() if p and p != 'None']
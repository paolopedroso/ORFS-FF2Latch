export DESIGN_NAME = gcd
export PLATFORM    = sky130hd

export VERILOG_FILES = $(DESIGN_HOME)/src/$(DESIGN_NICKNAME)/gcd.v
export SDC_FILE      = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/two_phase_clk_constraint.sdc
# export SDC_FILE      = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/default_constraint.sdc

# export TWO_PHASE_RECIRCMUX = 1
export ABC_RETIME_FOR_TWO_PHASE = 1
export TWO_PHASE_CLKGATE = 1

# Adders degrade GCD
export ADDER_MAP_FILE :=

export CORE_UTILIZATION = 40
export TNS_END_PERCENT = 100
export EQUIVALENCE_CHECK   ?=   0
export REMOVE_CELLS_FOR_EQY = sky130_fd_sc_hd__tapvpwrvgnd*

# This allows Yosys to print more details to the terminal during execution
export YOSYS_FLAGS

# source platforms/sky130hd/specify_files_for_sdc.tcl
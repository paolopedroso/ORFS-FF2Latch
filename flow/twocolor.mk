# taken from flow/Makefile
ifeq ($(origin FLOW_HOME), undefined)
  FLOW_HOME := $(abspath $(dir $(firstword $(MAKEFILE_LIST))))
endif
export FLOW_HOME

export TC_DIR_PATH:=$(FLOW_HOME)/twocolor

TC_SCRIPTS:=$(wildcard $(TC_DIR_PATH)/*.py)

export TC_PY_LIBS := matplotlib networkx

TC_PY_LIBS_DIR := $(addprefix $(TC_DIR_PATH)/pylibs/, $(TC_PY_LIBS))

$(TC_PY_LIBS_DIR): check_twocolor_dependencies

check_twocolor_dependencies:
	@echo "checking dependencies..."
	@mkdir -p $(TC_DIR_PATH)/pylibs
	@bash twocolor/build_twocolor.sh

# prepend dependencies to the python path
export PYTHONPATH:=$(TC_DIR_PATH)/pylibs:$(PYTHONPATH)

.PHONY: twocolor
twocolor: final $(TC_SCRIPTS) $(TC_PY_LIBS_DIR)
	@source ../env.sh && openroad -python twocolor/main.py

clean_twocolor:
	rm -rf $(wildcard $(TC_DIR_PATH)/plots/*) \
		$(wildcard $(TC_DIR_PATH)/reports/*)
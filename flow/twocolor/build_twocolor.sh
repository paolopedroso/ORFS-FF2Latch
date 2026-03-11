#!/bin/bash

function __check_libraries() {
    local lib="$1"
    
    # check here if lib not installed
    PYTHONPATH="$TC_DIR_PATH/pylibs:$PYTHONPATH" python3 -c "import $lib" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Library $lib is not installed. Installing..."
        pip install "$lib" --target="$TC_DIR_PATH/pylibs" -v
        if [ $? -eq 0 ]; then
            echo "Library $lib installed successfully."
        else
            echo "ERROR: Failed to install $lib"
            return 1
        fi
    else
        echo "Library $lib is already installed."
    fi
}

# check python libraries
for lib in $TC_PY_LIBS; do
    __check_libraries "$lib" || exit 1
done
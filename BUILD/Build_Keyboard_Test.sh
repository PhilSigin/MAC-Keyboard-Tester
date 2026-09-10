#!/bin/bash

# Redirect all output to both terminal and log file
#exec > >(tee Build_v40.log) 2>&1

# Start timer
START_TIME=$(date +%s)

echo "--- Cleaning Previous Build ---"

rm -rf Build 2>/dev/null || echo "Warning: Could not remove Build directory (may be locked)"
#rm -rf "Mac Keyboard Test.app" 2>/dev/null || echo "Warning: Could not remove Executable.app (may be locked)"

# Clean Nuitka cache (important if there are dependencies problems)
# Comment it after successful build
#python -m nuitka --clean-cache=all

echo "--- Build start ---"


export DYLD_LIBRARY_PATH=""
export DYLD_FALLBACK_LIBRARY_PATH=""

python -m nuitka \
    --standalone \
    --macos-create-app-bundle \
    --macos-app-name="Mac Keyboard Test" \
    --macos-signed-app-name="com.mackeyboardtest.app" \
    --macos-app-version="0.1.3" \
    --macos-app-icon="../materials/MacKeyboardTest.icns" \
    --macos-app-mode=gui \
    --enable-plugin=pyside6 \
    --include-package=code \
    --include-data-dir=../materials=materials \
    --output-dir=Build \
    ../main.py \
    --output-filename="MacKeyboardTest" \
    --output-folder-name="Mac Keyboard Test"



# End timer
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "Build Finished!"
echo "Time elapsed: $ELAPSED sec"


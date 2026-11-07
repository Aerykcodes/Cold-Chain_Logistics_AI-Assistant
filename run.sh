#!/bin/bash

export DYLD_LIBRARY_PATH="$(brew --prefix openssl@3)/lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"

source .venv/bin/activate

python "$@"
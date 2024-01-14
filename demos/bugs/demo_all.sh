#!/bin/sh
set -e -u

for venv_dir in venvs/*; do
    source ${venv_dir}/bin/activate
    python demo_texture_bug.py ${venv_dir}
    deactivate
done
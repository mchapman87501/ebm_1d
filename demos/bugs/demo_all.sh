#!/bin/sh
for venv_dir in venv_*; do
    source ${venv_dir}/bin/activate
    python demo_texture_bug.py ${venv_dir}
    deactivate
done
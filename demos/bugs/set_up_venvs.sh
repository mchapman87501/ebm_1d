#!/bin/bash

if [ -d venvs ]; then
    rm -rf venvs
fi
mkdir -p venvs

for req_file in requirements/*.txt; do
    venv_name=$(echo ${req_file} | sed -e 's,requirements/,,' -e 's/\.txt//' -e 's,^,venvs/,')
    python -m venv ${venv_name}
    source ${venv_name}/bin/activate
    python -m pip install -U pip -r ${req_file}
    deactivate
done

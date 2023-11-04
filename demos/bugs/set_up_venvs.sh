#!/bin/bash

mkdir -p venvs

for req_file in *requirements.txt; do
    venv_name=$(echo ${req_file} | sed -e 's/_requirements.txt//' -e 's,^,venvs/,')
    python -m venv ${venv_name}
    source ${venv_name}/bin/activate
    python -m pip install -r ${req_file}
    deactivate
done

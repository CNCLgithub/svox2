#!/bin/bash

. load_config.sh

usage="Syntax: $(basename "$0") [-h|--help] [COMPONENTS...] -- will set up the project environment,
where:
    -h | --help     Print this help
    COMPONENTS...   Specify component to set up

Valid COMPONENTS:
    all: setup all components (container will be pulled, not built; python packages will be installed)
    cont_[pull|build]: pull the singularity container or build it
    python: add python venv and install necessary packages
    data: pull data"


[ $# -eq 0 ] || [[ "${@}" =~ "help" ]] && echo "$usage"

cont_pull_url="https://yale.box.com/shared/static/4pvea8sthhg2b7vaq87p2nsgwumxybwv.sif"
cont_dest="cont.sif"

#################################################################################
# Container setup
#################################################################################

[[ "${@}" =~ "cont_build" ]] || [[ "${@}" =~ "cont_pull" ]] || \
    echo "Not touching container"

[[ "${@}" =~ "cont_pull" ]] && [[ -z "${cont_pull_url}" ]] || \
    [[ "${cont_pull_url}" == " " ]] && \
    echo "Tried to pull but no link provided in \$cont_pull_url"
[[ "${@}" =~ "cont_pull" ]] && [[ -n "${cont_pull_url}" ]] && \
    [[ "${cont_pull_url}" != " " ]] && \
    echo "pulling container" && \
    wget "$cont_pull_url" -O "${cont_dest}"

[[ "${@}" =~ "cont_build" ]] && echo "building ${BUILD} -> ${cont_dest}" && \
    # SINGULARITY_TMPDIR="${SPATHS[tmp]}" sudo -E $SING build \
    # "$cont_dest" "$BUILD"
    echo "Build container not yet implemented"


#################################################################################
# Python setup
#################################################################################
[[ "${@}" =~ "python" ]] || echo "Not touching python"

[[ "${@}" =~ "all" ]] || [[ "${@}" =~ "python" ]] && \
    echo "building python env at ${ENV[env]}" && \
    singularity exec "${ENV[cont]}" bash -c "virtualenv ${ENV[env]}" && \
    source ${ENV[env]}/bin/activate && \
    ./run.sh "python -m pip install --upgrade pip" && \
    ./run.sh "python -m pip install -r requirements.txt" && \
    # pip install . is how plenoxels builds its library and cuda kernel
    ./run.sh "pip install ." && \
    # If the svox2 folder isn't removed, python will look for the cuda kernel in the wrong place.
    # It could also be renamed, but it isn't needed for anything after installation ('pip install .')
    rm -r svox2

#################################################################################
# Project data
# (ie datasets and checkpoints)
#################################################################################
[[ "${@}" =~ "datasets" ]] || [[ "${@}" =~ "datasets" ]] || \
    echo "Not touching datasets"
[[ "${@}" =~ "all" ]] || [[ "${@}" =~ "datasets" ]] && echo "datasets not yet gettable"

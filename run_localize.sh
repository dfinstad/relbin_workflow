#!/bin/bash

# Note: this needs to be run in a python 3.6 enironment with
# the ligo-skymap package installed. LAL_DATA_PATH environment
# variable must also be set to a valid lalsuite-extra location

ANALYSIS_DIR=${1}
OUTDIR=${ANALYSIS_DIR}/sky_localization/skymap_files
CWD=${PWD}

# IMPORTANT: HIGHLY RECOMMENDED IF USING A SHARED WORKSTATION.
# Explicitly set the number of OpenMP threads
# instead of using all available cores.
export OMP_NUM_THREADS=4

mkdir -p ${OUTDIR}
cd ${OUTDIR}
for FILE in ../ligolw_files/*.xml; do
    # Run BAYESTAR
    bayestar-localize-coincs ${FILE} --f-low 25
    # rename output file from 0.fits
    INJID=${FILE#../ligolw_files/ligolw_injection_}
    INJID=${INJID%.xml}
    OUTFILE=skymap_${INJID}.fits
    mv 0.fits ${OUTFILE}
done
cd ${CWD}

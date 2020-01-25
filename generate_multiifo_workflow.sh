#!/bin/bash
# github user for config files
GITHUB_USER="gwastro"
# generate test workflow
TEST_WORKFLOW="yes"
# locations of analysis directory and results directory
PYCBC_TAG='master'
DATA_TYPE='GAUSSIAN_NOISE'
UNIQUE_ID=`uuidgen`
RUN_TAG="multiifo_noinj_testbank"
WORKFLOW_NAME=
WORKFLOW_DIR=output_test_6_hours
BASE_DIR=/home/daniel.finstad/projects/relbin_pe_paper/offline_search/test/inj_minimal_base_2ogc
PROJECT_PATH=${BASE_DIR}/analysis/analysis-${RUN_TAG}-${UNIQUE_ID}
WEB_PATH=/home/daniel.finstad/secure_html/relative_binning/offline_search/inj_minimal_base_2ogc/results/analysis-${RUN_TAG}-${UNIQUE_ID}

set -e
WORKFLOW_NAME=o1-analysis-${RUN_TAG}-${PYCBC_TAG}-${DATA_TYPE}
OUTPUT_PATH=${WEB_PATH}/${WORKFLOW_NAME}
WORKFLOW_TITLE="'O1 Analysis test ${DATA_TYPE}'"
WORKFLOW_SUBTITLE="'PyCBC ${PYCBC_TAG} Open GW Analysis'"

if [ -d ${PROJECT_PATH}/$WORKFLOW_NAME ] ; then
  echo "Error: ${PROJECT_PATH}/$WORKFLOW_NAME already exists."
  exit 1
fi
mkdir -p ${PROJECT_PATH}/$WORKFLOW_NAME
pushd ${PROJECT_PATH}/$WORKFLOW_NAME

if [ "x${TEST_WORKFLOW}" == "xyes" ] ; then
  CONFIG_OVERRIDES="workflow:start-time:1128466607 workflow:end-time:1128486607 workflow-tmpltbank:tmpltbank-pregenerated-bank:https://github.com/${GITHUB_USER}/1-ogc/raw/master/workflow/auxiliary_files/H1L1-WORKFLOW_TEST_BANK-1163174417-604800.xml.gz workflow-splittable-full_data:splittable-num-banks:2"
else
  CONFIG_OVERRIDES="workflow-splittable-full_data:splittable-num-banks:30"
fi


pycbc_create_offline_search_workflow \
  --workflow-name ${WORKFLOW_NAME} --output-dir output \
  --config-files \
  https://github.com/${GITHUB_USER}/pycbc-config/raw/v1.13.1/O3exp/pipeline/analysis.ini \
  https://github.com/${GITHUB_USER}/1-ogc/raw/master/workflow/configuration/losc_data.ini \
  https://github.com/${GITHUB_USER}/pycbc-config/raw/v1.13.1/O3exp/pipeline/executables.ini \
  https://github.com/${GITHUB_USER}/pycbc-config/raw/v1.13.1/O3exp/pipeline/plotting.ini \
  https://github.com/${GITHUB_USER}/1-ogc/raw/master/workflow/configuration/gps_times_O1_analysis_test.ini \
  --config-overrides ${CONFIG_OVERRIDES} \
  "results_page:output-path:${OUTPUT_PATH}" \
  "results_page:analysis-title:${WORKFLOW_TITLE}" \
  "multiifo_coinc:statistic-files:${BASE_DIR}/statHL.hdf" \
  "optimal_snr:cores:8" \
  "workflow:h1-channel-name:H1_FAKE_STRAIN" \
  "workflow:l1-channel-name:L1_FAKE_STRAIN" \
  "workflow:v1-channel-name:V1_FAKE_STRAIN" \
  "workflow-datafind:datafind-v1-frame-type:DUMMY" \
  "workflow-datafind:datafind-method:FROM_PREGENERATED_LCF_FILES" \
  "workflow-datafind:datafind-pregenerated-cache-file-h1:${BASE_DIR}/frame_data/H1_cache_6_hours.lcf" \
  "workflow-datafind:datafind-pregenerated-cache-file-l1:${BASE_DIR}/frame_data/L1_cache_6_hours.lcf" \
  "workflow-datafind:datafind-pregenerated-cache-file-v1:${BASE_DIR}/frame_data/V1_cache_6_hours.lcf" \
  "workflow-segments:segments-veto-definer-url:https://github.com/${GITHUB_USER}/1-ogc/raw/master/workflow/auxiliary_files/H1L1-DUMMY_O1_CBC_VDEF-1126051217-1220400.xml" \
  "workflow-segments:segments-science:DATA:CBC_CAT1_VETO" \
  "executables:segment_query:/home/daniel.finstad/opt/pycbc-rel-1.13.1/bin/pycbc_losc_segment_query"
  #"workflow-segments:segments-vetoes:CBC_CAT2_VETO,CBC_HW_INJ,BURST_HW_INJ"
  #https://github.com/${GITHUB_USER}/pycbc-config/raw/v1.13.1/O3exp/pipeline/analysis.ini \

pushd output
pycbc_submit_dax \
      --dax ${WORKFLOW_NAME}.dax \
      --no-create-proxy \
      --force-no-accounting-group \
      --append-pegasus-property 'pegasus.integrity.checking=none'
popd
popd
echo
echo "Results will be availale in ${OUTPUT_PATH}"
echo

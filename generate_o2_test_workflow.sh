#!/bin/bash

# the analysis block number
# analysis 0 is ER8A data which is not analyzed
# analysis 1 is ER8B data and O1 data which contains GW150914
# O1 analysis starts with block number 1
n=""

# data type is either LOSC_4_V1 or LOSC_16_V1
DATA_TYPE="O2_data"

# version of pycbc to use
PYCBC_TAG="dev"

# github user for config files
GITHUB_USER="gwastro"

# do not submit the workflow
NO_PLAN=""

# do not submit the workflow
NO_SUBMIT=""

# platform for submission
PLATFORM="vanilla"

# generate test on O2 data
O2_TEST="yes"

#GETOPT_CMD=`getopt -o a:d:p:g:P:thnN --long o2-test,analysis-segment:,data-type:,pycbc-tag:,github-user:,platform:,test-workflow,help,no-submit,no-plan -n 'generate_workflow.sh' -- "$@"`
#eval set -- "$GETOPT_CMD"
#
#while true ; do
#  case "$1" in
#    -a|--analysis-segment)
#      case "$2" in
#        "") shift 2 ;;
#        *) n=$2 ; shift 2 ;;
#      esac ;;
#    -d|--data-type)
#      case "$2" in
#        "") shift 2 ;;
#        *) DATA_TYPE=$2 ; shift 2 ;;
#      esac ;;
#    -p|--pycbc-tag)
#      case "$2" in
#        "") shift 2 ;;
#        *) PYCBC_TAG=$2 ; shift 2 ;;
#      esac ;;
#    -p|--github-user)
#      case "$2" in
#        "") shift 2 ;;
#        *) GITHUB_USER=$2 ; shift 2 ;;
#      esac ;;
#    -P|--platform)
#      case "$2" in
#        "") shift 2 ;;
#        *) PLATFORM=$2 ; shift 2 ;;
#      esac ;;
#    -t|--test-workflow) TEST_WORKFLOW='yes' ; shift ;;
#    -T|--o2-test) O2_TEST='yes' ; shift ;;
#    -n|--no-submit) NO_SUBMIT='--no-submit' ; shift ;;
#    -N|--no-plan) NO_PLAN='yes' ; shift ;;
#    -h|--help)
#      echo "usage: ${0} [-h] [-n] (-a N|-t) [-d DATA_TYPE] [-p PYCBC_TAG] -g GITHUB_TOKEN"
#      echo
#      echo "either one of the follow two arguments must be given:"
#      echo "  -a, --analysis-segment  analysis segment number to run [1-9]"
#      echo "  -t, --test-workflow     generate a small test workflow"
#      echo
#      echo "optional arguments:"
#      echo "  -d, --data-type         type of data to analyze [LOSC_16_V1]"
#      echo "  -p, --pycbc-tag         valid tag of PyCBC to use [v1.13.0]"
#      echo "  -g, --github-user       use 1-ocg repository from user [gwastro]"
#      echo "  -P, --platform          setup workflow to run on one of the following"
#      echo "                            platforms [osgconnect|orangegrid|vanilla]"
#      echo "                            default is osgconnect."
#      echo "  -h, --help              show this help message and exit"
#      echo "  -N, --no-plan           exit after generating the workflow"
#      echo "  -n, --no-submit         exit after generating and planning the workflow"
#      echo
#      exit 0 ;;
#    --) shift ; break ;;
#    *) echo "Internal error!" ; exit 1 ;;
#  esac
#done

if [[ "x${TEST_WORKFLOW}" == "xyes" || "x${O2_TEST}" == "xyes" ]]; then
  if [ "x${n}" == "x" ]; then
    n="test"
  else
    echo "Error: cannot give both --analysis-segment and --test-workflow."
    echo "Use --help for options."
    exit 1
  fi
else
  if [ "x${n}" == "x" ]; then
    echo "Error: one of --analysis-segment or --test-workflow must"
    echo "be specified. Use --help for options."
    exit 1
  fi
fi

if [ "${PLATFORM}" != "osgconnect" ] && [ "${PLATFORM}" != "orangegrid" ] && [ "${PLATFORM}" != "vanilla" ] ; then
  echo "Error: --platform must be one of osgconnect, orangegrid, or vanilla."
  echo "       Got ${PLATFORM}"
  exit 1
fi

echo "Generating workflow for analysis ${n} using ${DATA_TYPE} data and PyCBC ${PYCBC_TAG}"
echo "Downloading configuration files from https://github.com/${GITHUB_USER}/1-ogc"
echo "Generating workflow for platform ${PLATFORM}"

# locations of analysis directory and results directory
BASE=/home/daniel.finstad/projects/relbin_pe_paper/full_pipeline/run_workflow
UNIQUE_ID=`uuidgen`
STAT=phasetdnew_newsnr_sgveto
DURATION=21600
CENTER_TIME=1187008882
HALFDUR=$(($DURATION / 2))
RUN_TAG="O2_TEST_6HR_NO_BG_FIT_${STAT}_3det"
PROJECT_PATH=${BASE}/analysis_multiifo_3det/analysis-${n}-${RUN_TAG}-${UNIQUE_ID}
WEB_PATH=${HOME}/secure_html/relative_binning/full_pipeline/offline_search/results/analysis-${n}-${RUN_TAG}-${UNIQUE_ID}

set -e

WORKFLOW_NAME=analysis-${n}-${RUN_TAG}-${PYCBC_TAG}-${DATA_TYPE}
OUTPUT_PATH=${WEB_PATH}/${WORKFLOW_NAME}
WORKFLOW_TITLE="'Relative Binning Workflow Analysis ${n} ${DATA_TYPE}'"
WORKFLOW_SUBTITLE="'PyCBC ${PYCBC_TAG} Open GW Analysis'"

if [ -d ${PROJECT_PATH}/$WORKFLOW_NAME ] ; then
  echo "Error: ${PROJECT_PATH}/$WORKFLOW_NAME already exists."
  exit 1
fi
mkdir -p ${PROJECT_PATH}/$WORKFLOW_NAME
pushd ${PROJECT_PATH}/$WORKFLOW_NAME

export LIGO_DATAFIND_SERVER=sugwg-condor.phy.syr.edu:80

CONFIG_OVERRIDES="workflow:start-time:$(($CENTER_TIME - $HALFDUR)) workflow:end-time:$(($CENTER_TIME + $HALFDUR)) workflow-tmpltbank:tmpltbank-pregenerated-bank:https://github.com/${GITHUB_USER}/pycbc-config/raw/master/O1/bank/H1L1-UBERBANK_MAXM100_NS0p05_ER8HMPSD-1126033217-223200.xml.gz workflow-splittable-full_data:splittable-num-banks:40"


PLATFORM_CONFIG_OVERRIDES=""
EXEC_FILE=""

#  ${BASE}/config_multiifo/analysis_mod_o1_test.ini \
#  ${BASE}/config_multiifo/executables_mod_3det.ini \
#  ${BASE}/config_multiifo/plotting_mod_3det.ini \

#  https://github.com/${GITHUB_USER}/2-ogc/raw/master/search_configs/full/analysis.ini \
#  https://github.com/${GITHUB_USER}/2-ogc/raw/master/search_configs/full/executables.ini \
#  https://github.com/${GITHUB_USER}/2-ogc/raw/master/search_configs/full/plotting.ini \

#  "workflow-segments:segments-veto-definer-url:https://github.com/${GITHUB_USER}/1-ogc/raw/master/workflow/auxiliary_files/H1L1-DUMMY_O1_CBC_VDEF-1126051217-1220400.xml" \

pycbc_create_offline_search_workflow \
--workflow-name ${WORKFLOW_NAME} --output-dir output \
--config-files \
  ${BASE}/config_multiifo/analysis_mod_o1_test.ini \
  ${BASE}/config_multiifo/executables_mod_3det.ini \
  ${BASE}/config_multiifo/plotting_mod_3det.ini \
  https://github.com/${GITHUB_USER}/2-ogc/raw/master/search_configs/times/gps_times_O2_analysis_21.ini \
  https://github.com/${GITHUB_USER}/2-ogc/raw/master/search_configs/full/data_O2.ini \
  ${BASE}/config_multiifo/injections_bns.ini \
--config-overrides ${CONFIG_OVERRIDES} ${PLATFORM_CONFIG_OVERRIDES} \
  "results_page:output-path:${OUTPUT_PATH}" \
  "results_page:analysis-title:${WORKFLOW_TITLE}" \
  "results_page:analysis-subtitle:${WORKFLOW_SUBTITLE}" \
  "workflow-ifos:v1:" \
  "workflow:file-retention-level:all_triggers" \
  "workflow-segments:segments-veto-definer-url:https://github.com/${GITHUB_USER}/1-ogc/raw/master/workflow/auxiliary_files/H1L1-DUMMY_O1_CBC_VDEF-1126051217-1220400.xml" \
  "workflow-datafind:datafind-check-segment-gaps:update_times" \
  "workflow-datafind:datafind-check-frames-exist:raise_error" \
  "optimal_snr:cores:8" \
  "multiifo_coinc:statistic-files:${BASE}/stat_files/statHL.hdf ${BASE}/stat_files/statLV.hdf ${BASE}/stat_files/statHV.hdf ${BASE}/stat_files/statHLV.hdf" \
  "multiifo_coinc:ranking-statistic:${STAT}" \
  "inspiral:snr-threshold:4.5" \
  "inspiral:cluster-window:8" \
  "inspiral:verbose:" \
  "executables:page_ifar_catalog:/home/daniel.finstad/opt/pycbc-dev/bin/pycbc_ifar_catalog" \
  "multiifo_coinc:verbose:" \
  "multiifo_statmap:verbose:" \
  "multiifo_statmap_inj:verbose:" \
  "combine_statmap:verbose:"


if [ "x${NO_PLAN}" == "x" ] ; then
  pushd output

  if [ ${PLATFORM} == "osgconnect" ] ; then
    if [ ! -d /local-scratch/${USER}/workflows ] ; then
      mkdir -p /local-scratch/${USER}/workflows
    fi
    pycbc_submit_dax ${NO_SUBMIT} \
      --dax ${WORKFLOW_NAME}.dax \
      --no-create-proxy \
      --force-no-accounting-group \
      --append-site-profile 'local:env|LAL_DATA_PATH:/cvmfs/oasis.opensciencegrid.org/ligo/sw/pycbc/lalsuite-extra/e02dab8c/share/lalsimulation' \
      --execution-sites osgconnect \
      --local-staging-server 'stash://' \
      --remote-staging-server 'stash://' \
      --append-pegasus-property 'pegasus.integrity.checking=none' \
      --append-pegasus-property 'pegasus.transfer.bypass.input.staging=true' \
      --append-site-profile 'osgconnect:env|LAL_DATA_PATH:/cvmfs/oasis.opensciencegrid.org/ligo/sw/pycbc/lalsuite-extra/e02dab8c/share/lalsimulation' \
      --append-site-profile 'osgconnect:env|LIGO_DATAFIND_SERVER:sugwg-condor.phy.syr.edu:80' \
      --append-site-profile 'osgconnect:condor|requirements:((GLIDEIN_site isnt "IIT") && (GLIDEIN_site isnt "UChicago"))' \
      --append-site-profile "osgconnect:condor|+SingularityImage:\"/cvmfs/singularity.opensciencegrid.org/pycbc/pycbc-el7:${PYCBC_TAG}\"" \
      --local-dir /local-scratch/${USER}/workflows
  elif [ ${PLATFORM} == "orangegrid" ] ; then
    pycbc_submit_dax ${NO_SUBMIT} \
      --dax ${WORKFLOW_NAME}.dax \
      --no-create-proxy \
      --force-no-accounting-group \
      --append-site-profile 'local:env|LAL_DATA_PATH:/cvmfs/oasis.opensciencegrid.org/ligo/sw/pycbc/lalsuite-extra/e02dab8c/share/lalsimulation' \
      --append-site-profile 'local:env|LD_LIBRARY_PATH:/opt/intel/composer_xe_2015.0.090/mkl/lib/intel64:/opt/intel/2015/composer_xe_2015.0.090/mkl/lib/intel64' \
      --execution-sites orangegrid \
      --local-staging-server gsiftp://`hostname -f` \
      --remote-staging-server gsiftp://`hostname -f` \
      --append-pegasus-property 'pegasus.transfer.bypass.input.staging=true' \
      --append-pegasus-property 'pegasus.integrity.checking=none' \
      --append-site-profile 'orangegrid:condor|requirements:(TARGET.vm_name is "ITS-C6-OSG-20160824") || (TARGET.vm_name is "its-u18-nfs-20181019")' \
      --append-site-profile 'orangegrid:condor|+vm_name:"its-u18-nfs-20181019"' \
      --append-site-profile 'orangegrid:env|LAL_DATA_PATH:/cvmfs/oasis.opensciencegrid.org/ligo/sw/pycbc/lalsuite-extra/e02dab8c/share/lalsimulation'
  else
    pycbc_submit_dax ${NO_SUBMIT} \
      --dax ${WORKFLOW_NAME}.dax \
      --no-create-proxy \
      --force-no-accounting-group \
      --append-pegasus-property 'pegasus.integrity.checking=none' \
      --append-site-profile 'local:env|LAL_DATA_PATH:/cvmfs/oasis.opensciencegrid.org/ligo/sw/pycbc/lalsuite-extra/e02dab8c/share/lalsimulation' \
      --append-site-profile 'local:env|LD_LIBRARY_PATH:/opt/intel/composer_xe_2015.0.090/mkl/lib/intel64:/opt/intel/2015/composer_xe_2015.0.090/mkl/lib/intel64'
  fi
  popd
fi

popd

echo
echo "Workflow created in ${PROJECT_PATH}/${WORKFLOW_NAME}"
echo "Results will be availale in ${OUTPUT_PATH}"
echo

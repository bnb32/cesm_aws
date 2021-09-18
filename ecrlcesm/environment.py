import os

USERNAME="ec2-user"
NETID="bnb32"
PROJECT_CODE="UCOR0044"
ROOT_DIR="/data"
SCRATCH_DIR=ROOT_DIR+"/"+NETID+"/scratch"
RUN_DIR="%s/cesm" %(ROOT_DIR)
BASE_DIR="/home/%s/environment" %(USERNAME)
CESM_DIR=ROOT_DIR+"/"+NETID+"/my_cesm"
INPUT_DATA_DIR=RUN_DIR+"/inputdata"
MAIN_DIR=BASE_DIR+"/cesm_aws"
POST_PROC_DIR=MAIN_DIR+"/postprocessing"
PRE_PROC_DIR=MAIN_DIR+"/preprocessing"
CIME_OUT_DIR=SCRATCH_DIR+"/archive"
CESM_SCRIPTS=CESM_DIR+"/cime/scripts"
CESM_CAM_OUT_DIR=SCRATCH_DIR+"/archive/%s/atm/hist"

os.environ["PATH"]+=":%s"%env.CESM_SCRIPTS


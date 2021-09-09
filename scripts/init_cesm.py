import os,sys
sys.path.append("../")
sys.path.append("./")
import environment as env
import argparse

parser=argparse.ArgumentParser(description="Initialize CESM")
parser.add_argument('-only_config_copy',default=False,action='store_true')
args=parser.parse_args()

cmd="git clone https://github.com/escomp/cesm.git %s" %(env.CESM_DIR)
cmd+="; cd %s" %(env.CESM_DIR)
cmd+="; git checkout release-cesm2.1.1"
cmd+="; svn ls https://svn-ccsm-models.cgd.ucar.edu/ww3/release_tags"
cmd+="; ./manage_externals/checkout_externals"

if not args.only_config_copy:
    os.system(cmd)

cmd=" cp %s/SrcMods/*xml %s/cime/config/cesm/machines/" %(env.MAIN_DIR,env.CESM_DIR)
cmd+="; mkdir -p %s/inputdata" %(env.RUN_DIR)

os.system(cmd)

with open("%s/SrcMods/config_machines.xml" %(env.MAIN_DIR), 'r') as f:
    CONFIG_MACHINES = f.read()

with open("%s/cime/config/cesm/machines/config_machines.xml" %(env.CESM_DIR), 'w') as f:
    f.write(CONFIG_MACHINES.replace('%RUN_DIR%',env.RUN_DIR).replace('%SCRATCH_DIR%',env.SCRATCH_DIR).replace('%INPUT_DATA_DIR%',env.INPUT_DATA_DIR))
    f.close()


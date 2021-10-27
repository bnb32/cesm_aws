import ecrlgcm.environment
from ecrlgcm.misc import get_logger

import os
import argparse

logger = get_logger()

parser=argparse.ArgumentParser(description="Initialize CESM")
parser.add_argument('-download',default=False,action='store_true')
args=parser.parse_args()

cmd=f"rm -rf {os.environ['CESM_DIR']}; "
cmd+="svn ls https://svn-ccsm-models.cgd.ucar.edu/ww3/release_tags; "
cmd+=f"git clone git@github.com:ESCOMP/cesm.git {os.environ['CESM_DIR']}; "
cmd+=f"cd {os.environ['CESM_DIR']}; "
cmd+="git checkout release-cesm2.2.0; "
cmd+="./manage_externals/checkout_externals; "

if args.download: os.system(cmd)

cmd=f" cp {os.environ['CESM_REPO_DIR']}/SrcMods/config_machines.xml {os.environ['CESM_DIR']}/cime/config/cesm/machines/; "
cmd+=f" cp {os.environ['CESM_REPO_DIR']}/SrcMods/config_compilers.xml {os.environ['CESM_DIR']}/cime/config/cesm/machines/; "
cmd+=f" cp {os.environ['CESM_REPO_DIR']}/SrcMods/config_grids.xml {os.environ['CESM_DIR']}/cime/config/cesm/; "
cmd+=f"mkdir -p {os.environ['CESM_INPUT_DATA_DIR']}; "

os.system(cmd)
logger.info("Copied modified xml files")

with open(f"{os.environ['CESM_REPO_DIR']}/SrcMods/config_machines.xml", 'r') as f:
    CONFIG_MACHINES = f.read()

with open(f"{os.environ['CESM_DIR']}/cime/config/cesm/machines/config_machines.xml", 'w') as f:
    f.write(CONFIG_MACHINES.replace('%RUN_DIR%',os.environ['RUN_DIR']).replace('%SCRATCH_DIR%',os.environ['SCRATCH_DIR']).replace('%INPUT_DATA_DIR%',os.environ['CESM_INPUT_DATA_DIR']))
    f.close()
logger.info("Edited config_machines.xml")


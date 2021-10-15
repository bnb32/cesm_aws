import ecrlgcm.environment
from ecrlgcm.misc import get_logger,land_year_range,min_land_year,max_land_year
from ecrlgcm.preprocessing import interpolate_co2, modify_topofile, modify_co2file
from ecrlgcm.experiment import Experiment

import os
import argparse
import datetime

logger = get_logger()

experiment_dictionary = {
        #'cam':{'compset':'2000_CAM60_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'T42_T42','custom':True},
        'cam':{'compset':'1850_CAM60_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'f19_g17','custom':True},
        #'cam':{'compset':'B1850','res':'f19_g17','custom':False},
        'scam':{'compset':'2000_CAM60%SCAM_CLM50%SP_CICE%PRES_DOCN%DOM_SROF_SGLC_SWAV','res':'T42_T42','custom':True},
        'aqua':{'compset':'2000_CAM60_SLND_SICE_DOCN%SOMAQP_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':True},
        'baro':{'compset':'2000_CAM%DABIP04_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':True},
        'moist_hs':{'compset':'1850_CAM%TJ16_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':True},
        'dry_hs':{'compset':'1850_CAM%HS94_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':False},
        }

parser=argparse.ArgumentParser(description="Run CESM")
parser.add_argument('-exp_type',default='cam',
                    choices=[e for e in experiment_dictionary])
parser.add_argument('-multiplier',default=1.0,type=float,help="CO2 Multiplier")
parser.add_argument('-co2',default=None, help="CO2 Value")
parser.add_argument('-land_year',default=0,type=land_year_range,
                    metavar=f'[{min_land_year}-{max_land_year}]',
                    help="Years prior to current era in units of Ma")
parser.add_argument('-case',default='test',type=str)
parser.add_argument('-ntasks',default=96,type=int)
parser.add_argument('-nthrds',default=8,type=int)
parser.add_argument('-start_date',default="0001-01-01")
parser.add_argument('-step_type',default='ndays')
parser.add_argument('-nsteps',default=10,type=int)
parser.add_argument('-data_dir',default=os.environ['CESM_INPUT_DATA_DIR'])
parser.add_argument('-cime_out_dir',default=os.environ['CIME_OUT_DIR'])
parser.add_argument('-setup',default=False,action='store_true')
parser.add_argument('-build',default=False,action='store_true')
parser.add_argument('-run',default=False,action='store_true')
parser.add_argument('-run_all',default=False,action='store_true')
args=parser.parse_args()

cwd=os.getcwd()

cesmexp = Experiment(type='cesm',multiplier=args.multiplier,land_year=args.land_year)

args.case = f'{os.environ["CESM_REPO_DIR"]}/cases/{cesmexp.name}'

if args.exp_type not in experiment_dictionary:
    logger.error("Select valid case")
    exit()
else:
    args.res = experiment_dictionary[args.exp_type]['res']
    args.compset = experiment_dictionary[args.exp_type]['compset']
    args.custom = experiment_dictionary[args.exp_type]['custom']

if args.res.split('_')[0][0:3]=='T42':
    os.environ['ORIG_TOPO_FILE']=os.environ['T42_TOPO_FILE']
if args.res.split('_')[0][0:3]=='f19':
    os.environ['ORIG_TOPO_FILE']=os.environ['f19_TOPO_FILE']
if args.res.split('_')[0][0:3]=='f09':
    os.environ['ORIG_TOPO_FILE']=os.environ['f09_TOPO_FILE']

os.system(f'mkdir -p {os.environ["CESM_TOPO_DIR"]}')
os.system(f'mkdir -p {os.environ["CESM_CO2_DIR"]}')
topo_file = f"{os.environ['CESM_TOPO_DIR']}/{cesmexp.land_file}"
co2_file = f"{os.environ['CESM_CO2_DIR']}/{cesmexp.co2_file}"

modify_topofile(args.land_year,os.environ['ORIG_TOPO_FILE'],topo_file)
#modify_co2file(args.land_year,args.multiplier,os.environ['ORIG_CESM_CO2_FILE'],co2_file)

if args.co2_value is None:
    args.co2_value = args.multiplier*interpolate_co2(args.land_year)

def edit_namelists():
        
    os.chdir(cwd)
    nl_cam_file=f"{args.case}/user_nl_cam"
    nl_cpl_file=f"{args.case}/user_nl_cpl"
                    
    contents=[]
    contents.append('\n')

    if args.step_type=='ndays':
        contents.append('nhtfrq=-24\n')
        contents.append('mfilt=365\n')
    else:
        contents.append('nhtfrq=0\n')
        contents.append('mfilt=12\n')
    
    contents.append('state_debug_checks=.true.\n')
    contents.append('use_topo_file=.true.\n')
    contents.append(f'bnd_topo="{topo_file}"\n')
    #contents.append(f'eul_divdampn=1.0\n') 
    #contents.append(f"flbc_type='FIXED'\n")
    #contents.append(f"ramp_co2_annual_rate = 0.0\n")
    #contents.append(f"ramp_co2_start_ymd = 0\n")
    #contents.append(f'flbc_file="{co2_file}"\n')
    #contents.append(f"scenario_ghg='FIXED'\n")
    #contents.append('fv_nspltvrm=4\n')
    #contents.append('fv_nspltrac=8\n')
    #contents.append('fv_nsplit=8\n')

    contents.append(f"co2vmr={args.co2_value}e-6\n")
    #contents.append(f"co2vmr_rad={args.co2_value}e-6\n")

    logger.info(f"**Changing namelist file: {nl_cam_file}**")
    with open(nl_cam_file,'w') as f:
        for l in contents: f.write(l)
    f.close()
    
    #with open(nl_cpl_file,'w') as f:
        #f.write('orb_mode="fixed_year"\n')
        #f.write(f'orb_iyear={(args.start_date).split("-")[0]}\n')
        #f.write(f'orb_iyear_align={(args.start_date).split("-")[0]}\n')
        #f.close()    
    #    pass

create_case_cmd=f'create_newcase --case {args.case} --res {args.res} --mach aws_c5 --compset {args.compset} --handle-preexisting-dirs r --output-root {args.cime_out_dir}'

if args.custom: create_case_cmd+=' --run-unsupported'

change_xml_cmd=''
#change_xml_cmd+=f'; ./xmlchange RUN_STARTDATE={args.start_date}'
change_xml_cmd+=f'./xmlchange NTASKS={args.ntasks}'
change_xml_cmd+=f'; ./xmlchange STOP_OPTION={args.step_type}'
change_xml_cmd+=f'; ./xmlchange STOP_N={args.nsteps}'
change_xml_cmd+=f'; ./xmlchange CCSM_CO2_PPMV={args.co2_value}'

if args.setup or args.run_all or not os.path.exists(args.case):
    os.system(f'rm -rf {args.case}')
    os.system(f'rm -rf {os.environ["CIME_OUT_DIR"]}/{cesmexp.name}')

    os.system(create_case_cmd)
    edit_namelists()
    os.chdir(args.case)
    os.system(change_xml_cmd)
    os.system('./case.setup --reset')
    os.system('./preview_run')

if args.build or args.run_all:

    os.chdir(args.case)
    os.system('./case.build')

if args.run or args.run_all:
    try:
        os.chdir(args.case)
        os.system('./case.submit')
    except:
        logger.error("Error submitting case")
        exit()


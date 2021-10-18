import ecrlgcm.environment
from ecrlgcm.misc import get_logger,land_year_range,min_land_year,max_land_year,get_base_topofile
from ecrlgcm.preprocessing import eccentricity, obliquity, solar_constant, interpolate_co2, modify_solarfile, modify_topofile, modify_co2file
from ecrlgcm.experiment import Experiment

import os
import argparse
import xml.etree.ElementTree as ET
from datetime import date

logger = get_logger()

experiment_dictionary = {
        'cam':{'compset':'1850_CAM60_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'f19_g16','custom':True},
        'B1850CN':{'compset':'1850_CAM60_CLM50%CN_SICE_POP2_RTM_SGLC_SWAV','res':'f19_g16','custom':True},
        'B1850SP':{'compset':'1850_CAM60_CLM50%SP_SICE_DOCN%DOM_SROF_SGLC_SWAV','res':'f19_g16','custom':True},
        'aqua':{'compset':'2000_CAM60_SLND_SICE_DOCN%SOMAQP_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':True},
        'baro':{'compset':'2000_CAM%DABIP04_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':True},
        'moist_hs':{'compset':'1850_CAM%TJ16_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':True},
        'dry_hs':{'compset':'1850_CAM%HS94_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':True},
        }

parser=argparse.ArgumentParser(description="Run CESM")
parser.add_argument('-exp_type',default='cam',
                    choices=[e for e in experiment_dictionary])
parser.add_argument('-multiplier',default=1.0,type=float,help="CO2 Multiplier")
parser.add_argument('-co2_value',default=None, help="CO2 Value")
parser.add_argument('-land_year',default=0,type=land_year_range,
                    metavar=f'[{min_land_year}-{max_land_year}]',
                    help="Years prior to current era in units of Ma")
parser.add_argument('-case',default='test',type=str)
parser.add_argument('-ntasks',default=96,type=int)
parser.add_argument('-nthrds',default=8,type=int)
parser.add_argument('-start_date',default="0001-01-01")
parser.add_argument('-step_type',default='ndays')
parser.add_argument('-nsteps',default=10,type=int)
parser.add_argument('-restart',default=False,action='store_true')
parser.add_argument('-setup',default=False,action='store_true')
parser.add_argument('-build',default=False,action='store_true')
parser.add_argument('-run',default=False,action='store_true')
parser.add_argument('-run_all',default=False,action='store_true')
parser.add_argument('-remap',default=False,action='store_true')
args=parser.parse_args()

cwd=os.getcwd()

if args.exp_type not in experiment_dictionary:
    logger.error("Select valid case")
    exit()
else:
    args.res = experiment_dictionary[args.exp_type]['res']
    args.compset = experiment_dictionary[args.exp_type]['compset']
    args.custom = experiment_dictionary[args.exp_type]['custom']

cesmexp = Experiment(gcm_type='cesm',
                     multiplier=args.multiplier,
                     land_year=args.land_year,
                     res=args.res,
                     exp_type=args.exp_type)

args.case = f'{os.environ["CESM_REPO_DIR"]}/cases/{cesmexp.name}'
base_topofile = get_base_topofile(args.res)

topo_file = f"{os.environ['CESM_TOPO_DIR']}/{cesmexp.land_file}"
co2_file = f"{os.environ['CESM_CO2_DIR']}/{cesmexp.co2_file}"
solar_file = f"{os.environ['CESM_SOLAR_DIR']}/{cesmexp.solar_file}"

if args.run_all or args.run:
    if not os.path.exists(topo_file) or args.remap:
        modify_topofile(land_year=args.land_year,
                        infile=base_topofile,
                        outfile=topo_file)
    if not os.path.exists(co2_file) or args.remap:
        modify_co2file(land_year=args.land_year,
                       multiplier=args.multiplier,
                       infile=os.environ['ORIG_CESM_CO2_FILE'],
                       outfile=co2_file)
    if not os.path.exists(solar_file) or args.remap:
        modify_solarfile(land_year=args.land_year,
                         infile=os.environ['ORIG_CESM_SOLAR_FILE'],
                         outfile=solar_file)

if args.co2_value is None:
    args.co2_value = args.multiplier*interpolate_co2(args.land_year)

args.orbit_year = date.today().year-args.land_year*10**6
logger.info(f'Using CO2 Value {args.co2_value} ppm')
logger.info(f'Using orbital year {args.orbit_year} B.P.')

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
    
    #contents.append("cam_chempkg='trop_mam4'\n") 
    #contents.append("cam_physpkg='held_suarez'\n") 
    #contents.append('cld_macmic_num_steps=1\n')
    #contents.append("use_hetfrz_classnuc=.false.\n")
    #contents.append('do_clubb_sgs=.false.\n') 
    #contents.append("deep_scheme='off'\n") 
    #contents.append("eddy_scheme='HB'\n") 
    #contents.append("macrop_scheme='none'\n") 
    #contents.append("microp_scheme='NONE'\n") 
    #contents.append("shallow_scheme='Hack'\n") 
    #contents.append('nucleate_ice_use_troplev=.false.\n')
    #contents.append('use_preexisting_ice=.false.\n')
    contents.append('state_debug_checks=.true.\n')
    contents.append('use_topo_file=.true.\n')
    contents.append(f'bnd_topo="{topo_file}"\n')
    contents.append(f'eul_divdampn=1.0\n') 
    contents.append(f"solar_irrad_data_file='{solar_file}'\n")
    #contents.append(f'solar_const={solar_constant(args.land_year)}\n')
    #contents.append('fv_nspltvrm=4\n')
    #contents.append('fv_nspltrac=8\n')
    #contents.append('fv_nsplit=8\n')
    #contents.append(f"cldfrc2m_do_subgrid_growth=.false.\n")
    
    if args.exp_type in ['moist_hs','dry_hs']:
        contents.append(f"ncdata='{co2_file}'\n")
        contents.append(f"rad_climate='N:CO2:CO2'\n")
    #contents.append(f"mode_defs='mam_mode4:primary_carbon:='\n")
    #contents.append(f"radiation_scheme='rrtmg'\n")
    #contents.append(f"radiation_scheme='rrtmg'\n")
    contents.append(f"co2vmr={args.co2_value}e-6\n")
    contents.append(f"co2vmr_rad={args.co2_value}e-6\n")

    logger.info(f"**Changing namelist file: {nl_cam_file}**")
    with open(nl_cam_file,'w') as f:
        for l in contents: f.write(l)
    f.close()
    
    logger.info(f"**Changing namelist file: {nl_cpl_file}**")
    with open(nl_cpl_file,'w') as f:
        f.write('orb_mode="fixed_year"\n')
        #f.write(f'orb_iyear={args.orbit_year}\n')
        #f.write(f'orb_mvelp={}\n')
        f.write(f'orb_iyear=0\n')
        f.write(f'orb_eccen={eccentricity(args.land_year)}\n')
        f.write(f'orb_obliq={obliquity(args.land_year)}\n')
        #f.write(f'orb_iyear_align={(args.start_date).split("-")[0]}\n')
    f.close()    

create_case_cmd=f'create_newcase --case {args.case} --res {args.res} --mach aws_c5 --compset {args.compset} --handle-preexisting-dirs r --output-root {os.environ["CIME_OUT_DIR"]}'

if args.custom: create_case_cmd+=' --run-unsupported'

change_xml_cmd='./xmlchange '
change_xml_cmd+=f'NTASKS={args.ntasks},'
change_xml_cmd+=f'STOP_OPTION={args.step_type},'
change_xml_cmd+=f'STOP_N={args.nsteps},'
change_xml_cmd+=f'REST_N={args.nsteps//5+1},'
change_xml_cmd+=f'CCSM_CO2_PPMV={args.co2_value}'
#change_xml_cmd+=f'RUN_STARTDATE={args.start_date}'

if args.setup or args.run_all or not os.path.exists(args.case):
    os.system(f'rm -rf {args.case}')
    os.system(f'rm -rf {os.environ["CIME_OUT_DIR"]}/{cesmexp.name}')

    os.system(create_case_cmd)
    logger.info(f"Creating case: {create_case_cmd}")
    edit_namelists()
    os.chdir(args.case)
    os.system(change_xml_cmd)
    logger.info(f"Changing xml files: {change_xml_cmd}")
    os.system('./case.setup --reset')
    os.system('./preview_run')

if args.build or args.run_all:

    os.chdir(args.case)
    os.system('./case.build --skip-provenance-check')

if args.restart:
    os.chdir(args.case)
    cmd='./xmlchange CONTINUE_RUN=TRUE,'
    cmd+=f'STOP_OPTION={args.step_type},'
    cmd+=f'REST_N={args.nsteps//5+1},'
    cmd+=f'STOP_N={args.nsteps}'
    os.system(cmd)
    logger.info(f"Changing xml files: {cmd}")

if args.restart or args.run or args.run_all:
    try:
        os.chdir(args.case)
        os.system('./case.submit')
    except:
        logger.error("Error submitting case")
        exit()


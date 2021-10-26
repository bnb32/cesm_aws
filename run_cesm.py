import ecrlgcm.environment
from ecrlgcm.misc import edit_namelists,get_logger,land_year_range,min_land_year,max_land_year,get_base_topofile
from ecrlgcm.preprocessing import eccentricity, obliquity, solar_constant, interpolate_co2
from ecrlgcm.preprocessing import modify_input_files
from ecrlgcm.experiment import Experiment

import os
import argparse
import xml.etree.ElementTree as ET
import numpy as np
from datetime import date

logger = get_logger()

experiment_dictionary = {
        'cam':{'compset':'F1850_CAM60_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'f19_g16','custom':True},
        'cam_clmCN':{'compset':'F1850_CAM60_CLM50%CN_SICE_SOCN_SROF_SGLC_SWAV','res':'f19_g16','custom':True},
        'cam_clmSP':{'compset':'F1850_CAM60_CLM50%SP_SICE_SOCN_SROF_SGLC_SWAV','res':'f19_g16','custom':True},
        'cam_dlndSCPL':{'compset':'F1850_CAM60_DLND%SCPL_SICE_SOCN_SROF_SGLC_SWAV','res':'f19_g16','custom':True},
        'cam_clmCN_docnDOM':{'compset':'F1850_CAM60_CLM50%CN_SICE_DOCN%DOM_SROF_SGLC_SWAV','res':'f19_g16','custom':True},
        'cam_clmCN_docnSOM':{'compset':'F1850_CAM60_CLM50%CN_SICE_DOCN%SOM_SROF_SGLC_SWAV','res':'f19_g16','custom':True},
        'cam_clmSP_docnDOM':{'compset':'F1850_CAM60_CLM50%SP_SICE_DOCN%DOM_SROF_SGLC_SWAV','res':'f19_g16','custom':True},
        'cam_clmCN_pop':{'compset':'F1850_CAM60_CLM50%CN_SICE_POP2_SROF_SGLC_SWAV','res':'f19_g16','custom':True},
        'cam_clmSP_pop':{'compset':'F1850_CAM60_CLM50%SP_SICE_POP2_SROF_SGLC_SWAV','res':'f19_g16','custom':True},
        'cam_clmSP_docnDOM':{'compset':'F1850_CAM60_CLM50%SP_SICE_DOCN%DOM_SROF_SGLC_SWAV','res':'f19_g17','custom':True},
        'aqua':{'compset':'2000_CAM60_SLND_SICE_DOCN%SOMAQP_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':True},
        'baro':{'compset':'2000_CAM%DABIP04_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':True},
        'moist_hs':{'compset':'1850_CAM%TJ16_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':True},
        'dry_hs':{'compset':'1850_CAM%HS94_SLND_SICE_SOCN_SROF_SGLC_SWAV','res':'T42z30_T42_mg17','custom':True},
        'E1850TEST':{'compset':'E1850TEST','res':'f19_g16','custom':True},
        }

parser=argparse.ArgumentParser(description="Run CESM")
parser.add_argument('-exp_type',default='B1850CN',
                    choices=[e for e in experiment_dictionary])
parser.add_argument('-multiplier',default=1.0,type=float,help="CO2 Multiplier")
parser.add_argument('-co2_value',default=None, help="CO2 Value")
parser.add_argument('-land_year',default=0,type=land_year_range,
                    metavar=f'[{min_land_year}-{max_land_year}]',
                    help="Years prior to current era in units of Ma")
parser.add_argument('-case',default='test',type=str)
parser.add_argument('-ntasks',default=32,type=int)
parser.add_argument('-nthrds',default=8,type=int)
parser.add_argument('-start_date',default="0001-01-01")
parser.add_argument('-step_type',default='ndays')
parser.add_argument('-nsteps',default=3,type=int)
parser.add_argument('-restart',default=False,action='store_true')
parser.add_argument('-setup',default=False,action='store_true')
parser.add_argument('-build',default=False,action='store_true')
parser.add_argument('-run',default=False,action='store_true')
parser.add_argument('-run_all',default=False,action='store_true')
parser.add_argument('-remap',default=False,action='store_true')
parser.add_argument('-remap_hires',default=False,action='store_true')
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

cesmexp.docn_som_file = os.environ['ORIG_DOCN_SOM_FILE']

args.case = f'{os.environ["CESM_REPO_DIR"]}/cases/{cesmexp.name}'

modify_input_files(cesmexp,remap=args.remap,remap_hires=args.remap_hires)

if args.co2_value is None:
    args.co2_value = args.multiplier*interpolate_co2(args.land_year)

args.orbit_year = args.land_year*10**6-date.today().year
logger.info(f'Using CO2 Value {args.co2_value} ppm')
logger.info(f'Using orbital year {args.orbit_year} B.P.')
logger.info(f'Using solar constant {solar_constant(args.land_year)} W/m^2')

sim_config = {}
sim_config['atm'] = [
        f'bnd_topo="{cesmexp.topo_file}"',
        f"solar_irrad_data_file='{cesmexp.solar_file}'",
        f"co2vmr={args.co2_value}e-6",
        f"co2vmr_rad={args.co2_value}e-6",
        ]

if args.step_type=='ndays':
    sim_config['atm'].append('nhtfrq=-24')
    sim_config['atm'].append('mfilt=365')
else:
    sim_config['atm'].append('nhtfrq=0')
    sim_config['atm'].append('mfilt=12')
#f'use_topo_file=.true.'
#f'state_debug_checks=.true.'
#f'eul_divdampn=1.0' 
#f'eul_nsplit=8' 
#f'fv_nsplit=8' 
#f'iradlw=4' 
#f'irad_always=4' 
#f'use_rad_dt_cosz=.true.' 
#f"prescribed_strataero_use_chemtrop=.false."

sim_config['lnd'] = [
        #f"urban_hac='OFF'",
        #f'fsurdat="{cesmexp.landplant_file}"',
        ]
#f"glcmec_downscale_longwave=.false."
#f"melt_non_icesheet_ice_runoff=.false."
#f"use_subgrid_fluxes=.false."

sim_config['ocn'] = [
        #f'overflows_on=.false.',
        #f'overflows_interactive=.false.',
        #f'ltidal_mixing=.false.',
        #f'lhoriz_varying_bckgrnd=.false.',
        #f'region_mask_file="{cesmexp.oceanmask_file}"',
        #f'region_info_file="{os.environ["OCEAN_REGION_MASK_FILE"]}"',
        #f'topography_file="{cesmexp.oceantopo_file}"',
        #f"lat_aux_grid_type='user-specified'",
        #f"lat_aux_begin=-90.0",
        #f"lat_aux_end=90.0",
        #f"n_lat_aux_grid=180",
        #f"n_heat_trans_requested=.true.",
        #f"n_salt_trans_requested=.true.",
        #f"n_transport_reg=1",
        #f"moc_requested=.true.",
        #f"dt_count=30",
        #f'ldiag_velocity=.false.',
        #f'bckgrnd_vdc1=0.524',
        #f'bckgrnd_vdc2=0.313',
        #f"sw_absorption_type='jerlov'",
        #f'jerlov_water_type=3',
        #f"chl_option='file'",
        #f"chl_filename='unknown-chl'",
        #f"chl_file_fmt='bin'",
        #f"init_ts_option='mean'",
        #f"init_ts_file_fmt='bin'",
        #f"init_ts_option='ccsm_startup'",
        #f'init_ts_file="{cesmexp.init_ocean_file}"',
        ]

sim_config['docn'] = [
        #f'domainfile="{cesmexp.oceanfrac_file}"',
        ]

sim_config['ice'] = [
        f"ice_ic='none'",
        f"xndt_dyn=2",
        ]

sim_config['cpl'] = [
        #f'orb_mode="fixed_year"',
        #f'orb_iyear=1850',
        #f'orb_eccen={eccentricity(args.land_year)}',
        #f'orb_obliq={obliquity(args.land_year)}',
        ]

sim_config['xml_changes'] = [
        f'NTASKS={args.ntasks}',
        f'STOP_OPTION={args.step_type}',
        f'STOP_N={args.nsteps}',
        f'REST_N={args.nsteps//5+1}',
        f'--file env_build.xml DEBUG=TRUE',
        f'CCSM_CO2_PPMV={args.co2_value}',
        f"CLM_CO2_TYPE='constant'",
        f'EPS_FRAC=0.1',
        f'ATM_DOMAIN_PATH=""',
        f'ATM_DOMAIN_FILE="{cesmexp.landfrac_file}"',
        #f'LND_DOMAIN_PATH=""',
        #f'LND_DOMAIN_FILE="{cesmexp.landfrac_file}"',
        #f'DOCN_SOM_FILENAME="{cesmexp.docn_som_file}"',
        #f'OCN_DOMAIN_PATH=""',
        #f'OCN_DOMAIN_FILE="{cesmexp.oceanfrac_file}"',
        #f'ICE_DOMAIN_PATH=""',
        #f'ICE_DOMAIN_FILE="{cesmexp.oceanfrac_file}"',
        ]

sim_config['change_xml_cmd'] = ';'.join(f'./xmlchange {l}' for l in sim_config["xml_changes"])

create_case_cmd=f'create_newcase --case {args.case} --res {args.res} --mach aws_c5 --compset {args.compset} --handle-preexisting-dirs r --output-root {os.environ["CIME_OUT_DIR"]}'

if args.custom: create_case_cmd+=' --run-unsupported'

if args.setup or args.run_all or not os.path.exists(args.case):
    os.system(f'rm -rf {args.case}')
    os.system(f'rm -rf {os.environ["CIME_OUT_DIR"]}/{cesmexp.name}')

    os.system(create_case_cmd)
    logger.info(f"Creating case: {create_case_cmd}")
    os.chdir(args.case)
    logger.info(f"Changing namelists")
    edit_namelists(cesmexp,sim_config)
    os.chdir(args.case)
    logger.info(f"Changing xml files: {sim_config['change_xml_cmd']}")
    os.system(sim_config['change_xml_cmd'])
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


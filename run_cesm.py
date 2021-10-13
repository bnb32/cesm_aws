import ecrlcesm.environment as env
import ecrlgcm.environment
from ecrlgcm.misc import land_year_range,min_land_year,max_land_year
from ecrlgcm.preprocessing import interpolate_co2, modify_topofile

import os
import argparse
import datetime

parser=argparse.ArgumentParser(description="Run CESM")
parser.add_argument('-exp_type',default='cam_co2',choices=['aqua','cam','cam_land','cam_co2_fixed','cam_co2_ramp','moist_hs'])
parser.add_argument('-multiplier',default=1.0,help="CO2 Multiplier")
parser.add_argument('-co2',default=None, help="CO2 Value")
parser.add_argument('-land_year',default=0,type=land_year_range,metavar=f'[{min_land_year}-{max_land_year}]',help="Years prior to current era in units of Ma")
parser.add_argument('-case',default='test',type=str)
parser.add_argument('-ntasks',default=32,type=int)
parser.add_argument('-nthrds',default=4,type=int)
parser.add_argument('-start_date',default="1979-01-01")
parser.add_argument('-ndays',default=2,type=int)
parser.add_argument('-data_dir',default=env.INPUT_DATA_DIR)
parser.add_argument('-cime_out_dir',default=env.CIME_OUT_DIR)
parser.add_argument('-setup',default=False,action='store_true')
parser.add_argument('-build',default=False,action='store_true')
parser.add_argument('-run',default=False,action='store_true')
args=parser.parse_args()

#start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
#stop_date=(start_date + datetime.timedelta(days=args.ndays)).strftime("%Y%m%d")

cwd=os.getcwd()

args.case="%s/cases/%s" %(env.MAIN_DIR,args.case)

os.system(f'mkdir -p {env.CESM_TOPO_DIR}')
topo_file = f'{env.CESM_TOPO_DIR}/{args.land_year}Ma_topo.nc'

modify_topofile(args.land_year,env.ORIG_TOPO_FILE,topo_file)

def edit_namelists():
        
    os.chdir(cwd)
    nl_cam_file="%s/user_nl_cam"%(args.case)
    nl_cpl_file="%s/user_nl_cpl"%(args.case)
                    
    contents=[]
    contents.append('\n')
    contents.append('nhtfrq=-24\n')
    contents.append('mfilt=365\n')
    
    contents.append('state_debug_checks=.true.\n')
    contents.append('use_topo_file=.true.\n')
    contents.append(f'bnd_topo="{topo_file}"\n')
    contents.append('fv_nspltvrm=4\n')
    contents.append('fv_nspltrac=8\n')
    contents.append('fv_nsplit=8\n')

    if 'co2' in args.exp_type:
        #contents.append("scenario_ghg='FIXED'\n")
        contents.append(f"co2vmr={args.multiplier*interpolate_co2(args.land_year)}\n")
    #    #contents.append(f'ramp_co2_cap=-{float(args.multiplier)}\n')

    print(f"**Changing namelist file: {nl_cam_file}**")
    with open(nl_cam_file,'w') as f:
        for l in contents: f.write(l)
    f.close()
    
    with open(nl_cpl_file,'w') as f:
        f.write('orb_mode="fixed_year"\n')
        f.write(f'orb_iyear={(args.start_date).split("-")[0]}\n')
        f.write(f'orb_iyear_align={(args.start_date).split("-")[0]}\n')
        f.close()    

if args.exp_type=='aqua':

    args.custom=True
    args.compset="QSC6"
    args.res="f09_f09_mg17"

elif args.exp_type=='cam':

    args.custom=True
    args.compset="2000_CAM60_SLND_SICE_SOCN_SROF_SGLC_SWAV"
    args.res="f19_f19_mg17"

elif args.exp_type=='cam_land':

    args.custom=True
    args.compset="2000_CAM60%SCAM_CLM50%CN_SICE_SOCN_SROF_SGLC_SWAV"
    args.res="f19_f19_mg17"

elif args.exp_type=='cam_co2_ramp':

    args.custom=True
    args.compset="2000_CAM60%RCO2_SLND_SICE_SOCN_SROF_SGLC_SWAV"
    args.res="T42_T42"

elif args.exp_type=='cam_co2_fixed':

    args.custom=True
    args.compset="2000_CAM60_SLND_SICE_SOCN_SROF_SGLC_SWAV"
    args.res="T42_T42"

elif args.exp_type=='moist_hs':
    args.custom=True
    args.compset="FTJ16"
    args.res="T42z30_T42_mg17"

else:
    print("Select valid case")
    exit()

#create_case_cmd='create_newcase --mpilib openmpi --run-unsupported --case %s --res %s --compset %s --project %s --handle-preexisting-dirs r --output-root %s'%(args.case,args.res,args.compset,args.project,args.cime_out_dir)

if args.custom:
    create_case_cmd=f'create_newcase --run-unsupported --case {args.case} --res {args.res} --mach aws_c5 --compset {args.compset} --handle-preexisting-dirs r --output-root {args.cime_out_dir}'
else:
    create_case_cmd=f'create_newcase --case {args.case} --res {args.res} --mach aws_c5 --compset {args.compset} --handle-preexisting-dirs r --output-root {args.cime_out_dir}'

change_xml_cmd=''
change_xml_cmd+=f'./xmlchange NTASKS={args.ntasks}'
change_xml_cmd+=f'; ./xmlchange NTHRDS={args.nthrds}'
change_xml_cmd+=f'; ./xmlchange NINST=8'
#change_xml_cmd+=f'; ./xmlchange ROOTPE=32'
#change_xml_cmd+='; ./xmlchange RUN_STARTDATE=%s' %(args.start_date)
change_xml_cmd+=f'; ./xmlchange STOP_N={args.ndays}'


if 'co2' in args.exp_type:
    change_xml_cmd+=f'; ./xmlchange CCSM_CO2_PPMV={args.multiplier*interpolate_co2(args.land_year)}'
    #change_xml_cmd+=f'; ./xmlchange scenario_ghg="FIXED"'
    #change_xml_cmd+=f'; ./xmlchange ramp_co2_cap=-{float(args.multiplier)}'


if args.setup or not os.path.exists(args.case):
    os.system(f'rm -rf {args.case}')
    case_name = (args.case).split('cases')
    os.system(f'rm -rf {env.SCRATCH_DIR}/cases/{case_name[1]}')

    os.system(create_case_cmd)
    edit_namelists()
    os.chdir(args.case)
    os.system(change_xml_cmd)
    os.system('./case.setup --reset')
    os.system('./preview_run')

if args.build:

    os.chdir(args.case)
    os.system('./case.build')

if args.run:
    try:
        os.chdir(args.case)
        os.system('./case.submit')
    except:
        logger.error("Error submitting case")
        exit()


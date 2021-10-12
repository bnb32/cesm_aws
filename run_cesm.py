import ecrlcesm.environment as env
import ecrlgcm.environment
from ecrlgcm.misc import land_year_range,min_land_year,max_land_year
from ecrlgcm.preprocessing import interpolate_co2

import os
import argparse
import datetime

parser=argparse.ArgumentParser(description="Run CESM")
parser.add_argument('-exp_type',default='aqua',choices=['aqua','cam','cam_land','cam_co2','moist_hs'])
parser.add_argument('-multiplier',default=1.0,help="CO2 Multiplier")
parser.add_argument('-co2',default=None, help="CO2 Value")
parser.add_argument('-land_year',default=0,type=land_year_range,metavar=f'[{min_land_year}-{max_land_year}]',help="Years prior to current era in units of Ma")
parser.add_argument('-case',default='test',type=str)
parser.add_argument('-ntasks',default=96,type=int)
parser.add_argument('-nthrds',default=24,type=int)
parser.add_argument('-run',default=False,action='store_true')
parser.add_argument('-out_tstep',default=24)
parser.add_argument('-start_date',default="1979-01-01")
parser.add_argument('-ndays',default=2,type=int)
parser.add_argument('-data_dir',default=env.INPUT_DATA_DIR)
parser.add_argument('-cime_out_dir',default=env.CIME_OUT_DIR)
parser.add_argument('-rebuild',default=False,action='store_true')
parser.add_argument('-res',default="f09_f09_mg17",type=str)
parser.add_argument('-compset',default="QSC6",type=str)
parser.add_argument('-custom',default=False,action='store_true')
args=parser.parse_args()

#start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
#stop_date=(start_date + datetime.timedelta(days=args.ndays)).strftime("%Y%m%d")

cwd=os.getcwd()

args.case="%s/cases/%s" %(env.MAIN_DIR,args.case)

def edit_namelists():
        
    os.chdir(cwd)
    nl_cam_file="%s/user_nl_cam"%(args.case)
    nl_cpl_file="%s/user_nl_cpl"%(args.case)
                    
    contents=[]
    contents.append('\n')
    contents.append('nhtfrq=-%s\n'%(args.out_tstep))
    contents.append('mfilt=365\n')

    if args.exp_type=='cam_co2':
        #contents.append("scenario_ghg='FIXED'\n")
        contents.append(f"co2vmr={args.multiplier*interpolate_co2(args.land_year)}\n")
    #    #contents.append(f'ramp_co2_cap=-{float(args.multiplier)}\n')

    print("**Changing namelist file: %s**"%(nl_cam_file))
    with open(nl_cam_file,'w') as f:
        for l in contents: f.write(l)
    f.close()


if args.exp_type=='aqua':

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
    #args.res="T42_T42"

elif args.exp_type=='cam_co2':

    args.custom=True
    #args.compset="2000_CAM60%RCO2_SLND_SICE_SOCN_SROF_SGLC_SWAV"
    #args.compset="2000_CAM60%SCAM_CLM50%SP_CICE%PRES_DOCN%DOM_SROF_SGLC_SWAV"
    args.compset="2000_CAM60%SCAM_CLM50%CN_SICE_SOCN_SROF_SGLC_SWAV"
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
    create_case_cmd='create_newcase --run-unsupported --case %s --res %s --mach aws_c5 --compset %s --handle-preexisting-dirs r --output-root %s'%(args.case,args.res,args.compset,args.cime_out_dir)
else:
    create_case_cmd='create_newcase --case %s --res %s --mach aws_c5 --compset %s --handle-preexisting-dirs r --output-root %s'%(args.case,args.res,args.compset,args.cime_out_dir)


change_xml_cmd='./xmlchange NTASKS=%s' %(args.ntasks)
#change_xml_cmd+='; ./xmlchange NTHRDS=%s' %(args.nthrds)
#change_xml_cmd+='; ./xmlchange RUN_STARTDATE=%s' %(args.start_date)
change_xml_cmd+='; ./xmlchange STOP_N=%s' %(args.ndays)

if args.exp_type=='cam_co2':
    change_xml_cmd+=f'; ./xmlchange CCSM_CO2_PPMV={args.multiplier*interpolate_co2(args.land_year)}'
    #change_xml_cmd+=f'; ./xmlchange scenario_ghg="FIXED"'
    #change_xml_cmd+=f'; ./xmlchange ramp_co2_cap=-{float(args.multiplier)}'


if args.rebuild or not os.path.exists(args.case):
    os.system('rm -rf %s' %(args.case))
    case_name = (args.case).split('cases')
    os.system('rm -rf %s/cases/%s' %(env.SCRATCH_DIR,case_name[1]))

    os.system(create_case_cmd)
    edit_namelists()
    os.chdir(args.case)
    os.system(change_xml_cmd)
    os.system('./case.setup')
    os.system('./case.build')

else:
    os.chdir(args.case)
    os.system(change_xml_cmd)


if args.run:
    try:
        os.system('./case.submit')
    except:
        logger.error("Error submitting case")
        exit()


import ecrlcesm.environment as env

import os
import argparse
import datetime

parser=argparse.ArgumentParser(description="Run CESM")
parser.add_argument('-case',default='test',type=str)
parser.add_argument('-aqua',default=False,action='store_true')
parser.add_argument('-cam',default=False,action='store_true')
parser.add_argument('-cam_land',default=False,action='store_true')
parser.add_argument('-cam_double_co2',default=False,action='store_true')
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

    if args.cam_double_co2:
        contents.append("scenario_ghg='RAMP_CO2_ONLY'\n")
        contents.append('ramp_co2_cap=-2.0\n')

    print("**Changing namelist file: %s**"%(nl_cam_file))
    with open(nl_cam_file,'w') as f:
        for l in contents: f.write(l)
    f.close()


if args.aqua:

    args.compset="QSC6"
    args.res="f09_f09_mg17"

elif args.cam:

    args.custom=True
    args.compset="2000_CAM60_SLND_SICE_SOCN_SROF_SGLC_SWAV"
    args.res="f19_f19_mg17"

elif args.cam_land:

    args.custom=True
    args.compset="2000_CAM60%SCAM_CLM50%CN_SICE_SOCN_SROF_SGLC_SWAV"
    args.res="f19_f19_mg17"
    #args.res="T42_T42"

elif args.cam_double_co2:

    args.custom=True
    args.compset="2000_CAM60%RCO2_SLND_SICE_SOCN_SROF_SGLC_SWAV"
    args.res="f19_f19_mg17"


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

if args.rebuild:
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

try:
    os.system('./case.submit')
except:
    print("Error submitting case")
    exit()


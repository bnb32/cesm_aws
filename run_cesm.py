import os
import argparse
import sys
sys.path.append('./')
import environment as env
import datetime

os.environ["PATH"]+=":%s"%env.CESM_SCRIPTS

parser=argparse.ArgumentParser(description="Run CESM")
parser.add_argument('-case',default='test',type=str)
parser.add_argument('-drycore',default=False,action='store_true')
parser.add_argument('-cam',default=False,action='store_true')
parser.add_argument('-ntasks',default=96,type=int)
parser.add_argument('-nthrds',default=24,type=int)
parser.add_argument('-run',default=False,action='store_true')
parser.add_argument('-out_tstep',default=24)
parser.add_argument('-start_date',default="1980-03-15")
parser.add_argument('-ndays',default=100,type=int)
parser.add_argument('-stop_date',default="19800320")
parser.add_argument('-data_dir',default=env.INPUT_DATA_DIR)
parser.add_argument('-cime_out_dir',default=env.CIME_OUT_DIR)
parser.add_argument('-rebuild',default=False,action='store_true')
parser.add_argument('-res',default="T42z30_T42_mg17",type=str)
parser.add_argument('-compset',default="FHS94",type=str)
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
    contents.append('nhtfrq=-%s\n'%(args.out_tstep))
    contents.append('mfilt=365\n')

    print("**Changing namelist file: %s**"%(nl_cam_file))
    with open(nl_cam_file,'w') as f:
        for l in contents: f.write(l)
    f.close()


if args.drycore:    
    args.compset="FHS94"
    args.res="T42z30_T42_mg17"

elif args.cam:
    #args.compset="FHIST"
    #args.res="f09_f09_mg17"

    #CAM simplified and non-versioned physics 
    #CAM dry adiabatic baroclinic instability
    #args.compset="FDABIP04"
    #args.res="T42z30_T42_mg17"
    
    #args.compset="FCSCAM"
    #args.res="T42_T42"

    #args.compset="F2000climo"
    #args.res="f09_f09_mg17"

    args.compset="FWHIST"
    args.res="f09_f09_mg17"

else:
    print("Select valid case: <aqua/drycore/cam>")
    exit()

#create_case_cmd='create_newcase --mpilib openmpi --run-unsupported --case %s --res %s --compset %s --project %s --handle-preexisting-dirs r --output-root %s'%(args.case,args.res,args.compset,args.project,args.cime_out_dir)
create_case_cmd='create_newcase --case %s --res %s --mach aws_c5 --compset %s --handle-preexisting-dirs r --output-root %s'%(args.case,args.res,args.compset,args.cime_out_dir)

change_xml_cmd='./xmlchange NTASKS=%s' %(args.ntasks)
#change_xml_cmd+='; ./xmlchange NTHRDS=%s' %(args.nthrds)
change_xml_cmd+='; ./xmlchange RUN_STARTDATE=%s' %(args.start_date)
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

try:
    os.system('./case.submit')
except:
    print("Error submitting case")
    exit()


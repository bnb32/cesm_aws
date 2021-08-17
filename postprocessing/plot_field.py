import os,sys
import argparse
sys.path.append('/home/ec2-user/environment/cesm_aws/')
import environment as env

parser=argparse.ArgumentParser(description="Plot CESM field")
parser.add_argument('-infile',required=True,type=str)
parser.add_argument('-outdir',default="%s/figs/"%(env.POST_PROC_DIR),type=str)
parser.add_argument('-field',default="Z3",type=str)
parser.add_argument('-level',default=250,type=int)
parser.add_argument('-drycore',default=False,action='store_true')
parser.add_argument('-aqua',default=False,action='store_true')

args=parser.parse_args()

case_name=(args.infile).split('/')[-1]
tmp=case_name.split('.cam')
case_name=tmp[0]
suffix='cam'+tmp[1]

if args.drycore: 
    case_type="drycore"
elif args.aqua: 
    case_type="aqua"
else:
    print("Select valid case type\n")
    exit()

cmd='ncl \'outdir="%s"\' \'infile="%s"\' \'case_name="%s"\' \'case_type="%s"\' \'field="%s"\' level=%s  %s/plot_field.ncl' %(args.outdir,args.infile,case_name,case_type,args.field,args.level,env.POST_PROC_DIR)

os.system(cmd)    

from ecrlgcm.misc import land_years, get_logger

import argparse
import os
import time

logger = get_logger()

years = [0,0.02,3,5,10,50,55,65,100,150,230,350,450,500]
ntasks = [2,4,8,16,32,64,96]

parser=argparse.ArgumentParser(description="Run CESM batch")
parser.add_argument('-years',default=False,action='store_true')
parser.add_argument('-restart',default=False,action='store_true')
parser.add_argument('-timing',default=False,action='store_true')
parser.add_argument('-remap',default=False,action='store_true')
args=parser.parse_args()

if args.years:
    for y in years:
        cmd = f'python run_cesm.py -year {y}'
        if not args.restart:
            cmd+=' -run_all'
        else:
            cmd+=' -restart'
        if args.remap:
            cmd+=' -remap -remap_hires'
        if y==0.02: cmd+=' -sea_level -100'
        os.system(cmd)

elif args.remap:
    for y in years:
        cmd = f'python run_cesm.py -year {y} -remap -remap_hires'
        if y==0.02: cmd+=' -sea_level -100'
        os.system(cmd)

elif args.timing:
    for n in ntasks:
        cmd = f'python run_cesm.py -year 0 -ntasks {n} -timing'
        start_time = time.time()
        os.system(cmd)
        end_time = time.time()
        logger.info(f'Time elapsed: {end_time-start_time}')

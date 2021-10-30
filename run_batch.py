from ecrlgcm.misc import land_years
import os

years = [0,0.02,3,5,10,50,55,65,100,150,230,350,450,500]

for y in years:
    cmd = f'python run_cesm.py -year {y} -restart -nsteps 100'
    #cmd = f'python run_cesm.py -year {y} -run_all -remap -remap_hires'
    #cmd = f'python run_cesm.py -year {y} -remap -remap_hires'
    if y==0.02: cmd+=' -sea_level -100'
    os.system(cmd)

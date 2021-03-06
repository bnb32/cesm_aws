# README #

This repo is for setting up cesm on AWS.

**RUNNING CESM**

1. Create new cloud9 instance:   
   - select vpc-00177ee82dc8fe654 under "Network Settings"

2. Add default security group to your cloud9 instance:    
   - Go to AWS console  
   - Click on running instances  
   - Click on your instance in the list  
   - Click on actions, networking, change security groups  
   - Select default group and assign group

3. Clone cesm_aws and gcm_aws repos to your cloud9 instance:    
   - Modify environment variables in `gcm_aws/eclrgcm/environment.py`

4. Run the following commands to install packages and mount storage
```bash
$ cd gcm_aws
$ pip install -e . 
$ cd ../cesm_aws
$ pip install -e .
$ bash ./go.sh  
```

5. Finally run the following for description of parameters  
```bash    
$ python run_cesm.py -h
```

6. cesm output will be in `'/data/<username>/scratch/archive/<case>'`

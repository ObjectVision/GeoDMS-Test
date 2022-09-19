INTRO
This document describes the steps to use the GeoDMSPerformance.py script, which creates an interactive representation of the performance of GeoDMS for a given item in a configuration.

PREREQUISITES
Python 3.x is required in order to run, and can be installed from https://www.python.org/downloads/. Make sure to register to system path.
The script requires the following python packages, which can be installed using: pip install <package>, but more easily installed using pip install -r requirements.txt from
the script folder:
- psutil
- bokeh

OVERVIEW
GeoDMSPerformance.py is a tool that helps the GeoDMS modeler get insight into the performance of a model. 
The script lets the user define performance experiments and make comparisons between revisions in terms of:
- cpu usage
- virtual and physical memory
- number of threads
- bytes read and written. 

EXPERIMENT FILE
Experiments are defined using an experiment file. This file has two sections: 1) general parameters, 2) definitions of experiments.
Every line starting with: "#" is interpreted as comment. 

1) The general section has three parameters and are mandatory given as key value pair, with a semi-colon as separator and no spaces or tabs: <KEY;VALUE>:
cfg;VALUE
item;VALUE
storage_fldr;VALUE

cfg:  	      parameter defines the starting GeoDMS configuration file, 										ie: cfg;stam.dms
item: 		  parameter denotes the configration item to profile 												ie: item;ResultingState/landuse
storage_fldr: is the location where the experiments data and final interactive html figure are stored	        ie: storage_fldr;D:\GeoDMS_experiments

2) Experiment definitions take up one line per experiment, and are setup using csv style approach, each experiment takes up to six fields
These fields are again separated by a semi-colon: name;svn;exe_fldr;ld_fldr;flags;fullname with field definitions:
name: name of the experiment
svn (optional): only required when testing a working copy of GeoDMS otherwise leave empty, 
			    two parameters, separated by a comma: GeoDMS working copy path,revision 			     	    ie: C:\dev\geodms\branches\v8001,14234
				
exe_fldr: folder where the GeoDMSRun.exe to be tested is located.
ld_fldr(optional): LocalData folder, in case of testing GeoDMS version<=8 to not make an comparison unfair using the calccache.
flags: experiment flags passed to GeoDMSRun.exe for instance /S1 /S2
fullname: experiments are stored in storage_fldr/experiment_data. These experiments of the past can also directly be used to combine into an interactive figure.
          If the user enters a fullname, all other parameters are neglected and the fullname is used to directly load the experiment data.

EXAMPLE_EXPERIMENTS
# GeoDMS installed
7214;;C:\"Program Files"\ObjectVision\GeoDms7412\;C:\LocalData\100m_DynaPop_v8;/S1 /S2;

# GeoDMS build from svn revision
8005;C:\dev\geodms\branches\v8001,14234;C:\dev\geodms\branches\v8001\bin\Release\x64\;;/S1 /S2;

# Saved experiment file
;;;;;D:\GeoDMS_experiments_small\experiment_data\7214_S1S2_000000000000000000004CCC6AD6787A_508454196354344.bin

# Batch file calling GeoDMSRun (leave cfg and item empty; enter name and batch full path at exe_fldr field, in case of log enter the full path in the flags field)
cfg;
item;
storage_fldr;D:\GeoDMS_experiments\batch\

name;svn;exe_fldr;ld_fldr;flags;fullname
7412;;C:\prj\tst\batch\fast.bat 7412;;;

# GeoDMSGui
7214_gui;;C:\"Program Files"\ObjectVision\GeoDms7412\GeoDmsCaller.exe;C:\LocalData\100m_DynaPop_v8;/S1 /S2;

USAGE
To run a given experiment file use command: python GeoDMSPerformance.py <experiment.file>.

OUTPUT
Three outputs are generated:
1. one log per experiment, which is a temporary file and can be discarded afterwards
2. experiment data is stored as storage_fldr/experiment_data//{filename}.bin where the filename is build from the following parameters:
{name}_{revision}_{flags}_{uuid}_{cfg_item_hash}.bin with:
name: name of the experiment as given by the user
revision: GeoDMS svn revision number used as specified by the user in the svn parameter
flags: GeoDMSRun.exe flags as given by the user in the flags parameter
uuid: a unique machine indentifier build up as a hash of multiple component ids, generated using command: "wmic cpu get ProcessorId".
cfg_item_hash: 15-digit hash of cfg + item parameters using sha256 method.

3. Interactive html figure is the output of the performance experiments and is stored in compare.html file in the user defined output_fldr parameter
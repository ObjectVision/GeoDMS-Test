import os
import re
import psutil
import shutil
from datetime import datetime
import time
import pickle
import hashlib
import difflib
import subprocess
import argparse
import csv

from bokeh import plotting
from bokeh.models import HoverTool, PanTool, ResetTool, WheelZoomTool, CheckboxGroup, CheckboxButtonGroup, CustomJS, Legend, LegendItem
from bokeh.layouts import row, column
from bokeh.palettes import Category10, Category20, Category20b, Category20c

class Experiment:
    def __init__(self, name, command, experiment_folder, environment_variables, cwd, geodms_logfile, binary_experiment_file):
        self.name                   = name
        self.command                = command
        self.experiment_folder      = experiment_folder
        self.environment_variables  = environment_variables
        self.cwd                    = cwd
        self.geodms_logfile         = geodms_logfile
        self.binary_experiment_file = binary_experiment_file
        self.result = {}
        def __str__(self):
            return f"Experiment: name:{name} command:{command}"

def readLog(log_filename, filter=None):
    ret = {"time":[], "text":[]}
    if not os.path.exists(log_filename):
        return ret

    with open(log_filename, "r") as f:
        date_end = 19
        while (True):
            line = f.readline()
            if not line:
                break
                
            if len(line) <= 26: # empty line, no information
                continue
                 
            if not line[0].isnumeric():
                continue
                
            if filter and not filter in line:
                continue

            date  = line[0:date_end]

            #2023-11-15 09:39:22
            datet = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            ret["time"].append(datet)
            ret["text"].append(f"{line[date_end:]}<br>")
    return ret

def readLogAllocator(log_fn, start_time):
    log_alloc = {"time":[], "dtime":[], "reserved":[], "allocated":[], "freed":[], "uncommitted":[], "PageFileUsage":[]}
    alloc_log = readLog(log_fn, filter="Reserved in Blocks")

    if len(alloc_log["time"]) == 0:
        return None

    for ind in range(len(alloc_log["time"])):
        print(alloc_log["time"][ind], alloc_log["text"][ind])  
        # 2023-11-21 14:10:50[1]Reserved in Blocks 63532[MB]; allocated: 0[MB]; freed: 62532[MB]; uncommitted: 999[MB]; PageFileUsage: 62767[MB]
        integers_in_entry = re.findall(r"\d+", alloc_log["text"][ind])[1:]
        print(integers_in_entry)
        if len(integers_in_entry) < 5:
            continue
        
        log_alloc["time"].append(alloc_log["time"][ind])
        log_alloc["dtime"].append((alloc_log["time"][ind]-start_time).total_seconds())
        log_alloc["reserved"].append(int(integers_in_entry[0])*10**-3)      # [GB]
        log_alloc["allocated"].append(int(integers_in_entry[1])*10**-3)     # [GB]
        log_alloc["freed"].append(int(integers_in_entry[2])*10**-3)         # [GB]
        log_alloc["uncommitted"].append(int(integers_in_entry[3])*10**-3)   # [GB]
        log_alloc["PageFileUsage"].append(int(integers_in_entry[4])*10**-3) # [GB]
    return log_alloc

def getProcessIdIfActive(names, parent_pid=None):
    pid = -1
    if not type(names)== list:
        names = [names]

    # if parent pid is given, use this scope only
    for i in range(10):
        if parent_pid:
            if not psutil.pid_exists(parent_pid):
                time.sleep(0.5)
                continue
            
            parent_process = psutil.Process(parent_pid)
            for child_process in parent_process.children(recursive=True):
                print(child_process.name())
                for name in names:
                    if(name.lower() in child_process.name().lower()):
                        print(child_process.name())
                        return child_process.pid
        else:
            for proc in psutil.process_iter():
                for name in names:
                    if(name.lower() in proc.name().lower()):
                        pid = proc.pid # assume only one exe_name is active at this time!
                        return pid
        time.sleep(0.5)
    return pid

def getProcessCurrentStatistics(process:psutil.Process, experiment_start_time, cpu_curr_time=None):
    t=None
    dt=None
    cpu_p=0
    cpu_ct=cpu_curr_time
    mem_p=0
    rss=0
    vms=0
    num_threads=0
    rb=0
    wb=0
    net_c=0

    try:
        with process.oneshot():
            cur_time = datetime.now()
            t = cur_time
            dt = (cur_time-experiment_start_time).total_seconds()
            cpu_p_raw = process.cpu_percent()
            num_cpus = psutil.cpu_count()
            cpu_p = cpu_p_raw / num_cpus
            print(f"{num_cpus} {cpu_p_raw} {cpu_p}")
            if cpu_curr_time:
                cpu_ct += cpu_p / 100.0
            mem_p = process.memory_percent()
            memory_info = process.memory_info()
            rss = memory_info.rss * 10.0**-9.0 # GB
            vms = memory_info.vms * 10.0**-9.0 # GB
            num_threads = process.num_threads()
            io_counters = process.io_counters()
            rb = io_counters.read_bytes/10.0**9 # GB
            wb = io_counters.write_bytes/10.0**9 # GB
            net_c = len(process.net_connections())
    except:
        return [t, dt, cpu_p, cpu_ct, mem_p, rss, vms, num_threads, rb, wb, net_c]
    return [t, dt, cpu_p, cpu_ct, mem_p, rss, vms, num_threads, rb, wb, net_c]

def getPerformance(exp:Experiment, sampling_rate=1.0):
    profile_log = {"time":[], "dtime":[], "cpu_percent":[], "cpu_curr_time":[], "memory_percent":[], "rss":[], "vms":[], "num_threads":[], "total_read_bytes":[], "total_write_bytes":[], "net_connections":[], "processes":[]} # rss=resident set size (aka physical non swapped memory in use by process), vms virtual memory ize
    command = exp.command
    env = exp.environment_variables
    cwd = exp.cwd
    
    parent_process_open_handle = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)    
    parent_process = psutil.Process(parent_process_open_handle.pid)
    experiment_start_time = datetime.fromtimestamp(parent_process.create_time())
    cpu_ct = 0
    while (psutil.pid_exists(parent_process.pid)):
        print("BEGIN\n")
        time_measurement_start = datetime.now()
        t, dt, cpu_p, cpu_ct, mem_p, rss, vms, num_threads, rb, wb, net_c = getProcessCurrentStatistics(parent_process, experiment_start_time, cpu_ct)
        profile_log["time"].append(t)
        profile_log["dtime"].append(dt)
        profile_log["cpu_percent"].append(cpu_p)
        profile_log["cpu_curr_time"].append(cpu_ct)
        profile_log["memory_percent"].append(mem_p)
        profile_log["rss"].append(rss)
        profile_log["vms"].append(vms)
        profile_log["num_threads"].append(num_threads)
        profile_log["total_read_bytes"].append(rb)
        profile_log["total_write_bytes"].append(wb)
        profile_log["net_connections"].append(net_c)
        child_processes = parent_process.children(recursive=True) 
        profile_log["processes"].append(len(child_processes)+1)

        for child_process in child_processes:
            t, _, cpu_p, _, mem_p, rss, vms, num_threads, rb, wb, net_c = getProcessCurrentStatistics(child_process, experiment_start_time)
            if not t:
                continue
            profile_log["cpu_percent"][-1]       += cpu_p
            profile_log["memory_percent"][-1]    += mem_p
            profile_log["rss"][-1]               += rss
            profile_log["vms"][-1]               += vms
            profile_log["num_threads"][-1]       += num_threads
            profile_log["total_read_bytes"][-1]  += rb
            profile_log["total_write_bytes"][-1] += wb
            profile_log["net_connections"][-1]   += net_c
        print("END\n")
        time_measurement_end = datetime.now()
        dtimestamp = (time_measurement_end-time_measurement_start).total_seconds()
        sleep_time = sampling_rate-dtimestamp        
        if sleep_time > 0.0:
            time.sleep(sleep_time)
        else:
            print(f"Warning: measurements of calculation process took {dtimestamp} seconds, and is longer than sampling rate: {sampling_rate}")

    return profile_log, experiment_start_time

def getClosestLog(dms_log_t, profile_log, param):
    smallest_dt = 99999999999.0 # absurdly large
    ind_chosen = None
    for ind, profile_log_t in enumerate(profile_log["time"]):
        dt = abs((dms_log_t-profile_log_t).total_seconds())
        if dt < smallest_dt:
            smallest_dt = dt
            ind_chosen = ind
    assert ind_chosen, "dms_log datetime falls within profile log datetime range, hence index should be between 0 and the end of the profile log"
    return (ind_chosen, profile_log[param][ind_chosen])

def getClosestProfilelogForGeodmslog(profile_log, geodms_log, param):
    xy = {"ind":[], "x":[], "y":[], "dms_log_ind":[]}
    for i, dms_log_t in enumerate(geodms_log["time"]):
        profile_log_first_datetime = profile_log['time'][0]
        profile_log_last_datetime = profile_log['time'][-1]
        dmslogt_seconds_after_profile_start = (dms_log_t - profile_log_first_datetime).total_seconds() # positive when dms_log_t is after start of profile
        dmslogt_seconds_before_profile_end = (profile_log_last_datetime - dms_log_t).total_seconds() # positive when dms_log_t is before end of profile

        if dmslogt_seconds_after_profile_start < -1.0 or dmslogt_seconds_before_profile_end < -1.0:
            print(f"Geodms log entry is outside experiment timeline: {geodms_log['text'][i]} {dmslogt_seconds_after_profile_start} {dmslogt_seconds_before_profile_end}")
            continue

        (ind, y) = getClosestLog(dms_log_t, profile_log, param)
        xy["ind"].append(ind)
        xy["x"].append(profile_log["dtime"][ind])
        xy["y"].append(y)
        xy["dms_log_ind"].append(i)
    return xy

def getCompactClosestLogForRLog(profile_log, geodms_log, param, max_lines=50):
    rlog_compact = {"inds":{}, "x":[], "y":[], "text":[], "num_text_lines":[], "IsEnded":{}}
    xy = getClosestProfilelogForGeodmslog(profile_log, geodms_log, param)
    
    ind_cur = 0
    for i in range(len(xy["x"])):
        ind_log = xy["ind"][i]
        dtime = xy["x"][i]
        val   = xy["y"][i]
        ind_geodms_log = xy["dms_log_ind"][i]

        if ind_log not in rlog_compact["inds"]:
            rlog_compact["inds"][ind_log] = ind_cur
            rlog_compact["x"].append(dtime)
            rlog_compact["y"].append(val)
            rlog_compact["text"].append(geodms_log["text"][ind_geodms_log])
            rlog_compact["num_text_lines"].append(1)
            ind_cur += 1
        else:
            rlog_compact["num_text_lines"][rlog_compact["inds"][ind_log]] += 1
            if (rlog_compact["num_text_lines"][rlog_compact["inds"][ind_log]] > max_lines):
                continue
            rlog_compact["text"][rlog_compact["inds"][ind_log]] += geodms_log["text"][ind_geodms_log]
            if (rlog_compact["num_text_lines"][rlog_compact["inds"][ind_log]] == max_lines):
                rlog_compact["text"][rlog_compact["inds"][ind_log]] += "...<br>"

    return rlog_compact
    
def getLogInfoForPlotting(log, log_fn, param):
    geodms_log = readLog(log_fn)
    rlog_compact = getCompactClosestLogForRLog(log, geodms_log, param)
    return rlog_compact

def getSvnVersion(exp):
    if exp.svn[0]:
        svn_id = subprocess.run("svn info --show-item last-changed-revision", cwd=exp.svn[0], capture_output=True).stdout.decode("utf-8")
        svn_id = svn_id.replace("\n", "")
        svn_id = svn_id.replace("\r", "")
    else:
        svn_id = "<non versioned>"
    return svn_id

def getExperimentFileName(experiment:Experiment):
    experiment_hash = int(hashlib.sha256((experiment.name + experiment.command).encode('utf-8')).hexdigest(), 16) % 10**15
    
    fldrname = f"{experiment.experiment_folder}/experiment_data/"
    if not os.path.exists(fldrname):
        os.makedirs(fldrname)
    filename  = f"{experiment.name}{experiment_hash}.bin"
    return (fldrname, filename)

def storeExperimentToPickleFile(experiment):
    fldrname, filename = getExperimentFileName(experiment)
    exp_fn = fldrname + filename
    with open(exp_fn, "wb") as f:
        pickle.dump(experiment, f)
    return
    
def loadExperimentFromPickleFile(experiment, exp_fn=None):
    if not exp_fn:
        fldrname, filename = getExperimentFileName(experiment)
        exp_fn = fldrname + filename

    with open(exp_fn, "rb") as f:
        experiment = pickle.load(f)
    return experiment

def RunExperiments(experiments:list[Experiment], sampling_rate=1.0):
    for exp_index, exp in enumerate(experiments):
        bin_exp_fn = exp.binary_experiment_file
        if bin_exp_fn:
            if not os.path.exists(bin_exp_fn): # check if experiment exists
                print(f"Experiment file: {bin_exp_fn} does not exist, skipping experiment.")
                experiments[exp_index] = None
                continue
            experiments[exp_index] = loadExperimentFromPickleFile(None, exp_fn=bin_exp_fn)
            print(experiments[exp_index])
            continue
        
        fldrname, filename = getExperimentFileName(exp)
        exp_fn = fldrname + filename
        
        #if os.path.exists(exp_fn): # Experiment is calculated before, do not recalculate
        #    experiments[exp_index] = loadExperimentFromPickleFile(None, exp_fn)
        #    continue

        # Sample performance
        geodms_logfile = exp.geodms_logfile
        if os.path.exists(geodms_logfile): # always start with empty log
            os.remove(geodms_logfile)
        exp.result["log"], start_time = getPerformance(exp)

        if os.path.exists(geodms_logfile):
            exp.result["cpu_percent"]       = getLogInfoForPlotting(exp.result["log"], geodms_logfile, "cpu_percent")
            exp.result["cpu_curr_time"]     = getLogInfoForPlotting(exp.result["log"], geodms_logfile, "cpu_curr_time")
            exp.result["memory_percent"]    = getLogInfoForPlotting(exp.result["log"], geodms_logfile, "memory_percent")
            exp.result["num_threads"]       = getLogInfoForPlotting(exp.result["log"], geodms_logfile, "num_threads")
            exp.result["rss"]               = getLogInfoForPlotting(exp.result["log"], geodms_logfile, "rss")
            exp.result["vms"]               = getLogInfoForPlotting(exp.result["log"], geodms_logfile, "vms")
            exp.result["read_bytes"]        = getLogInfoForPlotting(exp.result["log"], geodms_logfile, "read_bytes")
            exp.result["write_bytes"]       = getLogInfoForPlotting(exp.result["log"], geodms_logfile, "write_bytes")
            exp.result["total_read_bytes"]  = getLogInfoForPlotting(exp.result["log"], geodms_logfile, "total_read_bytes")
            exp.result["total_write_bytes"] = getLogInfoForPlotting(exp.result["log"], geodms_logfile, "total_write_bytes")

        # Get allocator state from log
        log_alloc = readLogAllocator(geodms_logfile, start_time) # temporarily disable allocator logging
        exp.result["log_alloc"] = None
        if log_alloc:
            exp.result["log_alloc"] = log_alloc

        storeExperimentToPickleFile(exp)

    return experiments

def vgroupToLabel(vgroup):
    if vgroup[0] == "cpu_percent":
        label = "cpu (%)"
    elif vgroup[0] == "cpu_curr_time":
        label = "cpu time (s)"
    elif vgroup[0] == "memory_percent":
        label = "memory (%)"
    elif vgroup[0] == "num_threads":
        label = "threads (#)"
    elif vgroup[0] == "read_bytes":
        label = "read bytes (mb/s)"
    elif vgroup[0] == "write_bytes":
        label = "written bytes (mb/s)"
    elif vgroup[0] == "total_read_bytes":
        label = "total read bytes (GB)"
    elif vgroup[0] == "total_write_bytes":
        label = "total written bytes (GB)"    
    elif type(vgroup[0]) is tuple or vgroup[0]=="vms":
        label = "Committed and and freelist allocated memory (^) (GB)"
    
    return label
    
def ExpHasLogAvailable(exp, key):
    if key in exp.result and len(exp.result[key]):
        return True
    return False

def VisualizeExperiments(experiments, vgroups):
    tool_tips = """
    <div>
        <div>
            <span style="font-size: 12px;">x: $x, y: $y</span>
        </div>
        <div>
            <span style="font-size: 12px;">@text</span>
        </div>
    
    </div>
    """

    figs = []
    renderers = []
    colors = []
    labels = []
    for i, exp in enumerate(experiments):
        colors.append(Category10[10][i])
        fldrname, filename = getExperimentFileName(exp)
        labels.append(filename[:-4])

    # create ColumnDataSource(s)
    exps_ds = []
    for i, exp in enumerate(experiments):
        exp_ds_graphs = {}
        exp_ds_logs = {}
        exp_ds_alloc = {"time":[], "allocated":[], "text":[]}
        exp_ds_graphs["time"] = exp.result["log"]["dtime"]
        for ii, vgroup in enumerate(vgroups):
            if type(vgroup[0]) is tuple:
                if not "time" in exp_ds_logs and ExpHasLogAvailable(exp, vgroup[0][0]):
                    exp_ds_logs["time"]     = exp.result[vgroup[0][0]]["x"]
                    exp_ds_logs["text"]     = exp.result[vgroup[0][0]]["text"]
                if ExpHasLogAvailable(exp, vgroup[0][0]):
                    exp_ds_logs[vgroup[0][0]]   = exp.result[vgroup[0][0]]["y"]
                    exp_ds_logs[vgroup[0][1]]   = exp.result[vgroup[0][1]]["y"]
                exp_ds_graphs[vgroup[0][0]] = exp.result["log"][vgroup[0][0]]
                exp_ds_graphs[vgroup[0][1]] = exp.result["log"][vgroup[0][1]]
            else:
                if not "time" in exp_ds_logs and ExpHasLogAvailable(exp, vgroup[0]):
                    exp_ds_logs["time"] = exp.result[vgroup[0]]["x"]
                    exp_ds_logs["text"] = exp.result[vgroup[0]]["text"]
                if ExpHasLogAvailable(exp, vgroup[0]):
                    exp_ds_logs[vgroup[0]]  = exp.result[vgroup[0]]["y"]
                exp_ds_graphs[vgroup[0]] = exp.result["log"][vgroup[0]]
            if vgroup[0]=="vms": # allocator log only added to committed memory figure
                if exp.result["log_alloc"]:
                    exp_ds_alloc["time"] = exp.result["log_alloc"]["dtime"] 
                    exp_ds_alloc["allocated"] = exp.result["log_alloc"]["allocated"]
                    for i in range(len(exp.result["log_alloc"]["dtime"])):
                        exp_ds_alloc["text"].append(f"A: {exp.result['log_alloc']['allocated'][i]}, R: {exp.result['log_alloc']['reserved'][i]}, F: {exp.result['log_alloc']['freed'][i]}, U: {exp.result['log_alloc']['uncommitted'][i]}")

        exps_ds.append([exp_ds_graphs, exp_ds_logs, exp_ds_alloc])
        
    for ii, vgroup in enumerate(vgroups):
        title = ""
        
        if not vgroup[1]: # no y_range
            p = plotting.figure(width=2000, height=500, tooltips=tool_tips, tools="pan,wheel_zoom,box_zoom,reset,save,hover", title=title)
        else:
            p = plotting.figure(width=2000, height=500, y_range=(vgroup[1][0], vgroup[1][1]), tooltips=tool_tips, tools="pan,wheel_zoom,box_zoom,reset,save,hover", title=title)
            
        for i, exp in enumerate(experiments):
            if not exp:
                continue
                
            color = Category10[10][i]

            fldrname, filename = getExperimentFileName(exp)
            if type(vgroup[0]) is tuple: # do something with this vgroup case
                renderers.append(p.line('time', vgroup[0][0], color=color, line_dash="4 4", source=exps_ds[i][0]))
                renderers.append(p.line('time', vgroup[0][1], color=color, source=exps_ds[i][0]))
                if ExpHasLogAvailable(exp, vgroup[0][0]):
                    renderers.append(p.scatter('time', vgroup[0][1], size=5, color=color, source=exps_ds[i][1]))

                if exps_ds[i][2]: # allocation log was available
                    renderers.append(p.line('time', "allocated", color=color, line_dash="4 4", source=exps_ds[i][2]))
                    renderers.append(p.triangle('time', 'allocated', size=7, fill_color=color, line_color=color, source=exps_ds[i][2]))
            else:
                renderers.append(p.line('time', vgroup[0],            color=color, source=exps_ds[i][0]))
                if ExpHasLogAvailable(exp, vgroup[0]):
                    renderers.append(p.scatter('time', vgroup[0], size=5, color=color, source=exps_ds[i][1]))       
            if vgroup[0]=="vms": # allocator log only added to committed memory figure
                renderers.append(p.line('time', "allocated", color=color, line_dash="4 4", source=exps_ds[i][2]))
                renderers.append(p.triangle('time', 'allocated', size=7, fill_color=color, line_color=color, source=exps_ds[i][2]))
                print(exps_ds[i][2])
                
        p.xaxis.axis_label = 'time (s)'
        #p.xaxis.axis_label_text_font_size = '15px'
        #p.yaxis.axis_label_text_font_size = '15px'
        p.yaxis.axis_label = vgroupToLabel(vgroup)
        p.toolbar.logo = None # remove Bokeh logo

        if figs:
            p.x_range = figs[0].x_range # sync xrange between figures
        
        figs.append(p) # add figure to figs

    legend_items = []
    for i,color in enumerate(colors):
        legend_items.append(LegendItem(label=labels[i], renderers=[renderer for renderer in renderers if renderer.glyph.line_color==color]))
    
    ## Use a dummy figure for the LEGEND
    dum_fig = plotting.figure(width=600,height=600,outline_line_alpha=0,tools="pan,wheel_zoom,box_zoom,reset,save,hover",toolbar_location=None)
    # set the components of the figure invisible
    for fig_component in [dum_fig.grid[0],dum_fig.ygrid[0],dum_fig.xaxis[0],dum_fig.yaxis[0]]:
        fig_component.visible = False
    # The glyphs referred by the legend need to be present in the figure that holds the legend, so we must add them to the figure renderers
    dum_fig.renderers += renderers
    # set the figure range outside of the range of all glyphs
    dum_fig.x_range.end = 1005
    dum_fig.x_range.start = 1000
    # add the legend
    dum_fig.add_layout( Legend(click_policy='hide',location='top_left',border_line_alpha=0,items=legend_items) )

    output_fn = f"{experiments[0].experiment_folder}compare.html"
    print(f"Storing experiments interactive figure in {output_fn}")
    
    grid_structure = []
    for i,fig in enumerate(figs):
        if i == 0:
            grid_structure.append([fig, dum_fig])
        else:
            grid_structure.append([fig, None])
    grid = plotting.gridplot(grid_structure)
    plotting.output_file(output_fn)
    plotting.show(grid)
    return

def InitExperimentsFromCsvFile(fn):
    if not os.path.exists(fn):
        raise Exception(f"Experiment file does not exist: {fn}")
    
    with open(fn) as experiment_csv_file:
        csv_reader = csv.reader(experiment_csv_file, delimiter=";")

        print("Skipping first line in experiment file, assuming it has a header")
        next(csv_reader)

        experiments = []
        for row_index, csv_row in enumerate(csv_reader):
            assert len(csv_row)==7, f"Unexpected number of csv fields ({len(csv_row)}) in experiment file row {row_index}, should be semicolonseparated with fields: name;command;experiment_folder;environment_variables(optional);cwd(optional);geodms_logfile(optional);binary_experiment_file(optional), skipping"
            # experiment fields
            name,command,experiment_folder,environment_variables,cwd,geodms_logfile,binary_experiment_file = csv_row 
            experiments.append(Experiment(name=name, command=command, experiment_folder=experiment_folder, environment_variables=environment_variables,cwd=cwd,geodms_logfile=geodms_logfile,binary_experiment_file=binary_experiment_file))

    return experiments
    
def pause():
    while (True):
        abort = input("Results differ between experiments, investigation required, abort? Press 'y' [yes] or 'n' [no] followed by <ENTER>")
        if abort == "y":
            return True
        elif abort == "n":
            break
        else:
            print(f"Invalid input: {abort}")
        
    return False
    
def compareStatFiles(name1, statfn_1, name2, statfn_2):
    files_are_different = False
    with open(statfn_1) as f, open(statfn_2) as g:
        flines = f.readlines()
        glines = g.readlines()

        d = difflib.Differ()
        diffs = d.compare(flines, glines)
        for lineNum, line in enumerate(diffs):
            # split off the code
            code = line[:2]
            # if the  line is in both files or just b, increment the line number.
            if code in ("  ", "+ "):
                lineNum += 1
            # if this line is only in b, print the line number and the text on the line
            if code == "+ " or code == "- ":
                files_are_different = True
                print(f"{code} {line[2:].strip()}")
        
        if files_are_different:
            print(f"\nFound differences in statistics of experiments: {name1} and {name2}")
        
        return files_are_different

def compareExperimentStatisticsFiles(experiments):
    evaluated_combinations = {}
    results = []
    for i,exp1 in enumerate(experiments):
        if not exp1.cfg and not exp1.item: # batch processed experiment
            continue
        fldrname, filename = getExperimentFileName(exp1)
        name1 = filename[:-4]
        statfn_1 = stat_fn = f"{exp1.storage_fldr}stat{i}.txt"
        for j,exp2 in enumerate(experiments):
            if i == j: # same experiment, same statistics file
                continue
            if (i,j) in evaluated_combinations or (j,i) in evaluated_combinations: # dont evaluate similar combinations
                continue

            fldrname, filename = getExperimentFileName(exp2)
            name2 = filename[:-4]
            statfn_2 = f"{exp2.storage_fldr}stat{j}.txt"
            results.append(compareStatFiles(name1, statfn_1, name2, statfn_2))
            
            evaluated_combinations[(i,j)] = True
            evaluated_combinations[(j,i)] = True
            
    result = False    
    if any(results):    
        result = pause()
    
    return result

def testReadLog():
    log_fn = "D:\\GeoDMS_experiments\\log3.txt"
    log = readLog(log_fn)
    print(log)
    return

def testReadAllocatorInfoLog():
    alloc_info = {"time":[], "reserved":[], "allocated":[], "freed":[], "uncommitted":[]}
    log_fn = "log_with_alloc_info.txt"
    alloc_log = readLog(log_fn, filter="Reserved in Blocks")

    for ind in range(len(alloc_log["time"])):
        print(alloc_log["time"][ind], alloc_log["text"][ind])

        integers_in_entry = re.findall(r"\d+", alloc_log["text"][ind])[1:]
        assert(len(integers_in_entry)==4)
        
        alloc_info["time"].append(alloc_log["time"][ind])
        alloc_info["reserved"].append(int(integers_in_entry[0]))
        alloc_info["allocated"].append(int(integers_in_entry[1]))
        alloc_info["freed"].append(int(integers_in_entry[2]))
        alloc_info["uncommitted"].append(int(integers_in_entry[3]))

    return alloc_log

def Run(config_fn, sampling_rate=1.0):

    # init
    experiments = InitExperimentsFromCsvFile(config_fn)

    if not experiments:
        print(f"No valid experiments found in experiment file: {config_fn}")
        return
        
    # run 
    experiments = RunExperiments(experiments, sampling_rate)
    
    # visualize    
    vgroups = [("cpu_percent", (0,100)), ("cpu_curr_time", False), ("vms", False), ("num_threads", False), ("total_read_bytes", False), ("total_write_bytes", False)]
    VisualizeExperiments(experiments, vgroups)

    return

def RunFromCmdLine():
    # arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("fn", help="csv file that describes experiments: path/to/file.csv")
    parser.add_argument("-s", help="Time between samples, cannot be lower than 1.0")
    args = parser.parse_args()
    config_fn = args.fn
    
    # time between samples
    if args.s:
        if float(args.s) < 1.0:
            print("Argument s set to 1.0, time between samples cannot be lower than 1.0")
            sampling_rate = 1.0
        else:
            sampling_rate = float(args.s)
    else:
        sampling_rate = 1.0

    Run(config_fn, sampling_rate)
    return

def RunTestConfig(config_fn):
    Run(config_fn)
    return

def main():
    RunFromCmdLine()
    return
    
if __name__=="__main__":
    #main()
    RunTestConfig("C:/Users/Cicada/prj/GeoDMS-Test/Performance/scripts/profiler_rework.txt")
    #testReadLog()
    #testReadAllocatorInfoLog()
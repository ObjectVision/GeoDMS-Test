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

from bokeh import plotting
from bokeh.models import HoverTool, PanTool, ResetTool, WheelZoomTool, CheckboxGroup, CheckboxButtonGroup, CustomJS, Legend, LegendItem
from bokeh.layouts import row, column
from bokeh.palettes import Category10, Category20, Category20b, Category20c

class Experiment:
    def __init__(self, name, svn, exe_fldr, ld_fldr, storage_fldr, cfg, item, flags, color=None):
        self.name         = name
        self.svn          = svn
        self.exe_fldr     = exe_fldr
        self.ld_fldr      = ld_fldr
        self.storage_fldr = storage_fldr
        self.cfg          = cfg
        self.item         = item
        self.flags        = flags
        self.color        = color
       
        self.result = {}

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

def getPerformance(exe_name, sampling_rate=1.0, log=None, start_time=None, cpu_curr_time=None, delta_start_time=0.0, parent_pid=None):
    print(f"PARENT PID {parent_pid}")

    if not log:
        log = {"time":[], "dtime":[], "cpu_percent":[], "cpu_curr_time":[], "memory_percent":[], "rss":[], "vms":[], "num_threads":[], "read_bytes":[], "write_bytes":[], "total_read_bytes":[], "total_write_bytes":[]} # rss=resident set size (aka physical non swapped memory in use by process), vms virtual memory size
    pid = getProcessIdIfActive(exe_name, parent_pid)
    
    if pid == -1:
        print("Cannot find process id")
        return log, start_time, cpu_curr_time

    if not psutil.pid_exists(pid):
        print(f"Process id {pid} does not exist.")
        return log, start_time, cpu_curr_time
    
    p = psutil.Process(pid)

    if not start_time:
        start_time = datetime.fromtimestamp(p.create_time()) #datetime.now()
    prev_io_counters = p.io_counters()
    prev_time = start_time
    if not cpu_curr_time:
        cpu_curr_time = 0.0
    while (psutil.pid_exists(pid)):
        timestamp_start = datetime.now()

        try:
            with p.oneshot():
                cur_time = datetime.now()
                log["time"].append(cur_time)
                log["dtime"].append((cur_time-start_time).total_seconds()-delta_start_time)
                cpu_percent = p.cpu_percent() / psutil.cpu_count()
                cpu_curr_time += cpu_percent / 100.0
                log["cpu_percent"].append(cpu_percent)
                log["cpu_curr_time"].append(cpu_curr_time)
                log["memory_percent"].append(p.memory_percent())
                memory_info = p.memory_info()
                log["rss"].append(memory_info.rss * 10.0**-9.0) # GB
                log["vms"].append(memory_info.vms * 10.0**-9.0) # GB
                log["num_threads"].append(p.num_threads())
                io_counters = p.io_counters()
                log["read_bytes"].append((io_counters.read_bytes-prev_io_counters.read_bytes)/(cur_time-prev_time).total_seconds()/10.0**9) # mb/second
                log["write_bytes"].append((io_counters.write_bytes-prev_io_counters.write_bytes)/(cur_time-prev_time).total_seconds()/10.0**9) # mb/second
                log["total_read_bytes"].append(io_counters.read_bytes/10.0**9) # mb
                log["total_write_bytes"].append(io_counters.write_bytes/10.0**9) # mb
        except:
            break

        prev_io_counters = io_counters
        
        timestamp_end = datetime.now()
        dtimestamp = (timestamp_end-timestamp_start).total_seconds()
        sleep_time = sampling_rate-dtimestamp
        #print(sleep_time, dtimestamp)
        prev_time = cur_time
        
        if sleep_time > 0.0:
            time.sleep(sleep_time)
            
    return log, start_time, cpu_curr_time

def getPerformanceBatch(batch_cmd, sampling_rate=1.0):
    exe_name = ["GeoDmsRun.exe", "Python.exe"]
    log = None
    start_time = None
    cpu_curr_time = None
    p = subprocess.Popen(batch_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)

    while p.poll() is None:
        if not start_time:
            log, start_time, cpu_curr_time = getPerformance(exe_name, sampling_rate, log, start_time, cpu_curr_time, parent_pid=p.pid)
        else:
            log,_,cpu_curr_time = getPerformance(exe_name, sampling_rate, log, start_time, cpu_curr_time, parent_pid=p.pid)
    print(f"Finished profiling batchfile {batch_cmd}")
    return log, start_time

def createGeoDMSCallerBatchFile(exp, log_fn, delta_start_time=0):
    gui_caller_cmd_fn = f"{exp.storage_fldr}/tmp_dms_caller_file.bat"
    exe_fldr = os.path.dirname(exp.exe_fldr)
    with open(gui_caller_cmd_fn, "w") as f:
        f.write(f"start \"GeoDmsGui\" /MAX {exe_fldr}\GeoDmsGui.exe {exp.flags} {exp.cfg}\n")
        #f.write(f"\"{exp.exe_fldr}\" WAIT 10\n")
        f.write(f"timeout {int(delta_start_time)}\n")
        f.write(f"{exp.exe_fldr} GOTO \"{exp.item}\"\n")
        f.write(f"{exp.exe_fldr} SEND 5 0 >> {log_fn}\n")
        #f.write(f"{exp.exe_fldr} SEND 1 3 16 0 0 \n")
    return gui_caller_cmd_fn

def getPerformanceGui(exp, log_fn, sampling_rate=1.0):
    delta_start_time = 10.0
    gui_caller_cmd = createGeoDMSCallerBatchFile(exp, log_fn, delta_start_time)
    exe_name = "GeoDmsGui.exe"
    log = None
    start_time = None
    cpu_curr_time = None
    batchfldr_name = os.path.dirname(gui_caller_cmd)
    p = subprocess.Popen(gui_caller_cmd, cwd=batchfldr_name)
    while p.poll() is None:
        log, start_time, cpu_curr_time = getPerformance(exe_name, sampling_rate, log, start_time, cpu_curr_time, delta_start_time)
    return log, start_time

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

def getExperimentFileName(experiment):
    cfg_item_hash = int(hashlib.sha256((experiment.cfg + experiment.item).encode('utf-8')).hexdigest(), 16) % 10**15
    if experiment.svn[1]:
        svn_revision_entry = f"_{experiment.svn[1]}_"
    else:
        svn_revision_entry = "_"

    flags = experiment.flags.replace(" ", "") # remove spaces
    flags = flags.replace("/", "") # remove forward slashes
    
    
    if not experiment.cfg and not experiment.item: # batch file, flags param used for hardcoded log filename
        flags = ""
    
    fldrname = f"{experiment.storage_fldr}experiment_data\\"
    if not os.path.exists(fldrname):
        os.makedirs(fldrname)
    filename  = f"{experiment.name}{svn_revision_entry}{flags}_{cfg_item_hash}.bin"
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

def RunExperiments(experiments, sampling_rate=1.0):
    exe_name = "GeoDmsRun.exe"
    for i, exp in enumerate(experiments):
        
        if type(exp) is str: # Read experiment from stored file
            exp_fn = exp
            if not os.path.exists(exp_fn): # check if experiment exists
                print(f"Experiment file: {exp_fn} does not exist, skipping experiment.")
                experiments[i] = None
                continue
            experiments[i] = loadExperimentFromPickleFile(None, exp_fn=exp_fn)
            fn_no_ext = exp[:-4].split('\\')
            print(f"Experiment: {fn_no_ext[-1]}, rev: {getSvnVersion(experiments[i])}, flags: {experiments[i].flags}, cfg: {experiments[i].cfg}, item: {experiments[i].item}")
            continue
            
        if type(exp) is tuple:
            exp_fn = exp[0]
            if not os.path.exists(exp_fn): # check if experiment exists
                print(f"Experiment file: {exp_fn} does not exist, skipping experiment.")
                experiments[i] = None
                continue
            experiments[i] = loadExperimentFromPickleFile(None, exp_fn=exp_fn)
            experiments[i].storage_fldr = exp[1]
            
            fn_no_ext = exp[0][:-4].split('\\')
            print(f"Experiment: {fn_no_ext[-1]}, rev: {getSvnVersion(experiments[i])}, flags: {experiments[i].flags}, cfg: {experiments[i].cfg}, item: {experiments[i].item}")
            continue
        
        fldrname, filename = getExperimentFileName(exp)
        print(f"Experiment: {filename[:-4]}, rev: {getSvnVersion(experiments[i])}, flags: {experiments[i].flags}, cfg: {experiments[i].cfg}, item: {experiments[i].item}")
        exp_fn = fldrname + filename

        
        if os.path.exists(exp_fn): # Experiment is calculated before, do not recalculate
            experiments[i] = loadExperimentFromPickleFile(exp)
            continue
        
        if exp.ld_fldr and os.path.exists(exp.ld_fldr): # for a fair comparison remove LocalData
            try:
                shutil.rmtree(exp.ld_fldr)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))       

                
        if exp.svn[0] and getSvnVersion(exp) != exp.svn[1]: # svn revision should match
            print(f"Warning: cannot compute experiment {filename}, local svn copy revision: {getSvnVersion(exp)} does not match experiments revision: {exp.svn[1]}")
            continue

        # Sample performance
        if (not exp.cfg and not exp.item): # BATCH
            log_fn = exp.flags
            if os.path.exists(log_fn): # always start with empty log
                os.remove(log_fn)
            exp.result["log"],start_time = getPerformanceBatch(f"{exp.exe_fldr} {exp.flags}", sampling_rate)
            
        else: # RUN
            log_fn = f"{exp.storage_fldr}log{i}.txt"
            stat_fn = f"{exp.storage_fldr}stat{i}.txt"
            if os.path.exists(log_fn): # remove log
                os.remove(log_fn)
            if "GeoDmsCaller.exe" in exp.exe_fldr: # GUI
                exp.result["log"],start_time = getPerformanceGui(exp, log_fn, sampling_rate=1.0)
            else:
                cmd = f"start \"GeoDmsRun\" {exp.exe_fldr}{exe_name} /L{log_fn} {exp.flags} {exp.cfg} @file {stat_fn} @statistics {exp.item}"
                print(cmd)
                os.system(cmd)
                exp.result["log"],start_time,_ = getPerformance(exe_name, sampling_rate)

        # LOG
        if os.path.exists(log_fn):
            exp.result["cpu_percent"]    = getLogInfoForPlotting(exp.result["log"], log_fn, "cpu_percent")
            exp.result["cpu_curr_time"]  = getLogInfoForPlotting(exp.result["log"], log_fn, "cpu_curr_time")
            exp.result["memory_percent"] = getLogInfoForPlotting(exp.result["log"], log_fn, "memory_percent")
            exp.result["num_threads"]    = getLogInfoForPlotting(exp.result["log"], log_fn, "num_threads")
            exp.result["rss"]            = getLogInfoForPlotting(exp.result["log"], log_fn, "rss")
            exp.result["vms"]            = getLogInfoForPlotting(exp.result["log"], log_fn, "vms")
            exp.result["read_bytes"]     = getLogInfoForPlotting(exp.result["log"], log_fn, "read_bytes")
            exp.result["write_bytes"]    = getLogInfoForPlotting(exp.result["log"], log_fn, "write_bytes")
            exp.result["total_read_bytes"]     = getLogInfoForPlotting(exp.result["log"], log_fn, "total_read_bytes")
            exp.result["total_write_bytes"]    = getLogInfoForPlotting(exp.result["log"], log_fn, "total_write_bytes")

        # Get allocator state from log
        log_alloc = readLogAllocator(log_fn, start_time) # temporarily disable allocator logging
        if log_alloc:
            exp.result["log_alloc"] = log_alloc
        else: 
            exp.result["log_alloc"] = None
        
        # store experiment    
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
        if ii == 0:
            title = f"{experiments[0].cfg} {experiments[0].item}"
        else:
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
    
    output_fn = f"{experiments[0].storage_fldr}compare.html"
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
        return None
    cfg = None
    item = None
    storage_fldr = None
    
    experiments = []
    with open(fn, "r") as f:
        while (True):
            line = f.readline()
            if not line:
                break
            
            if "name;svn;exe_fldr;ld_fldr;flags;fullname" in line:
                continue
                
            if line[0] == "#": # comment
                continue
                
            if len(line) == 1: # empty line
                continue
            
            line_split   = line.split(";")
            
            if len(line_split) == 2: # general params
                if line_split[0] == "cfg":
                    cfg = line_split[1].replace("\n", "")
                elif line_split[0] == "item":
                    item = line_split[1].replace("\n", "")
                elif line_split[0] == "storage_fldr":
                    storage_fldr = line_split[1].replace("\n", "")
            else:
                name         = line_split[0]
                svn_split    = line_split[1].split(",")
                if len(svn_split) == 1:
                    svn = (None, None)
                else:
                    svn = (svn_split[0], svn_split[1])
                exe_fldr     = line_split[2]
                ld_fldr      = line_split[3]
                flags        = line_split[4]
                fullname     = line_split[5].replace("\n", "").replace("\t","").replace(" ","")
                
                if fullname and storage_fldr:
                    experiments.append((fullname,storage_fldr))
                elif fullname:
                    experiments.append(fullname)
                else:
                    experiments.append(Experiment(name=name, svn=svn, exe_fldr=exe_fldr, ld_fldr=ld_fldr, storage_fldr=storage_fldr, cfg=cfg, item=item, flags=flags))

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
        print(f"Unable to initialize experiments from csv file: {config_fn}")
        return
        
    # run 
    experiments = RunExperiments(experiments, sampling_rate)

    # check
    #if compareExperimentStatisticsFiles(experiments):
    #    print("Aborting..")
    #    return
    
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
    main()
    #RunTestConfig("C:\\prj\\tst\\Performance\\scripts\\experiments_Fast_test_batch.txt")
    #testReadLog()
    #testReadAllocatorInfoLog()
import os
import rrdtool
import datetime
import time

''' Make sure the relevant folders exist '''
data_folder = f"{os.path.dirname(os.path.realpath(__file__))}/rrd"
graphs_folder = f"{os.path.dirname(os.path.realpath(__file__))}/graphs"
if not os.path.exists(graphs_folder):
    os.makedirs(graphs_folder)

''' Set graph history, change "minutes = 20" to however long history the graph should display '''
end_time = datetime.datetime.now() - datetime.timedelta()
end_time = int(time.mktime(end_time.timetuple()))
start_time = datetime.datetime.now() - datetime.timedelta(hours = 8)
start_time = int(time.mktime(start_time.timetuple()))

''' Each step in the graph should be atleast 5 pixels or the graph becomes hard to interpret.
    Data is saved in 60 second increments, so that's the smallest possible step.
    A 1200 pixels wide graph can contain 240 steps maximum (1200/5=240), so the graph history can't be more than 240 minutes if it's going to look good
    A longer graph history requires a larger step size, for example a 5 hour history requires a 120 second step size. '''
graph_history = end_time - start_time
graph_width = 1200
maximum_steps = graph_width / 5
step_size = minimum_step = 60
while (graph_history / step_size) > maximum_steps:
    step_size += minimum_step

''' Create the graphs '''
data_files = os.listdir(data_folder)
for data_file in data_files:

    input_file = f"{data_folder}/{data_file}"
    image_file = data_file.replace(".rrd", "")

    ''' https://htmlcolors.com/color-chart '''
    for radio in ["2ghz", "5ghz"]:

        rrdtool.graph(f"{graphs_folder}/{image_file}-{radio}.png", 
            "--start", f"{start_time}",
            "--end", f"{end_time}",
            f"--title={image_file} statistics",
            "--height=450",
            f"--width={graph_width}",
            "--upper-limit=100",
            "--lower-limit=0",
            "COMMENT:                       Average           Max\l",
            f"DEF:clients-{radio}={input_file}:clients-{radio}:AVERAGE:step={step_size}", f"AREA:clients-{radio}#81c784:Clients", f"GPRINT:clients-{radio}:AVERAGE:%15.1lf%s", f"GPRINT:clients-{radio}:MAX:%14.1lf%s\l",
            f"DEF:bytes-tx-{radio}={input_file}:bytes-tx-{radio}:AVERAGE:step={step_size}", f"CDEF:megabits-tx-{radio}=bytes-tx-{radio},8,*,1000000,/", f"LINE:megabits-tx-{radio}#4fc3f7:Tx", f"GPRINT:megabits-tx-{radio}:AVERAGE:%21.1lf%s", f"GPRINT:megabits-tx-{radio}:MAX:%12.0lf%s\l",
            f"DEF:bytes-rx-{radio}={input_file}:bytes-rx-{radio}:AVERAGE:step={step_size}", f"CDEF:megabits-rx-{radio}=bytes-rx-{radio},8,*,1000000,/", f"LINE:megabits-rx-{radio}#4FF7D9:rx", f"GPRINT:megabits-rx-{radio}:AVERAGE:%21.1lf%s", f"GPRINT:megabits-rx-{radio}:MAX:%12.0lf%s\l",
            f"DEF:ch-util-{radio}={input_file}:ch-util-{radio}:AVERAGE:step={step_size}",               f"LINE2:ch-util-{radio}#d32f2f:Channel Utilization\l",
            f"DEF:interfering-ap-{radio}={input_file}:interfering-ap-{radio}:AVERAGE:step={step_size}", f"LINE2:interfering-ap-{radio}#5d4037:Interfering APs\l",
            f"DEF:tx-retries-{radio}={input_file}:tx-retries-{radio}:AVERAGE:step={step_size}",         f"LINE2:tx-retries-{radio}#fbc02d:TX retries %\l",
        )

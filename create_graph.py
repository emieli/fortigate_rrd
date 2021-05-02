import os
import rrdtool
import datetime
import time
import json

data_folder = f"{os.path.dirname(os.path.realpath(__file__))}/rrd"
graphs_folder = f"{os.path.dirname(os.path.realpath(__file__))}/graphs"
if not os.path.exists(graphs_folder):
    os.makedirs(graphs_folder)

end_time = datetime.datetime.now() - datetime.timedelta()
end_time = int(time.mktime(end_time.timetuple()))
start_time = datetime.datetime.now() - datetime.timedelta(days = 2)
start_time = int(time.mktime(start_time.timetuple()))

''' Each step in the graph should be atleast 5 pixels or the graph looks like shit 
    Data is saved in 60 second increments, so that's the smallest possible step.
    A 1200 pixels wide graph can contain 240 steps maximum (1200/5=240), so the graph history can't be more than 240 minutes if it's going to look good
    A longer graph history requires a larger step size, for example a 5 hour history requires a 120 step size. '''
graph_history = end_time - start_time
graph_width = 1200
maximum_steps = graph_width / 5
step_size = minimum_step = 60
while (graph_history / step_size) > maximum_steps:
    step_size += minimum_step

data_files = os.listdir(data_folder)
for data_file in data_files:

    input_file = f"{data_folder}/{data_file}"
    image_file = data_file.replace(".rrd", ".png")


    ''' Create the .png file and place it in the /static/ folder. '''
    rrdtool.graph(f"{graphs_folder}/{image_file}", 
        "--start", f"{start_time}",
        "--end", f"{end_time}",
        f"--title={data_file.replace('.rrd', '')} Channel Utilization",
        "--height=450",
        f"--width={graph_width}",
        "--upper-limit=100",
        "--lower-limit=0",
        "--vertical-label", "Percent",
        f"DEF:ch-util-2ghz-max={input_file}:ch-util-2ghz:MAX:step={step_size}",
        "LINE:ch-util-2ghz-max#A22615:2 ghz peak\l:dashes=4",
        f"DEF:ch-util-2ghz-avg={input_file}:ch-util-2ghz:AVERAGE:step={step_size}",
        "LINE2:ch-util-2ghz-avg#F26C52:2 ghz average\l",
        f"DEF:ch-util-5ghz-max={input_file}:ch-util-5ghz:MAX:step={step_size}",
        "LINE:ch-util-5ghz-max#003046:5 ghz peak\l:dashes=4",
        f"DEF:ch-util-5ghz-avg={input_file}:ch-util-5ghz:AVERAGE:step={step_size}",
        "LINE2:ch-util-5ghz-avg#006EB9:5 ghz average\l")

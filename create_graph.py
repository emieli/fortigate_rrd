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
start_time = datetime.datetime.now() - datetime.timedelta(minutes = 40)
start_time = int(time.mktime(start_time.timetuple()))

data_files = os.listdir(data_folder)
for data_file in data_files:

    input_file = f"{data_folder}/{data_file}"
    image_file = data_file.replace(".rrd", ".png")

    ''' Create the .png file and place it in the /static/ folder. '''
    rrdtool.graph(f"{graphs_folder}/{image_file}", 
        "--start", f"{start_time}",
        "--end", f"{end_time}",
        f"--title={data_file.replace('.rrd', '')} Channel Utilization",
        "--height=300",
        "--width=900",
        "--upper-limit=100",
        "--lower-limit=0",
        f"DEF:ch-util-2ghz-max={input_file}:ch-util-2ghz:MAX",
        "LINE:ch-util-2ghz-max#A22615:2.4 ghz max%:dashes=4",
        f"DEF:ch-util-2ghz-avg={input_file}:ch-util-2ghz:AVERAGE",
        "LINE2:ch-util-2ghz-avg#F26C52:2.4 ghz avg%",
        f"DEF:ch-util-5ghz-max={input_file}:ch-util-5ghz:MAX",
        "LINE:ch-util-5ghz-max#003046:5 ghz max%:dashes=4",
        f"DEF:ch-util-5ghz-avg={input_file}:ch-util-5ghz:AVERAGE",
        "LINE2:ch-util-5ghz-avg#006EB9:5 ghz avg%")

import os
import rrdtool
import datetime
import time

data_folder = f"{os.path.dirname(os.path.realpath(__file__))}/rrd_data"
images_folder = f"{os.path.dirname(os.path.realpath(__file__))}/images"
data_files = os.listdir(data_folder)

end_time = datetime.datetime.now()
start_time = datetime.datetime.now() - datetime.timedelta(minutes = 120)

for data_file in data_files:
    
    input_file = f"{data_folder}/{data_file}"
    image_file = data_file.replace(".rrd", ".png")

    ''' Create the .png file and place it in the /static/ folder. '''
    rrdtool.graph(f"{images_folder}/{image_file}", 
        "--start", f"{int(time.mktime(start_time.timetuple()))}",
        "--end", f"{int(time.mktime(end_time.timetuple()))}",
        f"--title={data_file.replace('.rrd', '')} Channel Utilization",
        "--height=150",
        "--width=470",
        "--upper-limit=100",
        f"DEF:ch-util-2ghz={input_file}:ch-util-2ghz:MAX",
        "LINE:ch-util-2ghz#c334eb:2.4 ghz %",
        f"DEF:ch-util-5ghz={input_file}:ch-util-5ghz:MAX",
        "LINE:ch-util-5ghz#f59c42:5 ghz %")

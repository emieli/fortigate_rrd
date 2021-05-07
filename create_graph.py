import os
import rrdtool
import datetime
import time

''' Make sure the relevant folders exist '''
data_folder = f"{os.path.dirname(os.path.realpath(__file__))}/rrd"
data_files = os.listdir(data_folder)
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
graph_width = 1930
maximum_steps = graph_width / 2
step_size = minimum_step = 60
while (graph_history / step_size) > maximum_steps:
    step_size += minimum_step
print(f"step: {step_size}")

''' Create interfering APs summary graph '''
for radio in ["2ghz", "5ghz"]:
    graph_data = [f"{graphs_folder}/interfering-ap-{radio}.png", 
                "--start", f"{start_time}",
                "--end", f"{end_time}",
                f"--title=Interfering AP statistics",
                "--height=300",
                f"--width={graph_width}",
                "--font=LEGEND:9:Consolas",
                "--dynamic-labels",
                "AREA:0",
                "TEXTALIGN:left",
                ]

    hex_colors = ["d50000", "aa00ff", "6200ea", "304ffe", "0091ea", "00b8d4", "00c853", "64dd17", "aeea00", "ffd600", "ff6d00", "dd2c00", "212121", "607d8b", "1b5e20"]
    color_index = -1
    data_files.sort()
    for i in range(len(data_files)):
        color_index += 1

        if i == len(hex_colors):
            color_index = 0
        
        data_file = data_files[i]
        input_file = f"{data_folder}/{data_file}"
        ap_name = data_file.split(".")[0]

        graph_data.append(f"DEF:{ap_name}-interfering-ap-{radio}={input_file}:interfering-ap-{radio}:AVERAGE:step={step_size}")
        graph_data.append(f"STACK:{ap_name}-interfering-ap-{radio}#{hex_colors[color_index]}:{ap_name}")
        graph_data.append(f"GPRINT:{ap_name}-interfering-ap-{radio}:AVERAGE:(avg %2.0lf\g")
        graph_data.append(f"GPRINT:{ap_name}-interfering-ap-{radio}:MAX:, max %2.0lf)")

    rrdtool.graph(graph_data)
quit()

''' Create the graphs '''
for data_file in data_files:

    input_file = f"{data_folder}/{data_file}"
    ap_name = data_file.replace(".rrd", "")

    ''' https://htmlcolors.com/color-chart '''
    for radio in ["2ghz", "5ghz"]:

        rrdtool.graph(f"{graphs_folder}/{ap_name}-{radio}.png", 
            "--start", f"{start_time}",
            "--end", f"{end_time}",
            f"--title={ap_name} statistics",
            "--height=500",
            f"--width={graph_width}",
            "--upper-limit=100",
            "--lower-limit=0",
            "--font=LEGEND:9:Consolas",
            "--dynamic-labels",
            "COMMENT:            Average     Max \l",
            f"DEF:clients-{radio}={input_file}:clients-{radio}:AVERAGE:step={step_size}",   f"AREA:clients-{radio}#00c853:Clients #", f"GPRINT:clients-{radio}:AVERAGE:%6.0lf", f"GPRINT:clients-{radio}:MAX:%6.0lf\l",
            f"DEF:bytes-tx-{radio}={input_file}:bytes-tx-{radio}:AVERAGE:step={step_size}", f"CDEF:megabits-tx-{radio}=bytes-tx-{radio},8,*,1000000,/", f"AREA:megabits-tx-{radio}#00b0ff99:Tx Mbps  ", f"GPRINT:megabits-tx-{radio}:AVERAGE:%6.0lf", f"GPRINT:megabits-tx-{radio}:MAX:%6.0lf\l",
            f"DEF:bytes-rx-{radio}={input_file}:bytes-rx-{radio}:AVERAGE:step={step_size}", f"CDEF:megabits-rx-{radio}=bytes-rx-{radio},8,*,1000000,/", f"AREA:megabits-rx-{radio}#18ffff99:Rx Mbps  ", f"GPRINT:megabits-rx-{radio}:AVERAGE:%6.0lf", f"GPRINT:megabits-rx-{radio}:MAX:%6.0lf\l",
            f"DEF:interfering-ap-{radio}={input_file}:interfering-ap-{radio}:AVERAGE:step={step_size}", f"LINE1.3:interfering-ap-{radio}#5d4037:Intf AP #", f"GPRINT:interfering-ap-{radio}:AVERAGE:%6.0lf", f"GPRINT:interfering-ap-{radio}:MAX:%6.0lf\l",
            f"DEF:ch-util-{radio}={input_file}:ch-util-{radio}:AVERAGE:step={step_size}", f"LINE1.3:ch-util-{radio}#b71c1c:Ch Util %", f"GPRINT:ch-util-{radio}:AVERAGE:%6.0lf", f"GPRINT:ch-util-{radio}:MAX:%6.0lf\l",
            # f"DEF:tx-retries-{radio}={input_file}:tx-retries-{radio}:AVERAGE:step={step_size}", f"LINE2:tx-retries-{radio}#e68f05:TX retr %", f"GPRINT:tx-retries-{radio}:AVERAGE:%6.0lf", f"GPRINT:tx-retries-{radio}:MAX:%6.0lf\l",
            # f"DEF:antenna-rssi-{radio}={input_file}:antenna-rssi-{radio}:AVERAGE:step={step_size}", f"LINE2:antenna-rssi-{radio}#afb42b:AP RSSI  ", f"GPRINT:antenna-rssi-{radio}:AVERAGE:%6.0lf", f"GPRINT:antenna-rssi-{radio}:MAX:%6.0lf\l",
            "--rigid",
            # "LINE:100#000",             
        )

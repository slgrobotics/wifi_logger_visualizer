# AI generated: 
# Below is an example of Python code using the matplotlib and seaborn libraries to generate a heatmap
#
# not to be confused with Heatmapper Node, ../wifi_logger_visualizer/heat_mapper_node.py
#
# Prerequisites:
#     sudo apt install python3-scipy python3-seaborn wireless-tools sqlite3
#
# Run it:
#     cd ~/robot_ws/src/wifi_logger_visualizer/wifi_heat_mapper
#     python3 heat_mapper.py
#

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math
import sqlite3

db_path = '../database/wifi_data.db'

scale_factor = 1 # map scale, larger value causes finer grid

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT x,y,bit_rate,link_quality,lat FROM wifi_data")
    #cursor.execute("SELECT * FROM wifi_data")
    #cursor.execute("SELECT count(*) FROM wifi_data")
    rows = np.array(cursor.fetchall())
    #rows = np.round(rows, decimals=1) * scale_factor

    conn.close()
    row_count = len(rows)
    #row_count = rows

    print(f"Number of rows: {row_count}")
    print(f"Row 0: {rows[0]}")
    print(f"Row 0 [0] = x: {rows[0][0]}")
    print(f"Row 0 [1] = y: {rows[0][1]}")
    print(f"Row 0 [2] = bit_rate: {rows[0][2]}")
    print(f"Row 0 [3] = link_quality: {rows[0][3]}")
    print(f"Row 0 [4] = signal_level: {rows[0][4]}")

    min_arr = np.min(rows, axis=0)
    min_x = math.floor(min_arr[0])
    min_y = math.floor(min_arr[1])

    max_arr = np.max(rows, axis=0)
    max_x = math.ceil(max_arr[0])
    max_y = math.ceil(max_arr[1])

    print(f"min: {min}")
    print(f"max: {max}")
    
    print(f"min_x: {min_x}  max_x: {max_x}")
    print(f"min_y: {min_y}  max_y: {max_y}")

    # dimensions of the drawing space:
    dim_x = int(math.ceil(max_x)) - int(math.floor(min_x)) + 3
    dim_y = int(math.ceil(max_y)) - int(math.floor(min_y)) + 3
    print(f"drawing space: dim_x: {dim_x}  dim_y: {dim_y}")

    heat_data = np.zeros((dim_y, dim_x)) # somehow x and y are inverted when drawing heatmap

    hd_min = +1000.0
    hd_max = -1000.0
    
    for y in range(dim_y):
        for x in range(dim_x):
            heat_data[y][x] = None # comment this out to see zeroes instead of white space
            records_cnt = 0 # how many records in the database refer to this grid cell
            hd_avg = 0.0
            for row in rows:
                # find data_x and data_y in rows matching our position (x,y) in drawing space:
                data_x = int(round(row[0]-min_x))+1
                data_y = int(round(row[1]-min_y))+1
                if data_x==x and data_y==y:
                    records_cnt += 1
                    hd_val = row[4] / scale_factor # signal_level=4; scale it back, round down
                    hd_avg += hd_val
                    hd_min = min(hd_min, hd_val)
                    hd_max = max(hd_max, hd_val)
                    heat_data[y][x] = hd_val
                    #heat_data[y][x] = records_cnt
                    #print(f"{data_x} {data_y}   {x} {y} {heat_data[y][x]}  records_cnt: {records_cnt}")
            if records_cnt > 0:
                hd_avg /= records_cnt
                print(f"{x} {y} avg: {hd_avg}  records_cnt: {records_cnt}")
        print(f"---- end Y {y}")

except sqlite3.Error as e:
    print(f"Error: retrieving wifi data: {e}")

bg_color = np.array([0.55, 0.8, 0.75, 0.1]) # RGBA value
grid_color = np.array([0.2, 0.2, 1.0, 0.05])

# Create the heatmap
ax = sns.heatmap(heat_data, annot=True, cmap='coolwarm',  fmt=".6f",
                 linewidths=0.2, linecolor=grid_color, clip_on=False) #, vmin=hd_min, vmax=hd_max)
# https://seaborn.pydata.org/tutorial/color_palettes.html
#ax.set_facecolor('lightgrey')
ax.set_facecolor(bg_color)
ax.invert_yaxis()

labels_x = np.arange(min_x, max_x+2, 1)
labels_x = np.insert(labels_x, 0, labels_x[0]-1)
labels_y = np.arange(min_y, max_y+2, 1)
labels_y = np.insert(labels_y, 0, labels_y[0]-1)

# Set x-axis labels
ax.set_xticks(np.arange(len(labels_x)) + 0.5) # Center labels on ticks
ax.set_xticklabels(labels_x)

# Set y-axis labels
ax.set_yticks(np.arange(len(labels_y)) + 0.5)
ax.set_yticklabels(labels_y)

# Set the x and y axis limits:
#ax.set_xlim(min_x, max_x)
#ax.set_ylim(min_y, max_y)

# Customize the plot (optional)
plt.title('WiFi Signal Strength Heatmap')
plt.xlabel('X-axis Travel (positive: East)')
plt.ylabel('Y-axis Travel (positive: North)')
plt.xticks(rotation=0) # horizontal
plt.yticks(rotation=0)

# Display the heatmap
plt.show()


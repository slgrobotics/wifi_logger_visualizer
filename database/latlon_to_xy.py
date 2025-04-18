# 
# A utility to convert lat,lon fields to x,y coordinates and fill those in the database
# Used when x,y (odometry supplied) have been zeroed while restarting ROS.
#
# Run it:
#     cd ~/robot_ws/src/wifi_logger_visualizer/database
#     python3 latlon_to_xy.py
#

import matplotlib.pyplot as plt
import numpy as np
import math
import sqlite3

from math import radians, cos, sin, asin, sqrt

def distance(lat1, lat2, lon1, lon2):
     
    # https://www.geeksforgeeks.org/program-distance-two-points-earth/

    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a)) 
    
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371.01
      
    # calculate the result
    return(c * r * 1000.0) # meters
     
db_path = 'wifi_data.db'

try:
    #
    # first, delete rows that cannot be converted:
    #
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM wifi_data WHERE lat IS NULL or lon IS NULL")
    except sqlite3.Error as e:
        print(f"Error: deleting wifi data with null lat or lon: {e}")

    print("IP: committing changes to database...")
    conn.commit()
    conn.close()

    #
    # now we can do the conversion:
    #
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT count(*) FROM wifi_data")
    row_count = int(cursor.fetchall()[0][0])
    print(f"rows count: {row_count}")

    cursor.execute("SELECT min(lat),min(lon),max(lat),max(lon) FROM wifi_data")
    rows = np.array(cursor.fetchall())
    min_lat = rows[0][0]
    min_lon = rows[0][1]
    max_lat = rows[0][2]
    max_lon = rows[0][3]
    print(f"Min LAT: {min_lat}  LON: {min_lon}")
    print(f"Max LAT: {max_lat}  LON: {max_lon}")

    width = round(distance(min_lat, min_lat, min_lon, max_lon), 1)
    height = round(distance(min_lat, max_lat, min_lon, min_lon), 1)
    print(f"Area Width (x or west-east): {width}  Height (y or south-north): {height} meters")

    cursor.execute("SELECT id,lat,lon FROM wifi_data")
    rows = np.array(cursor.fetchall())

    for row in rows:
        id = int(row[0])
        lat = row[1]
        lon = row[2]

        if lat is None or lon is None:
            print("Warning: Deleting row with lon/lat missing")
            try:
                cursor.execute("DELETE FROM wifi_data WHERE id=?", (id,)) # passing id as a tuple
            except sqlite3.Error as e:
                print(f"Error: deleting wifi data: {e}")
        else:
            x = distance(lat, lat, min_lon, lon)
            y = distance(min_lat, lat, lon, lon)
            #print(f"id: {id}  LAT: {lat}  LON: {lon}  X: {x}  Y: {y}")
            try:
                cursor.execute(f"UPDATE wifi_data SET x={x},y={y} WHERE id={id}")
            except sqlite3.Error as e:
                print(f"Error: updating wifi data: {e}")

    print("IP: committing changes to database...")
    conn.commit()
    conn.close()
    print("OK: Done")

except sqlite3.Error as e:
    print(f"Error: retrieving wifi data: {e}")

    exit()

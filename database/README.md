## sqlite3 Database installation

https://linuxcapable.com/how-to-install-sqlite-on-ubuntu-linux/

I am using Ubuntu 24.04 on Intel Desktops and Raspberry Pi 4 and 5
```
sudo apt install sqlite3
sqlite3 --version
```

Usage and general info:
- https://www.sqlite.org/quickstart.html
- https://github.com/sqlite/sqlite
- https://www.sqlite.org/
- https://github.com/wimblerobotics/Sigyn/blob/main/Documentation/Notes/wifi_signal.md

The ```wifi_data.db``` database file is created in the current directory when you run Logger node:
```
ros2 launch wifi_logger_visualizer wifi_logger.launch.py
```

Simple commands (note the semicolon at the end):
```
~/wimble_ws/src/Sigyn/wifi_signal_visualizer$ sqlite3 ../wifi_data.db
   SQLite version 3.45.1 2024-01-30 16:01:20
Enter ".help" for usage hints.

sqlite> .headers ON
sqlite> select count(*) from wifi_data;
count(*)
282

sqlite> SELECT * from wifi_data LIMIT 2;
id|timestamp|x|y|lat|lon|gps_status|gps_service|bit_rate|link_quality|signal_level
1|2025-04-11 16:44:55|6.7|-0.4|33.9521889999925|-105.331214000035|2|0|390.0|0.771428571428571|-56.0
2|2025-04-11 16:44:53|6.6|-0.4|33.9521895297565|-105.331215287443|2|0|390.0|0.757142857142857|-57.0

sqlite> .tables
wifi_data
sqlite> .schema wifi_data
CREATE TABLE wifi_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    lat REAL NULL,
                    lon REAL NULL,
                    gps_status INT NULL,
                    gps_service INT NULL,
                    bit_rate REAL CHECK (bit_rate >= 0),
                    link_quality REAL CHECK (link_quality >= 0 AND link_quality <= 1),
                    signal_level REAL CHECK (signal_level >= -90.0 AND signal_level <= -30.0),
                    UNIQUE(x, y, timestamp)
                );
CREATE INDEX idx_timestamp ON wifi_data(timestamp);
CREATE INDEX idx_coordinates ON wifi_data(x, y);
sqlite> 
```
## Working with GPS data

When outdoors, a robot can use GNSS ("_NavSatFix_" type, "/gps/filtered" or "/gps/fix" topic) and the *WiFi Logger* should collect that data.
It is possible that _odometry_-derived data in the database (_x,y_ fields) becomes less reliable than accumulated GNSS coordinates (this happens, for example, when robot nodes are restarted and odometry is zeroed out).

*latlon_to_xy.py* utility converts _lat,lon_ fields to relative _x,y_ coordinates and fills (updates) those in the database, overwriting the _x_ and _y_ fields.

**Note:**
- Please make a backup of your original database before running this utility.
- The utility will delete all records *WHERE lat IS NULL or lon IS NULL*
- The utility will update/overwrite the _x_ and _y_ fields.

Once the conversion is finished, _Heat Mapper_ can be run and will display the grid based on relative distance - meters from (_min(lat),min(lon)_) coordinates:

![Screenshot from 2025-04-18 12-20-47](https://github.com/user-attachments/assets/ccea20db-d2f2-4142-a6a2-9e3618da05ff)

![Screenshot from 2025-04-18 12-23-54](https://github.com/user-attachments/assets/cd1e64e3-a849-4a26-a658-b80fd8f0dda8)


----------------

**Back to** [Main Page](https://github.com/slgrobotics/wifi_logger_visualizer)

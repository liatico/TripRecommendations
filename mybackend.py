import sqlite3
import os.path
from pathlib import Path
import pandas as pd
from itertools import islice

class Database:

    def __init__(self):
        if not os.path.isfile('database.db'):
            # create database file
            Path('database.db').touch()
            # load csv file
            self.load_csv_file(sqlite3.connect('database.db'),'BikeShare.csv')
        self.conn = None

    @property
    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect('database.db')
        return self.conn

    @property
    def cursor(self):
        if self.conn is None:
            return self.connect.cursor()
        else:
            return self.conn.cursor()

    def load_csv_file(self, conn, csv_path):
        self.cursor.execute('''CREATE TABLE BikeShare (TripDuration int, StartTime timestamp, StopTime timestamp,
                                       StartStationID int, StartStationName text, StartStationLatitude real,
                                        StartStationLongitude real, EndStationID int, EndStationName text,
                                        EndStationLatitude real, EndStationLongitude real, BikeID int,
                                        UserType text, BirthYear int, Gender int, TripDurationinmin int)''')
        csv_data = pd.read_csv(csv_path)
        csv_data.to_sql('BikeShare', conn, if_exists='append', index=False)
        self.conn.close()

    # insert query
    def insert_new_entry(self,trip_duration, start_time, stop_time,
                                       start_station_id, start_station_name, start_station_latitude,
                                        start_station_longitude, end_station_id, end_station_name,
                                        end_station_latitude, end_station_longitude, bike_id,
                                        user_type, birth_year, gender, trip_duration_in_min):
        try:
            values = [(trip_duration,start_time, stop_time,
                                           start_station_id, start_station_name, start_station_latitude,
                                            start_station_longitude, end_station_id, end_station_name,
                                            end_station_latitude, end_station_longitude, bike_id,
                                            user_type, birth_year, gender, trip_duration_in_min)]

            query = '''INSERT INTO BikeShare (TripDuration, StartTime, StopTime,StartStationID, StartStationName, StartStationLatitude,
                        StartStationLongitude, EndStationID, EndStationName,EndStationLatitude, EndStationLongitude, BikeID,
                        UserType, BirthYear, Gender, TripDurationinmin) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            self.cursor.executemany(query, values)
            self.conn.close()
        except ConnectionError:
            print(ConnectionError.strerror)
        

    # select query
    def search(self, start_location, time_duration, k):
        query = """SELECT * FROM BikeShare WHERE StartStationName =? AND TripDuration<=?"""
        values = [start_location, time_duration]
        results = self.cursor.execute(query, values)
        self.conn.close()
        return self.pick_best_k(results, k)

    def pick_best_k(self,results, k):
        # count how many times the destination is retreved and rank accordingly
        # return best k
        destination = {}
        for res in results:
            dest = res[8]
            if not dest in destination.keys():
                destination[dest] = 1
            else:
                destination[dest] += 1
        destination = dict(sorted(destination.items(), key=lambda item: item[1],reverse=True))
        best_k = list(islice(destination.items(), k))
        best_k_list = []
        for item in best_k:
            best_k_list.append(item[0])
        return best_k_list




if __name__ == '__main__':
    db = Database()
    # c = db.cursor
    # print(c.execute('''SELECT * FROM BikeShare''').fetchall())
    # db.insert_new_entry(649,'31/03/2017 23:25',	'31/03/2017 23:36',	3185, 'City Hall', 40.7177325, -74.043845, 3190, 'Garfield Ave Station', 40.71046702, -74.0700388, 26200, 'Subscriber',1988,1,11)
    print(db.search('Christ Hospital', 376, 6))
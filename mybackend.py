import sqlite3
import os.path
from pathlib import Path
import pandas as pd
from itertools import islice

class Database:

    # constructor for database, if not exists creates database file and load bike csv to it
    def __init__(self):
        try:
            if not os.path.isfile('database.db'):
                # create database file
                Path('database.db').touch()
                # load csv file
                self.load_csv_file(sqlite3.connect('database.db'),'BikeShare.csv')
        except FileNotFoundError:
            print("csv file not found")
        self.conn = sqlite3.connect('database.db')

    # get connection property
    @property
    def connect(self):
        self.conn = sqlite3.connect('database.db')
        return self.conn

    # get cursor property to run queries
    @property
    def cursor(self):
        return self.connect.cursor()

    # loads csv file into the database
    def load_csv_file(self, conn, csv_path):
        try:
            self.cursor.execute('''CREATE TABLE BikeShare (TripDuration int, StartTime timestamp, StopTime timestamp,
                                           StartStationID int, StartStationName text, StartStationLatitude real,
                                            StartStationLongitude real, EndStationID int, EndStationName text,
                                            EndStationLatitude real, EndStationLongitude real, BikeID int,
                                            UserType text, BirthYear int, Gender int, TripDurationinmin int)''')
            csv_data = pd.read_csv(csv_path)
            csv_data.to_sql('BikeShare', conn, if_exists='append', index=False)
            conn.commit()
        except ConnectionError:
            print("can't connect to database")

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
            self.conn.commit()
        except ConnectionError:
            print(ConnectionError.strerror)

    # search query
    def search(self, start_location, time_duration, k, for_gui=False):
        try:
            query = """SELECT EndStationName,TripDurationinmin FROM BikeShare WHERE StartStationName =? AND TripDurationinmin <=?"""
            values = [start_location, time_duration]
            results = self.cursor.execute(query, values)
            self.conn.commit()
        except ConnectionError:
            print("can't connect to database")
            return [-1]
        # count how many times the destination is retrieved and rank accordingly
        # return best k
        if results:
            ranked_results = self.rank(results)
            best_k = list(islice(ranked_results.items(), int(k)))
            if for_gui:
                return best_k
            return self.pick_best_k(best_k)


    # cuts the list of results to return only location's name
    def pick_best_k(self,best_k):
        best_k_list = []
        for item in best_k:
            best_k_list.append(item[0])
        return best_k_list

    # adds to the list of results the number of time this destination came back
    # and the duration of the trip and ranks it accordingly
    def rank(self, results):
        destination = {}
        for res in results:
            dest = res[0]
            duration_in_min = res[-1]
            if not dest in destination.keys():
                destination[dest] = [duration_in_min, 1]
            else:
                destination[dest][1] += 1
        return dict(sorted(destination.items(), key=lambda item: item[1][1], reverse=True))

# for tests
if __name__ == '__main__':
    db = Database()
    # c = db.cursor
    # print(c.execute('''SELECT * FROM BikeShare''').fetchall())
    # db.insert_new_entry(649,'31/03/2017 23:25',	'31/03/2017 23:36',	3185, 'City Hall', 40.7177325, -74.043845, 3190, 'Garfield Ave Station', 40.71046702, -74.0700388, 26200, 'Subscriber',1988,1,11)
    print(db.search('Christ Hospital', 6, 3, True))
"""
Manager class to handle database interactions.
"""

import os
import sqlite3

DB_FILENAME = "oddsportal.db"

class DatabaseManager():

    def __init__(self, is_first_run):
        """
        Constructor.

        Args:
            is_first_run (bool): Is this the first DatabaseManager
                created in this run?
        """

        if is_first_run:
            try:
                os.remove(DB_FILENAME)
            except OSError:
                pass
        self.conn = sqlite3.connect(DB_FILENAME)
        self.cursor = self.conn.cursor()
        if is_first_run:
            self.cursor.execute('''DROP TABLE IF EXISTS surebets''')
            self.cursor.execute('''CREATE TABLE surebets
                                    (country text, league text, season text,
                                     start_time text, start_time_unix integer,
                                     score text, team1 text,
                                     team2 text, bookmaker text,
                                     odd_type text, odd float,
                                     odd_time text, odd_time_unix integer,
                                     retrieved_from_url text)''')
            self.conn.commit()
            self.cursor.execute('''DROP TABLE IF EXISTS dropodds''')
            self.cursor.execute('''CREATE TABLE dropodds
                                    (country text, league text, season text,
                                     start_time text, start_time_unix integer,
                                     score text, team1 text,
                                     team2 text, bookmaker text,
                                     start_1 float, start_x float, start_2 float,
                                     final_1 float, final_x float, final_2 float,
                                     drop_1 float, drop_x float, drop_2 float,
                                     retrieved_from_url text)''')
            self.conn.commit()


    def add_dropodds(self,country, league, season, current_date_str, current_date_unix, score,team1,team2,book,
    quota1Iniziale,quotaXIniziale,quota2Iniziale,quota1Finale,quotaXFinale,quota2Finale,drop1,dropX,drop2,url):
        sql_str = "INSERT INTO dropodds VALUES ('"
        sql_str += country + "', '"
        sql_str += league + "', '"
        sql_str += season + "', '"
        sql_str += current_date_str + "', "
        sql_str += current_date_unix + ", '"
        sql_str += score + "', '"
        sql_str += team1 + "', '"
        sql_str += team2 + "', '"
        sql_str += book + "', "
        sql_str += quota1Iniziale + ","
        sql_str += quotaXIniziale + ","
        sql_str += quota2Iniziale + ","
        sql_str += quota1Finale+ ","
        sql_str += quotaXFinale + ","
        sql_str += quota2Finale + ","
        sql_str += drop1 + ","
        sql_str += dropX + ","
        sql_str += drop2 + ", '"
        sql_str += url + "')"

        #print(sql_str)
        self.cursor.execute(sql_str)
        self.conn.commit()


    def add_surebet(self,country, league, season, start_time, start_time_unix, score, team1,
     team2, bookmaker,odd_type, odd, odd_time, odd_time_unix, retrieved_from_url):
        sql_str = "INSERT INTO surebets VALUES ('"
        sql_str += country + "', '"
        sql_str += league + "', '"
        sql_str += season + "', '"
        sql_str += start_time + "', "
        sql_str += start_time_unix + ", '"
        sql_str += score + "', '"
        sql_str += team1 + "', '"
        sql_str += team2 + "', '"
        sql_str += bookmaker + "', '"
        sql_str += odd_type + "', "
        sql_str += odd + ", '"
        sql_str += odd_time + "', "
        sql_str += odd_time_unix + ", '"
        sql_str += retrieved_from_url + "')"

        #print(sql_str)
        self.cursor.execute(sql_str)
        self.conn.commit()

    def __del__(self):
        """
        Destructor.
        """

        self.conn.close()

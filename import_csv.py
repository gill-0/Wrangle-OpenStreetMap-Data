#!/usr/bin/python
# -*- encoding: utf-8-*-

import sqlite3
import csv
from pprint import pprint
import os
#not sure if grader plans on running code. If so the db file will have to be changed
#as the instructions did not say to include it in submisson.
db = os.path.join(os.getcwd(), "sqlite_windows/madison.db")

con = sqlite3.connect(db)
cur = con.cursor()

'''
Inserts csv files into tables in a database
'''


def insert_nodes_tags():
    with open('nodes_tags.csv','rb') as fin:
        dr = csv.DictReader(fin) # comma is default delimiter
        to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"),i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in dr]
    cur.executemany("INSERT INTO nodes_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)
    con.commit()


def insert_nodes():
    with open('nodes.csv','rb') as fin:
        dr = csv.DictReader(fin) # comma is default delimiter
        to_db = [(i['id'].decode("utf-8"), i['lat'].decode("utf-8"), i['lon'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) for i in dr]
    cur.executemany("INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
    con.commit()

def insert_ways_tags():
    with open('ways_tags.csv','rb') as fin:
        dr = csv.DictReader(fin) # comma is default delimiter
        to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"), i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in dr]
    cur.executemany("INSERT INTO ways_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)
    con.commit()


def insert_ways():
    with open('ways.csv','rb') as fin:
        dr = csv.DictReader(fin) # comma is default delimiter
        to_db = [(i['id'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) for i in dr]
    cur.executemany("INSERT INTO ways(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)
    con.commit()

def insert_ways_nodes():
    with open('ways_nodes.csv','rb') as fin:
        dr = csv.DictReader(fin) # comma is default delimiter
        to_db = [(i['id'].decode("utf-8"), i['node_id'].decode("utf-8"), i['position'].decode("utf-8")) for i in dr]
    cur.executemany("INSERT INTO ways_nodes(id, node_id, position) VALUES (?, ?, ?);", to_db)
    con.commit()



insert_nodes_tags()
insert_nodes()
insert_ways_tags()
insert_ways()
insert_ways_nodes()
con.close()

'''
cur.execute('SELECT * FROM nodes_tags LIMIT 5')
all_rows = cur.fetchall()
print('1):')
pprint(all_rows)
'''
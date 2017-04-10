#!/usr/bin/python
# -*- encoding: utf-8-*-

import sqlite3
import csv
from pprint import pprint
import os
import matplotlib.pyplot as plt
import seaborn as sns
import re

tables = ['nodes', 'nodes_tags', 'ways', 'ways_tags', 'ways_nodes']
files = ['nodes_tags.csv', 'nodes.csv','ways_tags.csv', 'ways.csv', 'ways_nodes.csv', 'sqlite_windows/madison.db', 'madison.osm']

def user_percentage(cut_off):
    #Input: Number of nodes edited
    #Output: the percentage of users that less than/greater that have edited
    # the number of cutoff nodes and the percentage of nodes they have edited out
    # the total number of nodes
    users = cur.execute(query_users)
    user_counts = []
    made_cut = []
    count = 0
    for x in users:
        user_counts.append(x[1])
        if x[1] > cut_off:
            count += 1
            made_cut.append(x[1])
    total_count = len(user_counts)
    total_sum = sum(user_counts)
    sub_sum = sum(made_cut)

    count_percent = float(count)/ total_count *100
    sum_percent = float(sub_sum)/ total_sum *100
    return count_percent, sum_percent

def get_file_size(files):
    #Input: List of Files
    #Output: The names of files and thier file sizes in KB
 for file in files:
    file_path = os.path.join(os.getcwd(), file)
    print file + ':', (os.stat(file_path).st_size / 1000), "KB"

def delete_all(tables):
    #Input: list of tables in a database
    #Output: Deletes all tables.
    for table in tables:
        query = 'DELETE FROM {}'.format(table)
        cur.execute(query)
        con.commit()



def update_postcode(query_postcode):
    #Input: Query to find all post_codes
    #Output: Fixes al problematic zips in database that are in the nodes and ways tags.
    #Example WI 53707 --> 53707
    # 53707--5221 --> 53707
    nine_zip = re.compile(r'(\d{5})-\d{4}', re.IGNORECASE)
    state_zip = re.compile(r'\S+\s(\d{5})', re.IGNORECASE)
    cur.execute(query_postcode)
    zips = cur.fetchall()
    for zipp in zips:
        new_zip = ''
        m1 = re.findall(nine_zip, zipp[0])
        m2 = re.findall(state_zip, zipp[0])
        if m1:
            new_zip = m1[0]
        elif m2:
            new_zip = m2[0]
        if new_zip:
            new_zip = str(new_zip).encode("utf-8")
            print zipp, '---',new_zip
            cur.execute('UPDATE nodes_tags SET value = ? WHERE (value = ?  and key = "postcode")', (new_zip, zipp[0]))
            cur.execute('UPDATE ways_tags SET value = ? WHERE (value = ?  and key ="postcode");', (new_zip, zipp[0]))
            con.commit()





query_users = '''SELECT c.user, count(*) as num
                FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) c
                GROUP BY c.user
                ORDER BY num DESC
'''
                #HAVING num > 1000

query_postcode = '''SELECT zip.value, count(*) as count
                    FROM
                    (SELECT value, key FROM nodes_tags
                    WHERE key = 'postcode' UNION ALL
                    SELECT value, key FROM ways_tags
                    WHERE key = 'postcode') zip
                    GROUP BY zip.value
                    ORDER by count DESC
'''

query_unique= '''SELECT count(DISTINCT(c.user)) as num
                FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) c
'''


query_users_way = '''SELECT user, count(*) as num
                FROM ways
                GROUP BY user
                ORDER BY num DESC
'''

query_clean_street = 'SELECT key, value FROM nodes_tags WHERE (key = "street" and value LIKE "%St%")'

db = os.path.join(os.getcwd(), "sqlite_windows/madison.db")
con = sqlite3.connect(db)
cur = con.cursor()

#update_postcode(query_postcode)
#cur.execute('DROP TABLE IF EXISTS nodes_tags')
#conn.commit()

'''
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
'''
edits = 1000
count_percent, sum_percent =  user_percentage(edits)
print "{} percent of users have edited {} {} nodes or ways and account for about {} percent of the work done.".format(count_percent, 'greater than',  edits, int(sum_percent + .5))
#get_file_size(files)
#cur.execute(query_postcode)
answer = cur.fetchall()
pprint(answer)
con.close()
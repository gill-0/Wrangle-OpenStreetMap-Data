#!/usr/bin/python
# -*- encoding: utf-8-*-

import sqlite3
import csv
from pprint import pprint
import os

#queries used for database
#will need to change db if an


query_key = 'SELECT key, count(*) as num FROM nodes_tags GROUP BY key ORDER BY num DESC'

query_amenity = '''SELECT value, count(*) num FROM nodes_tags
                WHERE key = "amenity"
                GROUP BY value
                HAVING num >= 25
                ORDER BY num DESC
'''


query_food = '''SELECT * FROM nodes_tags
                WHERE key = "amenity" AND (value ="restaurant" OR value = "fast_food")
                '''


query_food_count = '''SELECT count(*) as num FROM nodes_tags
                WHERE  (value ="restaurant" OR value = "fast_food")
'''

#is this bad syntax below im using a where clause instead of and.
query_food_names = '''SELECT a.value, b.value
                    FROM nodes_tags b, nodes_tags a
                    WHERE b.id = a.id and (a.value = "restaurant" OR a.value = "fast_food") and  b.key = "name"
'''

query_burger_american = '''SELECT a.id, a.value, b.value
                    FROM nodes_tags b, nodes_tags a
                    WHERE b.id = a.id and (a.value = 'burger' or a.value = 'american') and  b.key = "name"
'''

query_cafe_coffee = '''SELECT a.id, a.value, b.value
                    FROM nodes_tags b, nodes_tags a
                    WHERE b.id = a.id and (a.value = 'cafe' or a.value ='coffee_shop') and  b.key = "name"
                    ORDER by b.value
'''

query_cuisine = '''SELECT value, count(*) as count
                  FROM nodes_tags
                  WHERE key = 'cuisine'
                  GROUP BY value
                  ORDER by count DESC
'''


query_users = '''SELECT c.user, count(*) as num
                FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) c
                GROUP BY c.user
                ORDER BY num DESC
'''

query_unique= '''SELECT count(DISTINCT(c.user)) as num
                FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) c
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

query_city = '''SELECT city.value, count(*) as count
                    FROM
                    (SELECT value, key FROM nodes_tags
                    WHERE key = 'city' UNION ALL
                    SELECT value, key FROM ways_tags
                    WHERE key = 'city') city
                    GROUP BY city.value
                    ORdER BY count DESC
'''


query_clean_street = 'SELECT key, value FROM nodes_tags WHERE (key = "street" and value LIKE "%St%")'

db = os.path.join(os.getcwd(), "sqlite_windows/madison.db")
con = sqlite3.connect(db)
cur = con.cursor()

#cur.execute('DROP TABLE IF EXISTS nodes_tags')
#conn.commit()

'''
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
'''

#get_file_size(files)
cur.execute(query_food_count)
answer = cur.fetchall()
pprint(answer)
con.close()
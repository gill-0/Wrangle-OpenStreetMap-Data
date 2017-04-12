
# Open Street Map Case Study: Madison

Link to Madison, WI OSM map 
https://www.openstreetmap.org/relation/3352040#map=12/43.0851/-89.4067

## Top Level XML Nodes
I ran an intial code audit to get an idea of the top level nodes and how many of each there were for the Madison Area. The main ones of note are node and way. Node is a point or location such as an address/shop or GPS coordinate on a road. Way can be one of two things. An open way is a combination of nodes to form a road and a closed way is an area. Nd references nodes in a way. There are more nd than nodes becuase a node can be included in more than one way.



```python
{'bounds': 1,
 'member': 11542,
 'meta': 1,
 'nd': 888431,
 'node': 724447,
 'note': 1,
 'osm': 1,
 'relation': 585,
 'tag': 237492,
 'way': 80042}
```

# Initial Audit of Tags
Below are results from a script that runs regex over element tags where the k's tag value = 'tag' to see if anything needs to be cleaned up on first glance. 


```python
{'lower': 153655, 'lower_colon': 80767, 'other': 3070, 'problemchars': 0}
```

    - There are no problem characters.
    - Lower looks for only lowercase values. 
    - Lower_colon denotes a values such as  addr:street that will be parsed out into seperate keys and values later. 

# Number of Users
I found 559 unique users by running code below. However this is different from a SQL QUERY which retreieved 551 unique users after I imported the data into the database. I found out that the difference was when users edited/added relations elements but not nodes or ways. When I edited the below code to only look at elements or ways it also returned 551. Since I did not import relations data into the database this difference is expected and I believe is sufficient enough to not warrant further investigation. 


```python
def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if 'user' in element.attrib:
            users.add(element.attrib['user'])
    return users
```

# Problems with Madison City Data 

The main problems I found and cleaned were related to addresses. Addresses follow a specific format and if they deviate from that format it is easier to find and clean as opposed to unknown unknowns within the data where I are not aware that anything is wrong with the data. 

# Cleaning Street Names

I ran a street audit to find streets that didn't have proper/uniform suffixes or prefixes (e.g. Rd. instead of Road or E/E. instead of East). On the inital audit there were some valid values such as Circle and Broadway as well as Highway Names such as County Highway M that were pulled in becasue they were not expected but are valid endings nonetheless.

Things that stood out to me that may not be street names are Bristol Bay, NewMarket Mews, and Maple Terrace. I will investigate these further later on.  

Below is code used to clean non-uniform street names. For example, E Washington Ave => East Washington Avenue. 



```python
def clean_street(name, mapping, regex):
    m = regex.search(name)
    if m:
      m = m.group()
      for key in mapping:
          if key == m:
              name = re.sub(regex, mapping[key], name)
    return name
```

### Problems That Occurred While Cleaning Street Names

Cleaning the street directions initially gave me troubles. In problematic names I was not only replacing S to South but it would also replace Street to Southreet when using the line below.


```python
name = name.replace(key, mapping[key]) 
```

This was initially not a problem with problem strings such as Cir or Ave since they would only occur once in the street address. But problem strings such as E or S were so common that I needed to be more specific with how I would replace the problem strings so I used the line below instead.


```python
name = re.sub(regex, mapping[key], name)
```

### Investigating Specific Street Addresses for Possible Further Cleaning
I checked a few values that I thought may not be actual street names for example NewMarket Mews since I have never heard of a street with such an unusual name. It turns out that this name was actually valid. 


```python
<?xml version='1.0' encoding='utf8'?>
<way changeset="45380716" id="389397164" timestamp="2017-01-22T22:39:43Z" uid="1743198" user="ItalianMustache" version="2">
    <nd ref="3925698883" />
    <nd ref="3925698884" />
    <nd ref="3925698885" />
    <nd ref="3925698886" />
    <nd ref="3925698887" />
    <nd ref="3925698888" />
    <nd ref="3925698889" />
    <nd ref="3925698890" />
    <nd ref="3925698883" />
    <tag k="addr:city" v="Waunakee" />
    <tag k="addr:housenumber" v="1803" />
    <tag k="addr:postcode" v="53597" />
    <tag k="addr:state" v="WI" />
    <tag k="addr:street" v="Newmarket Mews" />
    <tag k="building" v="house" />
  </way>
```

# Database Queries

## Importing Data into Database and Further Cleaning

When I originally imported the data I noticed some of the zip codes were not uniform. I took another look at the zip codes in the database using the query below. Since the inconsistency was not prolific I thought it would be easier and quicker to clean them while in the database.


```python
query_postcode = '''SELECT zip.value, count(*) as count
                    FROM
                    (SELECT value, key FROM nodes_tags
                    WHERE key = 'postcode' UNION ALL
                    SELECT value, key FROM ways_tags
                    WHERE key = 'postcode') zip
                    GROUP BY zip.value
                    ORDER by count DESC
'''
```

After finding the types all zip codes I cleaned the ones that were not unifrom with regex and then implemented the update statement below.


```python
def update_postcode(query_postcode):
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
            #print zipp, '---',new_zip
            cur.execute('''UPDATE nodes_tags SET value = ? 
                        WHERE (value = ?  and key = "postcode")''',
                        (new_zip, zipp[0]))
            cur.execute('''UPDATE ways_tags SET value = ? 
                        WHERE (value = ?  and key ="postcode")''',
                        (new_zip, zipp[0]))
            con.commit()

```

Below is a list of examples of zip codes that were 'dirty' and then cleaned with this method. 


```python
53703-3173 -> 53703
53705-2221 -> 53705
WI 53562 -> 53562
WI 53593 -> 53593
```

# Exploring City Values and Counts
It looks like it is more of the Greater Madison Area that is represented as opposed to just the city of Madison. There are also examples where Madison should be more uniform (e.g. 'Madison','Madison WI', 'Madison, WI'). There is a zip code value that slipped through as well. Since most of the other locations that are not in Madison are the minority, it should be decided if those locations should be dropped or if this map/data is actually of the greater Madison area. Below are the counts of city occurences from a query similiar to the postcode query. 


```python
[(u'Madison', 1837),
 (u'Waunakee', 273),
 (u'Middleton', 136),
 (u'Verona', 33),
 (u'Monona', 20),
 (u'McFarland', 18),
 (u'Sun Prairie', 16),
 (u'Fitchburg', 12),
 (u'Cottage Grove', 10),
 (u'Cross Plains', 5),
 (u'Madison, WI', 5),
 (u'Madison WI', 4),
 (u'53562', 1),
 (u'De Forest', 1),
 (u'DeForest', 1),
 (u'Martinsville', 1),
 (u'Shorewood Hills', 1),
 (u'Stoughton', 1),
 (u'Windsor', 1)]
```

# Additional Database Statistics

### Number of Nodes


```python
SELECT count(*) as count FROM nodes;
```


```python
[(80449,)]
```

### Number of Ways


```python
SELECT count(*) as count FROM ways;
```

[(8004,)]

### File Sizes

Below is the code used to get the csv, database, and osm file sizes and its output below.


```python
def get_file_size(files):
 for file in files:
    file_path = os.path.join(os.getcwd(), file)
    print file, os.stat(file_path).st_size

```


```python
nodes_tags.csv: 771 KB
nodes.csv: 60561 KB
ways_tags.csv: 7488 KB
ways.csv: 4781 KB
ways_nodes.csv: 21981 KB
sqlite_windows/madison.db: 82798 KB
madison.osm: 156259 KB
```

### User Breakdown

Below is a query that returns the number of uniquer users.


```python
SELECT count(DISTINCT(c.user)) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) c;

```


```python
[(551,)]
```

There are 2 different types of users, scripted or manual. Most of the edits have been done by very few users. We can assume that they have used a script to populate the fields and will categorize this type if they had more than 1000 edits. There are users who manually edited by hand. Many are in the single digits, but those that had less than 100 edits is a good starting point to classify these users. Between 100 and 1000 edits I would count as a gray area where I am unsure what kind of user (script of manual) has done the work. Below is a query to pull all users and the number of edits. 


```python
query_users = '''SELECT c.user, count(*) as num
                FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) c
                GROUP BY c.user
                ORDER BY num DESC
'''
```

Below are the top ten users from the query above


```python
[(u'FTA', 327533),
 (u'ItalianMustache', 170765),
 (u'woodpeck_fixbot', 84470),
 (u'hogrod', 57150),
 (u'Brutus', 45027),
 (u'hobbesvsboyle', 9378),
 (u'neuhausr', 8482),
 (u'Midnightlightning', 6536),
 (u'LoganS', 6355),
 (u'homeslice60148', 6124)]
```

I then ran a script against the results of this query to get a better idea of the two types of users. The cutoff points I used to define the different groups of 1000 and 100 are somewhat arbitrary but nonetheless give us a good idea about how the data is populated- mainly programatically by a few users. (Left out statistics for the gray area users)

### Scripted User Statistics


```python
5.08166969147 percent of users have edited greater than 1000 nodes or ways each
and account for about 95 percent of the work done.
```

### Manual User Statistics


```python
78.7658802178 percent of users have edited less than 100 nodes or ways each 
and account for about 1 percent of the work done.
```

## Amenity and Food Queries

I am interested in seeing what fields the amenity value holds. Query and list of top amenities is shown below. 


```python
query_amenity = '''SELECT value, count(*) num FROM nodes_tags
                WHERE key = "amenity"
                GROUP BY value
                HAVING num >= 25
                ORDER BY num DESC
                LIMIT 10
'''
```


```python
[(u'restaurant', 238),
 (u'parking_entrance', 109),
 (u'fast_food', 104),
 (u'bench', 92),
 (u'parking', 82),
 (u'fuel', 75),
 (u'drinking_water', 70),
 (u'cafe', 64),
 (u'school', 60),
 (u'bicycle_parking', 50)]
```

Some quirky amenities that are not show are a clock, BBQ, and a baking oven. I think this is oddly specific and likely to be the result of manually entered data. 

Below is the query and output for the number of restaurant and fast_food places in Madison.


```python
query_food_count = '''SELECT count(*) as num FROM nodes_tags
                WHERE  (value ="restaurant" OR value = "fast_food")
'''
```


```python
[(342,)]
```

Below is the query and output for the types of restaurant and fast food chains.


```python
query_cuisine = '''SELECT value, count(*) as count
                  FROM nodes_tags
                  WHERE key = 'cuisine'
                  GROUP BY value
                  ORDER by count DESC
                  LIMIT 20
'''
```


```python
[(u'pizza', 27),
 (u'coffee_shop', 24),
 (u'sandwich', 16),
 (u'asian', 15),
 (u'mexican', 13),
 (u'regional', 13),
 (u'american', 10),
 (u'burger', 10),
 (u'italian', 9),
 (u'ice_cream', 8),
 (u'chinese', 6),
 (u'greek', 5),
 (u'indian', 5),
 (u'thai', 3),
 (u'barbecue', 2),
 (u'breakfast', 2),
 (u'japanese', 2),
 (u'mediterranean', 2),
 (u"50's_style_diner", 1),
 (u'pizza;italian', 1)]
```

When living in Madison I thought there was a lack of good international food since it is a smaller midwestern city. This list may imply there is more diversity than I thought.  This list could also benefit from standardization of cuisine names such as (u'pizza', 27) and (u'pizza;italian', 1).

### Exploring if Restaurant Data is up to Date

Below is a query pulling all the burger and american restuarants to see if they are up to date since I have personal knowledge of some restaurants that have closed and opened recently.


```python
query_burger = '''SELECT a.value, b.value
                    FROM nodes_tags b, nodes_tags a
                    WHERE b.id = a.id and (a.value = 'burger' or a.value = 'american') and  b.key = "name"
'''
```


```python
[(u'american', u'Subway'),
 (u'american', u'Dairy Queen'),
 (u'burger', u"McDonald's"),
 (u'american', u'Bassett Street Brunch Club'),
 (u'burger', u"McDonald's"),
 (u'american', u'Everly'),
 (u'american', u"Ella's Deli and Ice Cream Parlor"),
 (u'burger', u"Culver's"),
 (u'burger', u"McDonald's"),
 (u'burger', u'DLUX'),
 (u'american', u"Nick's"),
 (u'american', u'Buffalo Wild Wings'),
 (u'burger', u'Burger King'),
 (u'american', u'Buffalo Wild Wings'),
 (u'american', u'The Flying Hound Ale House'),
 (u'burger', u'Mooyah'),
 (u'burger', u'Five Guys'),
 (u'burger', u'Mooyah'),
 (u'burger', u'Red Rock Saloon'),
 (u'american', u'HopCat')]
```

From first glance it looks like the restuarants are up to date. AJ BOMBERS which has closed in Madison in the last year is not on the list, and Mooyah which recently opened a new location is also on the list.

### Cafes vs Coffee Shops

I believe the way cafes and coffee shops are structured in the data is probably not the best way. Restaurants and cafes are both considered amenities. However, coffee_shops are a type a restaurant while cafes are not.  Using a query I found that some cafes and coffee shops held the same id as well. I find it peculiar that cafe is not a child of restaurants but coffee_shop is. For future cleaning, I would classify cafes under the restaurant parent node. Below is a the query I used and part of the output. 


```python
query_cafe_coffee = '''SELECT a.id, a.value, b.value
                    FROM nodes_tags b, nodes_tags a
                    WHERE b.id = a.id 
                        and (a.value = 'cafe' or a.value ='coffee_shop') 
                        and  b.key = "name"
                    ORDER by b.value
'''
```


```python
(1752001452, u'cafe', u"Beans N' Cream Coffeehouse"),
 (1752001452, u'coffee_shop', u"Beans N' Cream Coffeehouse"),
```

# Future Cleaning and Analysis

For future cleaning I would cross-validate the restaurant data with another data source such as Yelp or Google to see if all the restaurants are kept up to date. Even though the intial exploration shows that restaurants may be kept up to date, it is common for businesses in the food industry to go out of business in a few years and for others to spring up. A potential problem with validating the data is restuarants that are the actually the same between data sets but have slightly different names. For example, "Five Guys" may exist in my dataset, but Yelp may have the same restuarant under "Five Guys Burgers and Fries". 

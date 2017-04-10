"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import lxml.etree as etree
import pickle



OSMFILE = "madison.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
cardinal_direction_re= re.compile(r'^\S+',re.IGNORECASE )


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]



street_mapping = {'Ave': 'Avenue',
     'Cir': "Circle",
     'Dr': 'Drive',
     'Ln': 'Lane',
     'Ln.': 'Lane',
     'Ct': 'Court',
     'St': 'Street',
     'St.': 'Street',
     'street': 'Street',
     'Blvd': 'Boulevard',
     'Pkwy': 'Parkway',
     'Rd': 'Road',
     'Rd.': 'Road'}

cardinal_mapping = {'E': 'East',
     'E.': 'East',
     'N': 'North',
     'N.': 'North',
     'S': 'South',
     'S.': 'South',
     'W': 'West',
     'W.': 'West'}




problems = ["Newmarket Mews"]



def check_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected: #to find ones needing fix
        #if street_type in street_mapping: #this is to fix the mappings
            street_types[street_type].add(street_name)





def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

def is_city(elem):
    return (elem.attrib['k'] == "addr:city")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    zip_or_city = defaultdict(int)
    #element_list = {'street': street_types, 'cardinal': cardinal} # 'city': city, 'zip': zip_code}


    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    #check_street_type(street_types, tag.attrib['v'])
                    #check_street_direction(street_types, tag.attrib['v'])
                    check_invalid_addr(street_types, tag.attrib['v'], elem)
                #if is_postal_code(tag):
                #if is_city(tag):
                    #check_zip_city(zip_or_city, tag.attrib['v'])
    osm_file.close()
    #return street_types
    return zip_or_city


def check_street_direction(street_directions, street_name):
    m = cardinal_direction_re.search(street_name)
    if m:
        street_dir = m.group()
        if street_dir in cardinal_mapping:
            street_directions[street_dir].add(street_name)


def check_invalid_addr(dic, street_name, element):
        if street_name in problems:
            dic[street_name].add(element)
            element = ET.tostring(element, encoding='utf8', method='xml')
            print(element)
            #print(element.dom.toprettyxml(indent = '  '))

def check_zip_city(dic, zip_or_city):
        dic[zip_or_city] += 1






def update_name(name, mapping, regex):
    m = regex.search(name)
    m = m.group()
    for key in mapping:
        if key == m:
            name = re.sub(regex, mapping[key], name)
    return name


def test():
    cor_types = audit(OSMFILE)
    #assert len(st_types) == 3
    pprint.pprint(dict(cor_types))
    '''
    for cor_type, ways in cor_types.iteritems():
        for name in ways:
            better_name = update_name(name, cardinal_mapping, cardinal_direction_re)
            better_name = update_name(better_name, street_mapping, street_type_re)
            print name, "=>", better_name
'''

if __name__ == '__main__':
    test()

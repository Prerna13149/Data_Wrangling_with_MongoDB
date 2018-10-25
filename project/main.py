#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from collections import defaultdict
import create_DB
import test

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

OSMFILE = "example.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected_street_types = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Crescent", 'Terrace', 'Way', 'Circle', 'Sideroad', 'Line', 'Grove', 'Gate', 'Gardens']
expected_addr_types = ["street", "city", "housenumber", "postcode", "province", "Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Rd." : "Road",
            "Ave" : "Avenue",
            "N." : "North",
            "S." : "South",
            "W." : "West",
            "E." : "East"
            }
################################## data insertion ################################    
def insert_data(data, db):
    # Your code here. Insert the data into a collection 'arachnid'
    count = 0
    ct = 100
    for entry in data:
        count = count + 1
        db.example.insert(entry)
        ct = ct - 1

################################## pipeline creation ################################
def make_pipeline():
    # complete the aggregation pipeline
    myDict1 = {"$exists":True}
    myList = [];
    myList.append(myDict1)
    myStreet = "address.street"
    myMatch = "$match"
    assert len(myList) == 1
    myDict2 = {"_id":"$address.street"}
    myList.append(myDict2)
    myGroup = "$group"
    assert len(myList) == 2
    mySort = "$sort"
    myDict3 = {"_id":1}
    myList.append(myDict3)
    assert len(myList) == 3
    myPipe = [  {myMatch:{myStreet:myDict1}},
            {myGroup:myDict2},
            {mySort:myDict3}]
    return myPipe

################################## checking keys ################################
def check_key(street_name):
    keys_of_streets = []
    for keys in mapping:
        keys_of_streets.append(keys)
    #print keys_of_streets
    #print street_name
    p1 = street_name
    a = len(p1)
    for i in keys_of_streets:
        if i==street_name:
            return True
    return False

################################## checking pipeline ################################
def check_pipeline(result):
    indices = []
    for i in range(len(result)):
        if "." not in result[i]["_id"] and check_key(result[i]['_id'].rsplit(None,1)[-1]) == False:
            indices.append(result[i])
            
    return indices

def aggregate(db, pipeline):
    return [doc for doc in db.example.aggregate(pipeline)]    

################################## main ################################
if __name__ == "__main__":
 
    test.test()
    '''
    db = create_DB.get_db()
    with open('chicago.json') as f:
        data = json.loads(f.read())
        insert_data(data, db)
        print db.example.find_one()
    pipeline = make_pipeline()
    result = check_pipeline(aggregate(db, pipeline))
    pprint.pprint(result)'''

    
        
    
    
    
    
    



import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from collections import defaultdict

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

################################## added changes ################################			
def is_member_of(list, element):
	for i in range(len(list)):
		if(list[i]==element):
			return True
	return False


def update_name(name, mapping):
	words = name.split(" ");
	better_name = []
	for word in words:
		if is_member_of(mapping.keys(),word):
			word = mapping[word];
		better_name.append(word);    
	
	name = " ".join(str(word) for word in better_name)
	return name
lat_list = ['lat','lon']    

################################## added changes ################################
def create_node(element, node):
    node["created"] = {"version": element.attrib['version'],"changeset": element.attrib['changeset'],
                            "timestamp": element.attrib['timestamp'],
                            "uid": element.attrib['uid'],
                            "user": element.attrib['user']}


################################## added changes ################################
def tag_children(element,node):
	address = {}
	for tags in element.iter("tag"):
		if not problemchars.search(tags.attrib['k']):
			if lower_colon.search(tags.attrib['k']):
				if tags.attrib['k'].find('addr') == 0:
					address[tags.attrib['k'][5:]] = tags.attrib['v']
					found_name = re.search("addr:(\S+)",tags.attrib['k'] ) 
					if found_name.group(1) == 'street':
						modified_name = update_name(tags.attrib['v'], mapping)
						address[found_name.group(1)] = modified_name
						tags.attrib['v'] = modified_name
					else:
						node[tags.attrib['k']] = tags.attrib['v']
 				elif tags.attrib['k'].find(':') == -1:
					node[tags.attrib['k']] = tags.attrib['v']
	if bool(address) == True:
  		node["address"]=address

################################## added changes ################################        
def iterate_children(element,node):
	for iterator in element.iter("nd"):
		if 'node_refs' not in node:
		  node['node_refs'] = []
		node['node_refs'].append(iterator.attrib['ref'])

################################## added changes ################################
def shape_element(element):
	node = {}
	if element.tag == "node" or element.tag == "way":
		node['id']=element.attrib['id']
		node['type']=element.tag
		create_node(element,node)
		tag_children(element,node)
		iterate_children(element,node)
		return node
	else:
		return None


def audit_street_type(street_types, street_name):
	m = street_type_re.search(street_name)
	if m:
		street_type = m.group()
		if is_member_of(expected,street_type)==False:
			street_types[street_type].add(street_name)
			
def is_street_name(elem):
	return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
	osm_file = open(osmfile, "r")
	street_types = defaultdict(set)
	for event, elem in ET.iterparse(osm_file, events=("start",)):
		if elem.tag == "node" or elem.tag == "way":
			for tag in elem.iter("tag"):
				if is_street_name(tag):
					audit_street_type(street_types, tag.attrib['v'])
	osm_file.close()
	return street_types

def process_map(file_in, pretty = False):
	file_out = "chicago_new.json".format(file_in)
	data = []
	st_types = audit(OSMFILE)
	pprint.pprint(dict(st_types))
	with codecs.open(file_out, "w") as fo:
		for _, element in ET.iterparse(file_in):
			el = shape_element(element)
			if el:
				data.append(el)
				if pretty:
					fo.write(json.dumps(el, indent=2)+"\n")
				else:
					fo.write(json.dumps(el) + ",\n")
	return data

def test():
	data = process_map('example.osm', False)#chicago_part

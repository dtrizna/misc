#!/usr/bin/env python

# ----- README STARTS --------
#
# If anyone wants to use this script in their environment
# be sure to replace YOUR_SEARCH_ID with actual search ID
# within the curl command URL at line 70.
#
# Also 'post_body' variable at line 63 should be tuned according 
# to your query, as it is build assuming there's some specific static
# expressions from the beginning and the of query.json file.
# See: https://github.com/dtrizna/my_ELK_scripts/blob/master/TOR_SEARCH/query.json
#
# Additionaly set correct path to query.json file 
# at lines 65 and 70, replacing <PATH/TO/> entries.
#
# ----- README ENDS ----------

import re
import requests
import subprocess

# -------------------------
# GET THE LIST WITH TOR EXIT NODES FROM TORPROJECT WEB PAGE
nodes_raw = requests.get('https://check.torproject.org/exit-addresses')
nodes_raw_list = nodes_raw.text.split()

# -------------------------
# FILTER FROM WHOLE PAGE ONLY IP ADRESSES
regex = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
nodes = filter(regex.search, nodes_raw_list)

# -------------------------
# IP ADRESSES ARE IN UNICODE FORMAT, ENCODE THEM TO STRING
search_query = ''
i = 0

while i < len(nodes):
    try:
        nodes[i] = nodes[i].encode('ascii')
    except UnicodeEncodeError as err:
        print "Error due to IP adress encoding from Unicode to ASCII."
        print "UnicodeEncodeError says: {}".format(err)
    i = i + 1

# -------------------------
# CREATE KIBANA SEARCH QUERY
search_query = " OR ".join(nodes)


# -------------------------
# UPDATE FILE, THAT WILL BE USED AS BODY IN UPDATE COMMAND
# (CAN'T USE DIRECTLY, ES RETURNS ERROR, WORKS ONLY THROUGH FILE USING CURL)

with open('query.json', 'r') as file:
    data = file.readlines()

# 'data' is list, every element describes line in file called in above cycle
# As there's only one line(it must be onelined, for ES to accept it),
# data[0] represents all the future POST body request.
# It has fixed values from the beginning and the end of line.
# Although middle part may vary depending on request to tor website above.
post_body = data[0][:127] + search_query + data[0][-258:]

with open('<PATH/TO/>query.json', 'w') as file:
    file.writelines(post_body)

# -------------------------
# FINALY MAKE THE UPDATE REQUEST TO ELASTICSEARCH AND SEE REPLY
call = subprocess.Popen("curl -s -XPOST http://localhost:9200/.kibana/search/<SEARCH_ID>/_update?pretty=true -d@<PATH/TO/>/query.json",
                        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(result, error) = call.communicate()

print('Result is:\n {}\n'.format(result))
if error:
        print("Error is: \n {}".format(error))

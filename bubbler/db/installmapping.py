#!/usr/bin/env python

import os
import json
import mapping
import bannermodel
import scanmodel
from datetime import datetime
from pyes import *

def configure_scan():
	obj = conn.factory_object("survey_debug", scanmodel.document_type, scanmodel.scan)
	obj.timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	obj.scanner_name = "nmap + $VERSION"
	obj.summary = "the summary is the final output lines of nmap."
	obj.command = "the nmap command used"
	obj.data = "the nmap xml scan report, base64encoded and stored as binary/blob"
	obj.target = ["192.168.0.1","192.168.0.2"]
	return obj


conn = ES('127.0.0.1:9200',timeout=3.5)
# Get a manager object -> manager = managers.Indices(conn) OR managers.Cluster(conn)
conn.indices.delete_index("survey")
conn.indices.create_index("survey")
#try:
#	conn.indices.delete_index("survey_debug")
#except:
#	pass
#conn.indices.create_index("survey_debug")
#conn.indices.put_mapping("banner", mapping.banner, "survey_debug")
#conn.indices.put_mapping("scan", mapping.scan, "survey_debug")
conn.indices.put_mapping("banner", mapping.banner, "survey")
#conn.indices.put_mapping("scan", mapping.scan, "survey")


#obj = configure_scan()
#obj.save()
#reloaded = conn.get(bannermodel.index_name, bannermodel.document_type, obj._meta.id)
#assert reloaded.isp == "Oakville"

#conn.indices.refresh("survey")
#q = TermQuery("target", "192.168.0.1")


# All results can be returned with curl too
# curl -XGET localhost:9200/foo/_search?
#results = conn.search(query = q)
#print results
#for r in results:
#	print json.dumps(r)


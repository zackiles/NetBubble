# TO INSTALL -> conn.indices.put_mapping("scan", mapping.scan, "survey")
scan = {
	"_source" : {"compress" : "true"},
	"properties":{
	  "timestamp":{"type":"date", "format":"yyyy/MM/dd HH:mm:ss" },
	  "scanner_name":{ "type":"string"},
	  "summary":{"type":"string", "index":"no"},
	  "command":{"type":"string", "index":"not_analyzed"},
	  "data":{ "type":"binary" },
	  "target":{ "type":"ip" } # String[] of target ip's scanned. Stored as type IP in elastic seearch
	}
}
# TO INSTALL -> conn.indices.put_mapping("banner", mapping.banner, "survey")
banner = {
	"properties":{
		"timestamp": { "type":"date", "format":"yyyy/MM/dd HH:mm:ss" },
		"ip": { "type":"ip" },
		"host_os": {"type":"string"},
		u"data":{"type":"string"},
		u"product": {"type":"string"},
		"version": {"type":"string", "index":"not_analyzed"},
		u"device_type": {"type":"string"},
		"port": {"type":"integer"},
		"service": {"type":"string"},
		"service_os": {"type":"string"},
		"protocol": {"type":"string"},
		u"info": {"type":"string"},
		"cpe": {"type":"string"},
		u"title": {"type":"string"},
		u"html": {"type":"string"},
		"whois": {
			"properties":{
				u"net_name":{"type":"string"},
				"asn": {"type":"string"},
				"cidr":{"type":"string"},
				"net_range":{"type":"string"},
				"ips_in_range":{"type":"long"},
				u"org_name":{"type":"string"},
				"org_id":{"type":"string"},
				"hostnames": {"type":"string"},
				"domains": {"type":"string"}
			}
		},
	   "location": {
			"properties":{
				"area_code":{"type":"string"},
				u"city":{"type":"string"},
				"country_code2":{"type":"string"},
				"country_code3":{"type":"string"},
				u"country_name":{"type":"string"},
				"lat_lon":{"type":"geo_point"}, # lattitude longitude
				"lon_lat":{"type":"double"}, # help for geojson
				"postal_code":{"type":"string"},
				u"region_name":{"type":"string"}
			}
		},
		"opts": {
			"properties":{
				"name":{"type":"string"},
				"data":{"type":"string"}
			}
		}

	}	
}

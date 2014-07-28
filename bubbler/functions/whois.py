#!/usr/bin/env python
import requests
import json
import socket

def get_netobject_for_banner(ip):
	headers = {
	 "Accept": "application/json"
	}
	arin_whois = "http://whois.arin.net/rest/ip/"
	r = requests.get(arin_whois, headers = headers)
	data = r.json()
	ipinfodb = "http://api.ipinfodb.com/v3/ip-country/?key= 6988e44f7064860b3b394f59309efd480c0e5d4636359d3f6e967f30c98a7070&ip=" + ip + "&format=json"
	r_ip = requests.get(ipinfodb)
	buff =""
	buff2 =""
	buff3 = ""
	try:
		buff = data.get('net').get("originASes").get("originAS").get("$")
	except:
		pass
	try:
		buff2 = socket.gethostbyaddr(ip)[0]
	except:
		pass
	try:
		buff3 = data.get('net').get("orgRef").get("@name")
	except:
		pass	
	netobject = {
		"country_code2" : r_ip.json()['countryCode'],
		"hostnames" : buff2,
		"block_name" : data.get("net").get("name").get('$'),
		"org" : buff3,
		"isp" : data.get('net').get("name").get('$'),
		"asn" : buff,
		"cidrLength" : data.get("net").get("netBlocks").get("netBlock").get('cidrLength').get("$"),
		"startAddress" : data.get("net").get("netBlocks").get("netBlock").get('startAddress').get("$"),
		"cidr" : str(data.get("net").get("netBlocks").get("netBlock").get('startAddress').get("$") + "/" + data.get("net").get("netBlocks").get("netBlock").get('cidrLength').get("$"))
	}
	return netobject

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  bannerbulker.py
#  
#  Copyright 2014 Zachary Iles <zackiles@development>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
# 
from pyes import *
from pyes.models import DotDict
from netaddr import *
from config.bubblerconfig import SCAN_DIR
from libnmap.parser import NmapParser
from libnmap.reportjson import ReportDecoder, ReportEncoder
from libnmap.objects import NmapReport
import glob
import db.bannermodel as bm
import json
import shutil
from datetime import datetime
import re
import socket
from tld import get_tld
import requests
import signal
import sys
import time

class BannerImport(object):


#TODO GLOBAL VARIABLES
# banner->banner.cpe ? (not sure if this exists yet)
# banner->whois.asn
# banner->whois.cidr
# banner->whois.domains
# banner->whois.hostnames (improve)
# banner->location.country_code2
# banner->location.country_code3
# banner->location.postal_code
# banner->location.region_name
# banner->location.area_code
# banner->location.? (list of website links that match country_name and hostname/ip?)
# banner->banner.cpe
# banner->banner.html
	
	def __init__( self, online_mode=False, bulk_mode=False, debug_mode=False ):
		if debug_mode:
			self._index = "survey_debug"
		else:
			self._index = "survey"
		self._documment_type = "banner"
		self._online_mode = online_mode
		self._banner_count = 0
		self._scan_count = 0
		self._bulk_mode = bulk_mode
		self._debug_mode = debug_mode
		if bulk_mode:
			self._conn = ES('selandra.com:9200', timeout=300, bulk_size=50, default_indices=self._index, default_types=self._documment_type, dump_curl="bannerimport.log")
		else:
			self._conn = ES('selandra.com:9200', timeout=300, default_indices=self._index, default_types=self._documment_type, dump_curl="bannerimport.log")

	def from_nmap_xml(self, scan_dir=SCAN_DIR):
		try:
			while True:
				while len(glob.glob(scan_dir + "/*.xml")) == 0:
					print "Waiting for nmap scan files..."
					time.sleep(30)
				print "[]-->Processing " + str(len(glob.glob(scan_dir + "/*.xml"))) + " new scans."
				for scan_file in glob.glob(scan_dir + "/*.xml"):
					print "[]-->Importing " + scan_file
					scan_obj = NmapParser.parse_fromfile(scan_file)
					for host in scan_obj.hosts:
						self._scan_count += 1
						# doc_id is the _index in elasticsearch. it's immutable for the host.
						doc_id = str(int(IPAddress(host.ipv4)))
						print "   Importing banner : " + str(doc_id)
						new_entry_model = self._conn.factory_object(self._index, self._documment_type, bm.host)
						self._create_banner_object(new_entry_model, host)
					# Cleanup processed scans by moving to the 'archive' subdirectory.
					if not self._debug_mode:
						shutil.move(scan_file, scan_dir + "/archive")
			if self._bulk_mode:
				bulk_result = self._conn.force_bulk()
				print "[]-->Flushed : " + str(bulk_result) + " from the bulk."
			print "[]-->Processed : " + str(self._scan_count) + " scans, and " + str(self._banner_count) + " banners successfully."
			print "[]-->DONE"
		except KeyboardInterrupt:
			self._dispose()
	
	def _create_banner_object(self, host, nmap): 
		host.timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
		host.ip = str(nmap.ipv4)		
		if nmap.os_match_probabilities():
			host.host_os = nmap._extras['os']['osclass'][0]
		for script in nmap.scripts_results:			
			if script['id'] == 'whois':
				s_lines = script.get('output').splitlines()
				for s in s_lines:
					if not re.match(r'^\s*$', s):
						entry = s.split(':', 1)					
						if 'netname' == entry[0]:
							host.whois['net_name'] = unicode(entry[1].strip())
						if 'orgname' == entry[0]:
							host.whois['org_name'] = unicode(entry[1].strip())
						if 'custname' == entry[0]:						
							host.whois['org_name'] = unicode(entry[1].strip())
						if 'orgid' == entry[0]:
							host.whois['org_id'] = entry[1].strip()
						if 'netrange' == entry[0]:
							r = entry[1].split('-')
							host.whois['ips_in_range'] = len(list(iter_iprange(r[0].strip(), r[1].strip())))
							host.whois['net_range'] = entry[1].strip()
			if script['id'] == 'ip-geolocation-maxmind':
				s_lines = script['output'].splitlines()
				try:
					country_index = s_lines[3].index(",") + 1
					host.location[u'country_name'] = unicode(s_lines[3][country_index::].replace(" ", ""))
					city_index = s_lines[3].index(":") + 1
					host.location[u'city'] = unicode(s_lines[3][city_index:country_index - 1].replace(" ", ""))
					host.location['lat_lon'] = s_lines[2].rpartition(':')[-1].replace(" ", "")
					flip = str(host.location['lat_lon']).split(',', 1);
					host.location['lon_lat'] = [flip[1] , flip[0]] # helper for geojson	
				except ValueError:
					print ("WARNING : There was an error parsing the banners geo data fiels. Continuing anyway.")
					# Not sure te best thing to do here ATM. Not convinced that
					# the maxmin geo-ip api is the one we should use so I'm
					# not optimizing this currently.
					pass
		# BANNER DATA
		for service in nmap.services:
			print "      Banner found : " + service.service + " port : " + str(service.port)
			host.opts = []
			host.whois['hostnames'] = []
			for hostname in nmap.hostnames:
				host.whois['hostnames'].append(hostname)
			host.timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
			host.service = service.service
			host.port = service.port
			host.protocol = service.protocol
			host.product = unicode(service._service.get('product'))
			host.info = unicode(service._service.get('extrainfo'))
			host.device_type = unicode(service._service.get('devicetype'))
			host.service_os = service._service.get('ostype')
			host.version = service._service.get('version')
			for extra_script in service.scripts_results:
				if extra_script.get('id') == 'http-headers':
					host.data = unicode(extra_script.get('output'))
				elif extra_script.get('id') == 'banner':
					host.data = unicode(extra_script.get('output'))
				elif extra_script.get('id') == 'http-title':
					host.title = unicode(extra_script.get('output'))
				else:
					if host.opts:
						host.opts.append(extra_script)
					else:
						host.opts = [extra_script]
			# Online supplementry data only.
			if self._online_mode:
				host = self._get_online_data(host)
			result = host.save(bulk=self._bulk_mode, id=None)
			if self._bulk_mode:
				print "   OK - BANNER ADDED TO BULK."
			else:
				print "   OK - BANNER ID : " + str(result)
				
	def _dispose(self):
		if self._bulk_mode:
			bulk_result = self._conn.force_bulk()
			print "[]-->Flushed : " + str(bulk_result) + " from the bulk."
		print('[]-->IMPORTING STOPPED.')
		exit(0)

	def _get_online_data(self, host_object):
		ip = str(host_object['ip'])
		arin_whois = "http://whois.arin.net/rest/ip/" + ip
		ipinfodb = "http://api.ipinfodb.com/v3/ip-city/?key=6988e44f7064860b3b394f59309efd480c0e5d4636359d3f6e967f30c98a7070&ip=" + ip + "&format=json"
		headers = {"Accept": "application/json"}
		arin_response = None
		ipinfodb_response = None
		hostname = None
		asn = None
		cidr = None
		org_name = None
		cust_name = None
		try: arin_response = requests.get(arin_whois, headers = headers, timeout=1).json()
		except Exception, e: print e
		
		if hasattr(socket, 'setdefaulttimeout'):
			# Set the default timeout on sockets to 5 seconds
			socket.setdefaulttimeout(1)
		#try: hostname = socket.gethostbyaddr(ip)[0]
		#except Exception, e: print e
		try: ipinfodb_response = requests.get(ipinfodb, headers = headers, timeout=1).json()
		except Exception, e: print e
		if arin_response:
			try: org_name = arin_response.get('net').get("orgRef").get("@name")
			except: pass
			try: cust_name = arin_response.get('net').get("customerRef").get("@name")
			except: pass
			try: asn = arin_response.get('net').get("originASes").get("originAS").get("$")
			except: pass
			try: start_address = str(arin_response.get("net").get("netBlocks").get("netBlock").get('startAddress').get("$"))
			except: pass
			try: cidr_length =  str(arin_response.get("net").get("netBlocks").get("netBlock").get('cidrLength').get("$"))
			except: pass
			try: cidr = start_address + "/" + cidr_length
			except: pass
			if asn:
				host_object['whois']['asn'] = asn
			if cidr:
				host_object['whois']['cidr'] = cidr
			if not host_object['whois']['org_name']:
				if org_name:
					host_object['whois']['org_name'] = unicode(org_name)
				if cust_name:
					host_object['whois']['org_name'] = unicode(cust_name)
		
		if ipinfodb_response and ipinfodb_response.get('statusCode') == 'OK':
			host_object['location']['country_code2'] = ipinfodb_response.get('countryCode')
			host_object['location']['country_code3'] = ipinfodb_response.get('countryName')[:3]
			host_object['location']['region_name'] = unicode(ipinfodb_response.get('regionName'))
			host_object['location']['postal_code'] = ipinfodb_response.get('zipCode')
		if hostname:
			domain = get_tld('http://' + hostname)
			if not domain in host_object['whois']['domains']:
				host_object['whois']['domains'].append(domain)
			if not hostname in host_object['whois']['hostnames']:
				host_object['whois']['hostnames'].append(hostname)
		return host_object

def main():
	importer = BannerImport( online_mode=True, bulk_mode=True, debug_mode=False )
	importer.from_nmap_xml()
	return 0

if __name__ == '__main__':
	main()

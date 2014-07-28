# GENERIC MODEL OBJECT FOR BANNER TYPE.
# This is just the specification and for auto-complete helpers in your IDE.
# Don't actually use this object to add to the database. This is more just for documentation purposes.

_index="survey"
_type="host"
_id = None # _id should map to long integer version of the host IP. this is immutable.
host = {
	# MANDATORY - MAIN INDEXES
	"timestamp": None, #Date added.
	"ip": None,	# Ip as string on client side, elastic search converts to its native IP type
	"host_os": None, # The operating system that powers the device
	"data":None, # The raw banner, if this is a webserver, this is the header getched with GET/HEAD.
	u"product": None, # The name of the product that generated the banner.
	"version": None, # The products version
	u"device_type": None, # The type of device (webcam, router, etc.).
	"port": None, # Integer The port number that the service is operating on.
	"service": None, # The service name if known (ssh,http etc)
	"service_os": None,
	"protocol": None, # The protocol if known (tcp,udp,sip etc)
	u"info": None, # Miscellaneous information that was extracted about the product
	"cpe": None, # The relevant Common Platform Enumeration for the product
	u"title": None, # WEBSITE ONLY -The title of the website as extracted from the HTML source.
	u"html": None, # WEBSITE ONLY -The raw html source of the body.
	#WHOIS
	"whois": {
		u"net_name": None,
		"asn": None, # The autonomous system number (ex. "AS4837")
		"cidr": None,
		"net_range": None,
		"ips_in_range": None, # Count of all ips in the CIDR
		u"org_name": None,
		"org_id": None,
		"hostnames": [], # String[] of hostnames like '123account.domain.com' that are linked to this IP.
		"domains": [] # String[] of the top level ONLY domains like 'domain.com' linked to this IP.
	},
   "location": {
			"area_code": None,
			u"city": None,
			"country_code2": None,
			"country_code3": None,
			u"country_name": None,
			"lat_lon": None, # lattitude longitude
			"lon_lat": None, # help for geojson
			"postal_code": None,
			u"region_name": None
	},
	# OPTIONAL - INDEXED ( with care )  note: "data" is not indexed, so to make banners more searchable we should add stuff below
	"opts": [],
}

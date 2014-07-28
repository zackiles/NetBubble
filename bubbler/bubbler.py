#!/usr/bin/env python

import textwrap
import sys
import os
from config.bubblerconfig import BUBBLER_HOME

def main():
	args = sys.argv
	proxy_args = " ".join(args[2:]) # cleaned arg's to pass in proxy to module
	if not len(args) >= 2:
		print "You have not selected a module!"
		print_help()
		exit(1)
	if "-h" == args[1] or "--help" == args[1]:
		print_help()
	elif args[1] in ["target","scan","survey"]:
		os.system(BUBBLER_HOME + "/" + args[1] + ".py " + proxy_args )
	else:
		print "You've selected an invalid option. Exiting."
		print_help()
		exit(1)

def print_help():
	menu_text = textwrap.dedent("""
	The Bubbler Management CLI 
	--------------------------------
	This is the main interface for management of your Bubbler system.
	Below is a list of the core modules. Starting your banner database
	is as simple as:
	
	1) Generating a target, or list of targets with the target module.
	2) Starting a scan using the target
	
	The modules in this interface can be called like so:
	"./bubbler [module name] [module options]".

	"target" - Generates IP lists, and provides OSINT tools.
	"survey" - Database management, querying, and info.
	"scan"   - Starts NMAP scans and imports banners to database.

	NOTE: All modules have their own help menus!
	To start try, "bubbler scan --help"
	""")
	print menu_text

if __name__ == '__main__':
    rc = main()
    sys.exit( rc )
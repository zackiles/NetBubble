#!/usr/bin/env python

import sys
import os
import netaddr
from config.bubblerconfig import DATA_DIR, TARGET_DIR
from subprocess import Popen, PIPE, STDOUT
from netaddr import *
import requests
from functions.cd import cd
import textwrap
import shutil
import subprocess

def main():
	args = sys.argv
	if not len(args) >= 2:
		print "You have not selected an option."
		print_help()
	if "-h" == args[1] or "--help" == args[1]:
		print_help()
	elif "build" == args[1]:
		if args[2]:
			configure_target(args)
		else:
			print "No options specified for build mode. Exiting."
	elif "flush" == args[1]:
		if "--all" in args:
			flush_target(TARGET_DIR)
			os.makedirs(TARGET_DIR)
		elif "--target-name" in args:
			flush_target(args)
	else:
		print "The options specified were not recognized. Exiting"
		exit(1)
				
def flush_target(args):
	try:
		target_name = args[(args.index("--target-name") + 1)]
		if os.path.exists(target_name):
			shutil.rmtree(target_name)
		else:
			if not os.path.exists(TARGET_DIR + "/" +  target_name):
				print "Can't flush, the target does not exist! Exiting."
				return
			else:
				shutil.rmtree(TARGET_DIR +  "/" + target_name)
	except Exception, e:
		print str(e)
		print "The target was not flushed Exiting."
		return
	print target_name + " was flushed successfully!"

def configure_target(args):
	if not "--net-range" in args:
		print "No --net-range specified for build mode. Exiting."
		return
	target_ip = IPNetwork(args[(args.index("--net-range") + 1)])
	target_name = ""
	split_count = 0
	if not "--target-name" in args:
		target_name = str(target_ip.value)
		print "No --target-name selected, defaulting to " + target_name
	else:
		target_name = args[(args.index("--target-name") + 1)]
	if "--split-count" in args:
		split_count = args[(args.index("--split-count") + 1)]
	build_target(target_ip, target_name, split_count)

def build_target(target_ip, target_name, split_count):
	output_dir = TARGET_DIR +  "/" + target_name
	target_name += ".target" # add .target extension to file. it's helpful :)
	if os.path.exists(output_dir): # only one target with same name at a time.
		# make sure its not just empty. we'll continue if it's only empty.
		if len(os.listdir(output_dir)) > 0:
			print "Target already exists! Please flush before re-building. Exiting."
			return
	else:
		# make a folder to contain the target list/s.
		os.makedirs(output_dir)
		print 
	with cd(output_dir):	
		print "Generating IP lists for : " + target_name.replace(".target","")
		print "Total IP count in range : " + str(target_ip.size)
		if split_count > 0:
			print "Max IP per list (split-count) : " + str(split_count)
			print "Total IP lists after split : " + str(target_ip.size / int(split_count))
			linux_split = subprocess.Popen("split -d --numeric-suffixes --lines " + str(split_count) + " - " + target_name,
													stdin=subprocess.PIPE,
													stdout=subprocess.PIPE,
													stderr=subprocess.PIPE,
													shell = True)
			for i in target_ip:
				linux_split.stdin.write(str(i) + '\n')
			linux_split.stdin.close()
			linux_split.wait()
		else:
			with open(output_dir + "/" + target_name, 'a') as target_file:
				for i in target_ip:
					target_file.write(str(i) + '\n')				
	print "Target built successfully!"
	print "You can now start a scan by running the follow :"
	print "bubbler scan --target-name " + target_name.replace(".target","")

def print_help():
	menu_text = textwrap.dedent("""
Target Module for the Bubbler Backend
--------------------------------
This module builds lists of IP's used for the scans.
Currently it takes an IP range or block and generatesa list, 
or lists of IP's that can be automatically queued up for scans 
in the Bubbler "scan" module. Future versions will have options
to search for ranges based off company names, city, country, and 
other such fine-grained auto-reconnaissance. The purpose of bubbler
after-all, is to be able to connect visual and physical meta-data
to our electronic landscape.

Target as three "modes". Modes can be called like:
"bubbler target mode [ mode-options ]" 

Most modes have a single mandatory option, and several optional.
For example, "build" has one mandatory option of "--net-range" that
takes a CIDR to generate a list for such as 192.0.0.0/8. As
well optional paramaters such as "--target-name" and "--split-count"
can be used. To generate a target called "mynet" the command would be:

"bubbler target build --target-name "mynet" --net-range 192.168.0.0/16"

And to start a scan after:
"bubbler scan --target mynet" 

-------------------------------MODES LIST-------------------------------

1) build	
"--split-count"	
-When building targets, this number signifys the
maximum amount of IP's to store per target file.
Useful to split eventual large scans into smaller 
jobs to add to the queue.
						
"--target-name"   
-If not selected, this will be auto generated based off
the target IP range or primary host name. Setting a name
allows easier management when starting scans like;
"bubbler scan --target [target-name]
						

2) flush
"--all"			  
-RemoveS all target lists from the cache. After removal 
targets can no longer be called directly from the 
scanning module, and there lists are deleted from the 
system. Mainly useful when trying to conserve hard-drive 
space, or when regenerating lists. 

"--target-name"   
-Like the --all option, but used for a single target name.
Given the primary target name, it also deletes all lists
related to it if the --split-count option was given when
building the lists. This option is superseded by "--all" 
as then all targets are flushed from the system no matter
what their name is.
						
						
3) search
"--compan-name"   
-Returns known IP rangss assigned to specific companies,
or ones that are known to be used. 
						 
"--host" 		   
-Returns data-pulled from various sources like Shodan
to display possible IP matches to a hostname. Also returns
basic data, like possible matching whois entries etc.


""")
	print menu_text


if __name__ == '__main__':
    rc = main()
    sys.exit( rc )
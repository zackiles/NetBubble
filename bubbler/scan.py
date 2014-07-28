#!/usr/bin/env python
import sys
import os
import glob
from libnmap.process import NmapProcess
from time import sleep
import time
import shutil

from config.bubblerconfig import TARGET_DIR, SCAN_DIR, CONFIG_DIR

def main():
	args = sys.argv
	if not len(args) >= 2:
		print "You have not selected an option."
		print_help()
	if "-h" == args[1] or "--help" == args[1]:
		print_help()	
	elif "--target-name" in args:
		configure_scan(args)
	else:
		print "A target was not specified. Exiting."
		return

def configure_scan(args):
	target_name = args[(args.index("--target-name") + 1)]
	target_base_dir = TARGET_DIR + "/" + target_name
	scan_type = scan_type_to_cmd_string("default.scan") # use default scan profile until override 
	target_file = ""
	split_scan = False
	if "--split-scan" in args:
		split_scan = True
	if not os.path.exists(target_base_dir):
		print "The target list specified was not found. Exiting."
		return
	if not os.listdir(target_base_dir):
		print "The target has no lists. Please flush and rebuild. Exiting."
		return
	if "--scan-type" in args:
		scan_type = scan_type_to_cmd_string(args[(args.index("--scan-type") + 1)])
		if not scan_type:
			print "The scan type requested could not be found. Exiting."
			return
	while os.listdir(target_base_dir):
		target_file = get_next_target_list(target_base_dir)
		if target_file:
			print "Starting scan for list : " + target_file
			num_lines = sum(1 for line in open(target_file))
			print "Number of IP's being scanned : " + str(num_lines)
			if split_scan:
				print "Split scanning mode is activated, you'll be asked to continue after completion"
			scan_output_file = SCAN_DIR + "/temp/" + time.strftime("%Y%m%d%H%M%S") + ".xml"
			if not "--dry-run" in args:
				os.system("sudo nmap " + scan_type + " -iL " + os.path.abspath(target_file) + " -oX " + os.path.abspath(scan_output_file))
			os.remove(target_file)
			shutil.move(scan_output_file, SCAN_DIR)
			if split_scan:
				print "Scan complete for list : " + target_file
				raw_input("Press Enter to start the next list of IP's..." + '\n')
	print "All targets have been scanned. Exiting."
	shutil.rmtree(target_base_dir)

def get_next_target_list(target_base_dir):
	if os.listdir(target_base_dir):
		return min(glob.iglob(target_base_dir + '/*.target*'), key=os.path.getctime)
	else:
		return False	

def scan_type_to_cmd_string(scan_type):
	cmd_dir = CONFIG_DIR + "/scan/"
	cmd_file = "" #unknown for now
	cmd_string = "" #unknown for now
	if os.path.isfile(cmd_dir + scan_type):
		cmd_file = cmd_dir + scan_type
	elif os.path.isfile(cmd_dir + scan_type + ".scan"):
		cmd_file = cmd_dir + scan_type + ".scan"
	else:
		return False
	with open (cmd_file, "r") as filedata:
		cmd_string = filedata.read().replace('\n', '')
	return cmd_string


def print_help():
	menu_text = textwrap.dedent("""
Scan Module for the Bubbler Backend
--------------------------------
This module allows you to run scans based of previously
generated target lists. Since bubbler is mainly concerned
with big-data, it is assumed we'll only be scanning hosts
in large batches. This is not a pentest suite.

To start, read the "target" module documentation about
generating lists of IP's. Create a target, and use that
name to start a scan by doing something like :

"bubbler scan --target-name [mytarget]" 

Currently, --target-name is the only mandatory build option.
When --cmd is not specififed the default scan command is used.

NOTE: If you've used the --split-count in the target module
use the --split-scan option here to complete your scan in 
chunks. After each chunk, it'll ask you if you'd like to
continue. You can exit the program and return to finish
scans at any time. The --target-name will keep working
until all last remaining chunks have been scanned. This way
you can spread out large scans over many days or months if 
needed. You can also use seperate CMD's for each scan chunk.

CAUTION: The default CMD may cause network-strain on yours
and others systems. Please ensure you have permission from
any administrators of the networks you'll be scanning. 
During the testing of this software, abuse complaints were
extremely common. 


----------------------OPTIONS--------------------------

"--target-name"   
-Mandatory to build a scan. Targets can be generated
with the "target" module. Afterwords you can use the
same target name here. Names are case sensitive and may
not contain spaces or special characters.

"--scan-type"
-Scan types are names given to sets of paramters used
in map. They are located in your CONFIG/scan/ directory.
Bubbler comes with a deafult scan profile that'll be used
when --scan-type isn't specified.

"--split-scan"
-If this flag is set, Bubbler will scan each target list
and ask for confirmation before starting the next one.
This is useful for splitting large scans into smaller bits.
The target must have been generated with the --split-count
already set.


""")
	print menu_text


if __name__ == '__main__':
    rc = main()
    sys.exit( rc )

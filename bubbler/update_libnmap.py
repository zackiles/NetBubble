#!/usr/bin/env python
import tarfile
import os
from subprocess import call

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

make_tarfile("python-libnmap.tar.gz", "vendor/python-libnmap")
call(["pip uninstall -y python-libnmap"], shell=True)
call(["pip install ./python-libnmap.tar.gz"], shell=True)
os.remove("python-libnmap.tar.gz")

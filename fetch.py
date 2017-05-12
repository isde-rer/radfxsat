#!/bin/env python
import os, urllib, tarfile
from datetime import datetime

def fetch_foxt0(savedir, url="http://www.amsat.org/tlm/ops/FOX1T0.txt"):
    """Save the satellite reset times"""
    filepath = os.path.join(savedir,"FOX1T0.txt")
    r = urllib.urlretrieve(url, filepath)
    
def fetch_foxdb(savedir, url="http://www.amsat.org/tlm/ao85/FOXDB.tar.gz"):
    """Save the satellite telemetry and return a list a new files"""
    filepath = os.path.join(savedir,"FOXDB.tar.gz")
    r = urllib.urlretrieve(url, filepath)    
    # Only extract new files and return list of new files
    tar = tarfile.open(filepath)
    members = tar.getmembers()
    extractedMembers=[]
    for member in members:
        if not os.path.exists(os.path.join(savedir,member.name)):
            tar.extract(member,savedir)
            extractedMembers.append(member.name)
    tar.close()
    return extractedMembers

def fetch_tle(designator,savedir, url="http://www.amsat.org/amsat/ftp/keps/current/nasa.all"):
    """Save the satellite TLE from the most current set"""
    filename=designator+'.'+datetime.now().strftime("%Y%m%d%H%M%S")+".txt"
    fh = urllib.urlopen(url)
    lines = fh.readlines()
    tle = None
    for i in range(len(lines)):
        if lines[i].strip() == designator:
            tle = ''.join(x for x in lines[i:i+3])
    fh.close()
    fh = open(os.path.join(savedir,filename),'w')
    fh.write(tle)
    fh.close()
    return tle

if __name__ == "__main__":
    fetch_foxt0('./')
    fetch_foxdb('./')
    fetch_tle('AO-85','./')

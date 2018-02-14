#!/bin/env python
import os, urllib, tarfile
from datetime import datetime

def is_tar(filename):
    if filename.endswith('.tar'):
        return True
    if filename.endswith('.tgz'):
        return True
    if filename.endswith('.tar.gz'):
        return True
    return False

def fetch(savedir,filename,url,extract=False):
    """Save the file"""
    print "Fetching %s" % (url)
    if not os.path.exists(savedir):
        raise Exception('%s does not exist'%(savedir))
    filepath=os.path.join(savedir,filename)
    r = urllib.urlretrieve(url,filepath)
    if is_tar(url) and extract:        
        # Only extract new files and return list of new files        
        tar = tarfile.open(filepath)
        members = tar.getmembers()
        extractedMembers=[]
        for member in members:
            if not os.path.exists(os.path.join(savedir,member.name)):
                print "Extracting %s" %(member.name)
                tar.extract(member,savedir)
                extractedMembers.append(member.name)
        tar.close()
        return extractedMembers
    else:
        return [filename]

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
    fetch('./','FOX1T0.txt','http://www.amsat.org/tlm/ops/FOX1T0.txt')
    fetch('./','FOXDB.tgz','http://www.amsat.org/tlm/ao85/FOXDB.tar.gz',extract=True)    
    fetch_tle('AO-85','./')

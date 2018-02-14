import json, datetime
import fox_telem

def dt2googleDate(t):
    d = datetime.datetime.utcfromtimestamp(t)
    return "Date(%d,%d,%d,%d,%d,%d,0)" % (d.year,d.month-1,d.day,d.hour,d.minute,d.second)

print "Reading real time telemetry files..."
rt = fox_telem.Fox1rttelemetry("./FOXDB/Fox1rttelemetry_*.log","./FOX1T0.txt")
print "Reading Vulcan telemetry files..."
vulcan = fox_telem.Vulcan("./FOXDB/Fox1radtelemetry_*.log","./FOX1T0.txt")

# Filter zeros
print "Filtering..."
g=filter(lambda x:  x[2]['upsets'] != 0,vulcan.p)
(tstamp,vuc,lep,remaining)=zip(*g)

# Grab the fields
upset = [ x['upsets'] for x in lep ]
restarts = [ x['restarts'] for x in lep ]
power1 = [ x['exp1_power'] for x in vuc ]
uptime = [ x['uptime'] for x in lep ]
uptime = [ x/3600. for x in uptime ]

# Get data and only keep points where data changes to reduce size
# This will help a JSON file for the web.
(t1,t2,v1,v2,p1,p2) = zip(*fox_telem.changeTimes(tstamp,zip(upset,restarts),zip(power1,uptime,remaining)))
(upset,restarts) = zip(*v2)
(power1,uptime,remaining) = zip(*p2)

# Construct array for google with Date and headers
vulcanData = zip([dt2googleDate(d) for d in t2],upset,restarts,power1,uptime,remaining)
vulcanData.insert(0,[dict({"label": "tstamp", "name": "tstamp", "type": "datetime"}),dict({"label": "upsets", "name": "upsets"}),dict({"label": "restarts", "name": "restarts"}),dict({"label": "power", "name": "power"}),dict({"label": "uptime", "name": "uptime"}),dict({"label": "remaining", "name": "remaining"})] )

print "Saving..."
f=open('vulcan.json','w')
print >>f, "sat_data = '",
json.dump(vulcanData,f)
print >>f, "';"
f.close()

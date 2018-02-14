import json, csv, datetime
import fox_telem

def dt2googleDate(t):
    """Convert a datetime object to a Google Charts Date object"""
    d = datetime.datetime.utcfromtimestamp(t)
    return "Date(%d,%d,%d,%d,%d,%d,0)" % (d.year,d.month-1,d.day,d.hour,d.minute,d.second)

def date2googleDate(t):
    """Convert a date object to a Google Charts Date object"""    
    return "Date(%d,%d,%d,%d,%d,%d,0)" % (d.year,d.month-1,d.day,0,0,0)    

def dt2googleCsvDate(t):
    """Convert a datetime object to a Google Charts Date object"""
    d = datetime.datetime.utcfromtimestamp(t)
    return "%d/%d/%d %d:%d:%d" % (d.year,d.month,d.day,d.hour,d.minute,d.second)

### Assuming there is a FOXDB directory below
print "Reading real time telemetry files..."
rt = fox_telem.Fox1rttelemetry("./AO-85/FOXDB/Fox1rttelemetry_*.log","./AO-85/FOX1T0.txt")
print "Reading Vulcan telemetry files..."
vulcan = fox_telem.Vulcan("./AO-85/FOXDB/Fox1radtelemetry_*.log","./AO-85/FOX1T0.txt")

# Not interested in LEP data that contains 0's. Probably "bad".
print "Filtering..."
g=filter(lambda x:  x[3]['upsets'] != 0,vulcan.p)
(tstamp,dts,vuc,lep,remaining)=zip(*g)

# Grab the fields
upset = [ x['upsets'] for x in lep ]
restarts = [ x['restarts'] for x in lep ]
exp1_power = [ x['exp1_power'] for x in vuc ]
livetime = [x['livetime'] for x in lep ]
uptime = [ x['uptime'] for x in lep ]
uptime = [ x/3600. for x in uptime ]

# Get data and only keep points where data changes to reduce size
# This will help a JSON file for the web.
(t1,t2,v1,v2,p1,p2) = zip(*fox_telem.changeTimes(tstamp,zip(upset,restarts),zip(dts,exp1_power,uptime,livetime)))
(upset,restarts) = zip(*v2)
(dts,exp1_power,uptime,livetime) = zip(*p2)

#vulcanData = zip([dt2googleCsvDate(d) for d in t2],upset,restarts,exp1_power,uptime,livetime)
#f=open('fox1a.csv','w')
#w=csv.writer(f,delimiter=',',quoting=csv.QUOTE_NONE,escapechar='\\')
#w.writerows(vulcanData)
#f.close()

# Construct array for google with Date and headers
vulcanData = zip([dt2googleDate(d) for d in t2],upset,restarts,exp1_power,uptime,livetime)
vulcanData.insert(0,[dict({"label": "tstamp", "name": "tstamp", "type": "datetime"}),dict({"label": "upsets", "name": "upsets"}),dict({"label": "restarts", "name": "restarts"}),dict({"label": "power", "name": "power"}),dict({"label": "uptime", "name": "uptime"}),dict({"label": "livetime", "name": "livetime"})] )

print "Saving..."
f=open('./AO-85/FOXDB.json','w')
print >>f, "sat_data = '",
json.dump(vulcanData,f)
print >>f, "';"
f.close()

# Calculate the weekly bit upset rate
(d2,dlivetime)=fox_telem.deltas(dts,livetime)
(d2,dupset)=fox_telem.deltas(dts,upset)
(wk,dupset_wk)=fox_telem.weekly_aggregate(d2,dupset)
(wk,dlivetime_wk)=fox_telem.weekly_aggregate(d2,dlivetime)

# Filter weeks with no livetime changes
xx=filter(lambda x:  x[1] != 0, zip(dupset_wk,dlivetime_wk))
rate_wk = [ (u/float(l) / (8*2**20) * 86400) for (u,l) in xx ] # [ u/Mb-sec ]

# Construct array for google with Date and headers
vulcanData = zip([date2googleDate(d) for d in wk],rate_wk)
vulcanData.insert(0,[dict({"label": "tstamp", "name": "tstamp", "type": "datetime"}),dict({"label": "rate", "name": "rate"})] )

print "Saving..."
f=open('./AO-85/FOXDB_wk.json','w')
print >>f, "sat_data_wk = '",
json.dump(vulcanData,f)
print >>f, "';"
f.close()

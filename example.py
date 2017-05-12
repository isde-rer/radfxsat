import json
import fox_telem

rt = fox_telem.Fox1rttelemetry("./FOXDB/Fox1rttelemetry_*.log","./FOX1T0.txt")
vulcan = fox_telem.Vulcan("./FOXDB/Fox1radtelemetry_*.log")

#f=open('vulcan.json','w')
#json.dump(vulcanDict,f)
#f.close()

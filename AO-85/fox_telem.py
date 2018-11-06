import numpy as np
import datetime as dt
import glob, struct

epoch = dt.datetime(1970,1,1)

def csv_merge_generator(pattern):
    for file in glob.glob(pattern):
        for line in file:
            yield line

def daily_aggregate(dates,values,fn=lambda x,y: x+y):
    aggregate = dict()
    for d,v in zip(dates,values):
        d = d.date()
        if aggregate.has_key(d):
            aggregate[d] = fn(aggregate[d],v)
        else:
            aggregate[d] = v
    # Convert to lists
    new_dates = sorted(aggregate.keys())
    new_values = [aggregate[d] for d in new_dates]
    return (new_dates,new_values)

def weekly_aggregate(dates,values,fn=lambda x,y: x+y):
    aggregate = dict()
    for d,v in zip(dates,values):
        d = d.date() - dt.timedelta(days=d.date().weekday()+1)
        #week = int(( (d - epoch).total_seconds() / (7*86400) ))
        if aggregate.has_key(d):
            aggregate[d] = fn(aggregate[d],v)
        else:
            aggregate[d] = v
    # Convert to lists
    new_dates = sorted(aggregate.keys())
    new_values = [aggregate[d] for d in new_dates]
    return (new_dates,new_values)

def deltas(dates,values):
    dv = [0]*len(dates)
    for i in range(1,len(dates)):
        dv[i] = values[i]-values[i-1]
    return (dates,dv)

def changeTimes(dt,values,extras=None):
    changeTimes=[]
    if extras == None:
        extras=[None]*len(dt)
    for t in range(1,len(dt)):
        if values[t] != values[t-1]:
            changeTimes.append((dt[t-1],dt[t],values[t-1],values[t],extras[t-1],extras[t]))
    return changeTimes

def exposureWithUpsets(dt,values):
    changeTimes=[]
    for t in range(1,len(dt)):
        d = dt[t] - dt[t-1]
        #dV = values[t] - values[t-1]
        if d.total_seconds() < 6*60:
            changeTimes.append((dt[t-1],dt[t],values[t-1],values[t]))
    return changeTimes
            
class Fox1rttelemetry(object):
    def __init__(self,logfiles,t0file="./FOX1TO.txt"):
        # Read telemetry files
        files=glob.glob(logfiles)
        self.p = np.genfromtxt(files[0],delimiter=',')
        for f in files[1:]:
            d = np.genfromtxt(f,delimiter=',')
            self.p = np.vstack((self.p, d))
        # Read reset times
        fox1T0 = open(t0file,'r')        
        self.reset_tstamp = [ epoch + dt.timedelta(seconds=int(x.strip().split(',')[1])/1000) for x in fox1T0.readlines() ]
        fox1T0.close()
        try:
            self.calculated_tstamp = [ self.reset_tstamp[r] + uptime for r,uptime in zip(self.resets,self.uptime) ]
        except:
            pass
            
    def get_column(self,col):
        return self.p[:,col]

    def utctodatetime(self,t):
        """Is this right??"""
        (year,month,date,hour,minute,second) = [int(x) for x in (t[0:4],t[4:6],t[6:8],t[8:10],t[10:12],t[12:14])]
        return dt.datetime(year,month,date,hour,minute,second)

    @property
    def tstamp(self):        
        return self.calculated_tstamp
        #return [self.utctodatetime('%d'%x) for x in self.get_column(0)]

    @property
    def sn(self): return self.get_column(1)[0]

    @property
    def resets(self): return [int(x) for x in self.get_column(2)]

    @property
    def uptime(self): return [dt.timedelta(seconds=int(x)) for x in self.get_column(3)]

    @property
    def psu_temp(self): return self.get_column(25)/33.6 - 35.68

class Vulcan(object):
    def __init__(self,logfiles,t0file="./FOX1T0.txt"):
        # Read reset times
        fox1T0 = open(t0file,'r')
        self.reset_tstamp = [ epoch + dt.timedelta(seconds=int(x.strip().split(',')[1])/1000) for x in fox1T0.readlines() ]
        fox1T0.close()

        self.data = []                
        # Read telemetry files
        files=glob.glob(logfiles)
        for f in files:
            d = np.genfromtxt(f,delimiter=',',dtype=int) #[int]*5+[np.uint8]*20+[int]*38)
            self.data.append(d)
        self.p = np.vstack(self.data)
        vuc = [self.vuc_telemetry(x[5:15]) for x in self.p]
        lep = [self.lep_telemetry(x[15:25]) for x in self.p]
        remaining = [ sum(x[25:55]) for x in self.p ]        
        
        # Calculate timestamps
        d2 = [ self.reset_tstamp[x[2]] + dt.timedelta(seconds=x[3]) for x in self.p]
        tstamp = [ (d - dt.datetime(1970,1,1)).total_seconds() for d in d2 ]
        fox_resets = [ x[2] for x in self.p ]

        self.p = sorted(zip(tstamp,d2,vuc,lep,remaining), key=lambda x: x[0])
        
        # Filter
        self.p=filter(lambda x: x[2]['state'] == 3 and x[2]['exp1_state'] == 3 and x[4] == 0,self.p)
        print "Records ", len(self.p)
        
        # Fix data
        #self.p = zip(self.d2,vuc,lep)
        for x in self.p:
            # For some reason the counter cleared to 0 on this day
            if x[0] >= 1446188802:
                if x[3]['upsets'] > 0:
                    x[3]['upsets'] = x[3]['upsets'] + 64

    def vuc_telemetry(self,telemetry):
        telemetry = ''.join([chr(x) for x in telemetry])
        (b0,b1,b2,b3,b4,b5,b6,b7,b8,b9) = struct.unpack(">BBBBBBBBBB", telemetry)
        d = dict({'state': (b0>>4)&0x0F,
                  'restarts': (b0<<4)&0xF0 | (b1>>4)&0x0F,
                  'uptime': 16 * ( (b1&0x0F)<<16 | b2<<8 | b3 ),
                  'exp1_state': (b4>>4)&0x0F,
                  'exp2_state': (b4&0x0F),
                  'exp3_state': (b5>>4)&0x0F,
                  'exp4_state': (b5&0x0F),
                  'exp1_power': b6,
                  'exp2_power': b7,
                  'exp3_power': b8,
                  'exp4_power': b9,})
        return d

    def lep_telemetry(self,telemetry):
        telemetry = ''.join([chr(x) for x in telemetry])
        (restarts,up3,up2,up1,livetime,errors) = struct.unpack(">BBBBIH", telemetry)
        d = dict({'restarts': restarts,
                  'uptime': 16*int( up3*2**16 + up2*2**8 + up1),
                  'livetime': livetime,
                  'upsets': errors,
        })
        return d
    
    def get_column(self,col):
        return self.p[:,col]

    @property
    def tstamp(self):
        return [x[0] for x in self.p]    

    @property
    def exp1_state(self):
        return [x[1]['exp1_state'] for x in self.p]
    
    @property
    def lep_upsets(self):
        return [ x[2]['upsets'] for x in self.p]

if __name__ == '__main__':
    import os, sys
    import pickle
    print "Reading real time telemetry files..."
    #rt = Fox1rttelemetry("./FOXDB/Fox1rttelemetry_*.log","./FOX1T0.txt")

    logs = glob.glob("./FOXDB/Fox1radtelemetry_*.log")
    print "Reading Vulcan telemetry files..."
    for f in logs:
        pickleFile=f[:-4]+".pickle"
        if os.path.exists(pickleFile):
            continue
        print "Generating %s" % (pickleFile)
        vulcan = Vulcan(f,"./FOX1T0.txt")
        # Not interested in LEP data that contains 0's. Probably "bad".
        g=filter(lambda x:  x[3]['upsets'] != 0,vulcan.p)
        fh = open(pickleFile,'w')
        pickle.dump(g,fh)
        fh.close()

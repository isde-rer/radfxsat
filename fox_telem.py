import numpy as np
import datetime as dt
import glob

epoch = dt.datetime(1970,1,1)

def csv_merge_generator(pattern):
    for file in glob.glob(pattern):
        for line in file:
            yield line

class Fox1rttelemetry():
    def __init__(self,logfiles,t0file):
        fox1T0 = open(t0file,'r')
        files=glob.glob(logfiles)
        self.p = np.genfromtxt(files[0],delimiter=',')
        for f in files[1:]:
            d = np.genfromtxt(f,delimiter=',')
            self.p = np.vstack((self.p, d))
        self.reset_tstamp = [ epoch + dt.timedelta(seconds=int(x.strip().split(',')[1])/1000) for x in fox1T0.readlines() ]
        self.calculated_tstamp = [ self.reset_tstamp[r] + uptime for r,uptime in zip(self.resets,self.uptime) ]

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

class Vulcan():
    def __init__(self,logfiles):
        files=glob.glob(logfiles)
        self.p = np.genfromtxt(files[0],delimiter=',')
        for f in files[1:]:
            d = np.genfromtxt(f,delimiter=',')
            self.p = np.vstack((self.p, d))

    def get_column(self,col):
        return self.p[:,col]

    @property
    def tstamp(self): return [ epoch + dt.timedelta(seconds=int(x)) for x in self.get_column(0) ]

    @property
    def fox_uptime(self): return self.get_column(4)

    @property
    def vuc_uptime(self): return self.get_column(7)

    @property
    def lep_uptime(self): return self.get_column(17)

    @property
    def fox_resets(self): return self.get_column(3)

    @property
    def vuc_resets(self): return self.get_column(6)

    @property
    def lep_resets(self): return self.get_column(16)

    @property
    def power(self): return [self.get_column(12),self.get_column(13),self.get_column(14),self.get_column(15)]

    @property
    def lep_livetime(self): return self.get_column(18)

    @property
    def lep_upsets(self): return self.get_column(19)

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

def changeTimes(dt,values):
    changeTimes=[]
    for t in range(1,len(dt)):
        if values[t] != values[t-1]:
            changeTimes.append((dt[t-1],dt[t],values[t-1],values[t]))
    return changeTimes

def exposureWithUpsets(dt,values):
    changeTimes=[]
    for t in range(1,len(dt)):
        d = dt[t] - dt[t-1]
        #dV = values[t] - values[t-1]
        if d.total_seconds() < 6*60:
            changeTimes.append((dt[t-1],dt[t],values[t-1],values[t]))
    return changeTimes

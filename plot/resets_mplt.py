import os
import pickle, json, datetime
import fox_telem
import matplotlib
import matplotlib.dates as md
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np

epoch = datetime.datetime(1970,1,1)
mission_start=datetime.date(2017,7, 1) # (2015,10,8) #

fh = open('foxtelem.pickle','r')
g = pickle.load(fh)
fh.close()

# Grab the fields
(tstamp,dts,vuc,lep,remaining)=zip(*g)
upset = [ x['upsets'] for x in lep ]
restarts = [ x['restarts'] for x in lep ]
vrestarts = [ x['restarts'] for x in vuc ]
exp1_power = [ x['exp1_power'] for x in vuc ]
livetime = [x['livetime'] for x in lep ]
uptime = [ x['uptime'] for x in lep ]
uptime = [ x/3600. for x in uptime ]
lep_restarts = ['']*len(restarts)

# Handle roll over
xminindex=0
for i in range(len(restarts)):
    if dts[i].date() <= datetime.date(2015,11,28):
        # Before Nov, resets were all over the place
        restarts[i] = 0
        vrestarts[i] = 0
    else:
        restarts[i] = restarts[i] - 35
        vrestarts[i] = vrestarts[i] - 100
    if dts[i] > datetime.datetime(2017,4,8,12):
        restarts[i] = restarts[i]+256

    # LEP will restart if the VUC does, so isolate
    lep_restarts[i] = restarts[i] - vrestarts[i]
    # Find xmin
    if dts[i].date() <= mission_start:
        xminindex = i
        
def savefig(fig,plt,rootname,width=9,height=5):
    sz=fig.get_size_inches()
    sz[0] = width # in
    sz[1] = height # in
    fig.set_size_inches(sz,forward=True)    
    plt.savefig('%s.png'%rootname,dpi=900)

# Globals
years = md.YearLocator()   # every year
months = md.MonthLocator(interval=1)  # every month
weeks = md.WeekdayLocator(byweekday=md.SU)
days = md.DayLocator()  # every week

fig,axes = plt.subplots(1,1,sharex=True)
ax=axes

#ax.plot(dts, restarts)
#ax.plot(dts, vrestarts)
ax.plot(dts, lep_restarts)
plt.ylim([150,200])
start, end = ax.get_ylim()
#ax.yaxis.set_ticks(np.arange(start, end, 200))
#ax.yaxis.set_ticks(np.arange(start, end, 1000))
ax.set_ylabel("Restarts\n")

# X axis (time)
#xfmt = md.DateFormatter("%b'%y")
#ax.xaxis.set_major_locator(months)
#ax.xaxis.set_major_formatter(xfmt)
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(md.DateFormatter('\n\n%Y'))
ax.xaxis.set_minor_locator(months)
ax.xaxis.set_minor_formatter(md.DateFormatter('%b'))

axes.set_xlim([dts[xminindex],dts[-1]])

plt.setp(axes.xaxis.get_minorticklabels(), rotation=90)
plt.setp(axes.xaxis.get_minorticklabels(), fontsize=7)

plt.subplots_adjust(left=0.17,right=0.95,top=0.95,bottom=0.2)
savefig(fig,plt,'resets',width=5,height=3)
plt.subplots_adjust(left=0.17,right=0.95,top=0.95,bottom=0.35)
savefig(fig,plt,'resets_half',width=5,height=1.5)

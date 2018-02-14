import os
import pickle, json, datetime
import matplotlib
import matplotlib.dates as md
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np

import fox_telem

# Globals
years = md.YearLocator()   # every year
months = md.MonthLocator(interval=1)  # every month
weeks = md.WeekdayLocator(byweekday=md.SU)
days = md.DayLocator()  # every week

mission_start=datetime.date(2017,7, 1) #(2015,10,8) #

# Read datafile
fh = open('foxtelem.pickle','r')
g = pickle.load(fh)
fh.close()
    
# Grab the fields
(tstamp,dts,vuc,lep,remaining)=zip(*g)
upset = [ x['upsets'] for x in lep ]

def savefig(fig,plt,rootname,width=9,height=5):
    sz=fig.get_size_inches()
    sz[0] = width # in
    sz[1] = height # in
    fig.set_size_inches(sz,forward=True)    
    plt.savefig('%s.png'%rootname,dpi=900)


fig,axes = plt.subplots(1,1,sharex=True)
ax=axes

ax.plot(dts, upset)
plt.ylim([0,5600])
start, end = ax.get_ylim()
#ax.yaxis.set_ticks(np.arange(start, end, 200))
ax.yaxis.set_ticks(np.arange(start, end, 1000))
ax.set_ylabel("Upsets\n")

# X axis (time)
#xfmt = md.DateFormatter("%b'%y")
#ax.xaxis.set_major_locator(months)
#ax.xaxis.set_major_formatter(xfmt)
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(md.DateFormatter('\n\n%Y'))
ax.xaxis.set_minor_locator(months)
ax.xaxis.set_minor_formatter(md.DateFormatter('%b'))

axes.set_xlim([dts[0],dts[-1]])

plt.setp(axes.xaxis.get_minorticklabels(), rotation=90)
plt.setp(axes.xaxis.get_minorticklabels(), fontsize=7)

plt.subplots_adjust(left=0.17,right=0.95,top=0.95,bottom=0.2)
savefig(fig,plt,'upsets',width=5,height=3)
plt.subplots_adjust(left=0.17,right=0.95,top=0.95,bottom=0.35)
savefig(fig,plt,'upsets_half',width=5,height=1.5)

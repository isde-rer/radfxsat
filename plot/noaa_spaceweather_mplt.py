import sys, urllib2
import datetime
import matplotlib
import matplotlib.dates as md
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np

def parse_dgd(fname,start=None,end=None):
    f=open(fname,'r')
    dataset = []
    for line in f.readlines():
        # Skip lines with ':' or '#'
        if line.startswith('#') or line.startswith(':'):
            continue
        d = line.split()
        try:
            date = datetime.date(int(d[0]),int(d[1]),int(d[2]))
            if start and date < start:
                continue
            if end and date > end:
                continue
            dataset.append( (date, int(d[21])) )
        except:
            pass
    f.close()
    return dataset

def parse_dpd(fname,start=None,end=None):
    f=open(fname,'r')
    data = []
    for line in f.readlines():
        # Skip lines with ':' or '#'
        if line.startswith('#') or line.startswith(':'):
            continue
        d = line.split()
        try:
            date = datetime.date(int(d[0]),int(d[1]),int(d[2]))
            if start and date < start:
                continue
            if end and date > end:
                continue
            data.append( (date, float(d[3]), float(d[4]), float(d[5])) )
        except:
            pass
    f.close()
    return data

def parse_dsd(fname,start=None,end=None):
    f=open(fname,'r')
    data = []
    for line in f.readlines():
        # Skip lines with ':' or '#'
        if line.startswith('#') or line.startswith(':'):
            continue
        d = line.split()
        try:
            date = datetime.date(int(d[0]),int(d[1]),int(d[2]))
            if start and date < start:
                continue
            if end and date > end:
                continue
            data.append( (date, float(d[3]), d[8] ) )
        except:
            pass
    f.close()
    return data

def plot_dpd(ax,dpd):
    colors=('#ccccff','#8888ff','#0000ff')
    datenums=md.date2num([x[0] for x in dpd])
    p1=ax.fill_between(datenums,1e2,[x[1] for x in dpd],label="> 1 MeV",facecolor=colors[0])
    p10=ax.fill_between(datenums,1e2,[x[2] for x in dpd],label="> 10 MeV",facecolor=colors[1])
    p100=ax.fill_between(datenums,1e2,[x[3] for x in dpd],label="> 100 MeV",facecolor=colors[2])
    ax.set_yscale("log")
    ax.set_ylabel("Proton Flux $\phi$\n(p/cm$^2$-day-sr)")
    p1 = mp.Rectangle((0,0),1,1,fc=colors[0])
    p2 = mp.Rectangle((0,0),1,1,fc=colors[1])
    p3 = mp.Rectangle((0,0),1,1,fc=colors[2])
    ax.legend([p1,p2,p3],["> 1 MeV", "> 10 MeV", "> 100 MeV"],loc='upper left',ncol=3,frameon=False,fontsize=7)

    # Y axis
    start, end = ax.get_ylim()
    plt.ylim([1e3,1e10])
    ax.yaxis.set_ticks([1e4,1e6,1e8])

    # X axis (time)
    #xfmt = md.DateFormatter("%b'%y")
    #ax.xaxis.set_major_locator(months)
    #ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(md.DateFormatter('\n\n%Y'))
    ax.xaxis.set_minor_locator(months)
    ax.xaxis.set_minor_formatter(md.DateFormatter('%b'))
    
def plot_dgd(ax,dgd):
    datenums=md.date2num([x[0] for x in dgd])
    yvals=[x[1] for x in dgd]

    # Color key
    quiet = filter(lambda x: x[1] < 20, dgd)
    small = filter(lambda x: x[1] >= 20 and x[1] < 30, dgd)
    minor = filter(lambda x: x[1] >= 30 and x[1] < 50, dgd)
    moderate = filter(lambda x: x[1] >= 50 and x[1] < 100, dgd)
    strong = filter(lambda x: x[1] >= 100, dgd)

    for d,color in [(quiet,'green'),(small,'yellow'),(minor,'orange'),(moderate,'#AA0000'),(strong,'#0000AA')]:
        dates=[x[0] for x in d]
        datenums=md.date2num(dates)
        yvals=[x[1] for x in d]
        ax.bar(datenums, yvals, width=1, color=color, align='center',edgecolor='none')
    start, end = ax.get_ylim()
    ax.yaxis.set_ticks(np.arange(start,end,20))        
    ax.set_ylabel("Ap\n")

def savefig(fig,plt,rootname,width=9,height=5):
    sz=fig.get_size_inches()
    sz[0] = width # in
    sz[1] = height # in
    fig.set_size_inches(sz,forward=True)    
    plt.savefig('%s.png'%rootname,dpi=900)

def save_for_ppt(fig,plt,rootname):
    savefig(fig,plt,rootname,width=5,height=3)
    savefig(fig,plt,'%s_half'%rootname,width=5,height=1.5)

def save_for_pub(fig,plt,rootname):
    savefig(fig,plt,rootname,width=3,height=3)
    
host="ftp://ftp.swpc.noaa.gov/pub/indices/old_indices"
if __name__ == '__main__':
    import os, sys, glob

    # Globals
    years = md.YearLocator()   # every year
    months = md.MonthLocator(interval=1)  # every month
    weeks = md.WeekdayLocator(byweekday=md.SU)
    days = md.DayLocator()  # every week

    epoch = datetime.datetime(1970,1,1)
    mission_start=datetime.date(2015,10,8) #(2017,7,1)    
    #epoch = datetime.datetime(1970,1,1)
    #mission_start=datetime.date(2015,10,8)

    noaa_dir = sys.argv[1]
    # Read NOAA files
    dgd=[]
    for x in glob.glob('%s/*_DGD.txt'%noaa_dir):
        dgd = dgd + parse_dgd(x,start=mission_start)
    dgd = sorted(dgd,key=lambda x: x[0])
    dsd=[]
    for x in glob.glob('%s/*_DSD.txt'%noaa_dir):        
        dsd = dsd + parse_dsd(x,start=mission_start)
    dsd = sorted(dsd,key=lambda x: x[0])        
    dpd=[]
    for x in glob.glob('%s/*_DPD.txt'%noaa_dir):
        dpd = dpd + parse_dpd(x,start=mission_start)
    dpd = sorted(dpd,key=lambda x: x[0])
    fig,axes = plt.subplots(1,1,sharex=True)

    # Proton fluence plot
    plot_dpd(axes,dpd)#[0])

    # Planetary
    #plot_dgd(axes[1])

    datenums=md.date2num([x[0] for x in dpd])
    axes.set_xlim([datenums[0],datenums[-1]])
    plt.setp(axes.xaxis.get_minorticklabels(), rotation=90)
    plt.setp(axes.xaxis.get_minorticklabels(), fontsize=7)

    plt.subplots_adjust(left=0.17,right=0.95,top=0.95,bottom=0.2)
    savefig(fig,plt,'weather',width=5,height=3)

    plt.subplots_adjust(left=0.17,right=0.95,top=0.95,bottom=0.35)
    savefig(fig,plt,'weather_half',width=5,height=1.5)

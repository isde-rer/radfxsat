import os, sys, argparse
import pickle, json, datetime
import matplotlib
import matplotlib.dates as md
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np

parser = argparse.ArgumentParser(description='Plot')
parser.add_argument('--xdata', dest="xdata", action="store", type=str, default=None, help='xdata name')
parser.add_argument('--xmin', dest="xmin", action="store", type=float, default=None, help='xdata min')
parser.add_argument('--xmax', dest="xmax", action="store", type=float, default=None, help='xdata max')
parser.add_argument('--xlabel', dest="xlabel", action="store", type=str, default='x', help='xdata label')
parser.add_argument('--xlog', dest="xlog", action="store_true", default=False, help='xdata log')

parser.add_argument('--ydata', dest="ydata", action="store", type=str, default=None, help='ydata name')
parser.add_argument('--ymin', dest="ymin", action="store", type=float, default=None, help='ydata min')
parser.add_argument('--ymax', dest="ymax", action="store", type=float, default=None, help='ydata max')
parser.add_argument('--ylabel', dest="ylabel", action="store", type=str, default='y', help='ydata label')
parser.add_argument('--ylog', dest="ylog", action="store_true", default=False, help='ydata log')

parser.add_argument('--output', dest="output", action="store", type=str, default='foo.png', help='Output filename')
parser.add_argument('--dpi', dest="dpi", action="store", type=int, default=90, help='Output DPI')
parser.add_argument('--width', dest="width", action="store", type=float, default=None, help='Output width')
parser.add_argument('--height', dest="height", action="store", type=float, default=None, help='Output height')

args,unknown_args = parser.parse_known_args()
pfile = unknown_args[0]

###############################################################################
# Read datafile
###############################################################################
fh = open(pfile,'r')
data = pickle.load(fh)
fh.close()
#data = {'x': [0,1,2,3,4,5], 'y': [2,3,4,5,6,7]}

###############################################################################
# Retrieve the data
###############################################################################
xdata=[]
ydata=[]

if type(data) == list: # If a list of dicts eg [{'x': 1, 'y': 2},...]
    pass
elif type(data) == dict: # If a dict of lists {'x': [1, ...], 'y': [2, ....]}
    tdata=['']*len(data[args.xdata])
    for t in range(len(data[args.xdata])):
        tdata[t] = dict({args.xdata: data[args.xdata][t],
                         args.ydata: data[args.ydata][t]})
    data = tdata
    if len(xdata) > len(ydata):
        raise Exception("Insufficent ydata")
else:
    raise Exception("Data file must either be a list of dicts or a dict of lists.")

# Ensure that the data are sorted
data = sorted(data, key=lambda x: x[args.xdata])
xdata = [ xx[args.xdata] for xx in data ]
ydata = [ yy[args.ydata] for yy in data ]
    
###############################################################################
#
###############################################################################
fig,axes = plt.subplots(1,1,sharex=True)
ax=axes
ax.plot(xdata,ydata)

###############################################################################
# X axis
###############################################################################
ax.set_xlabel(args.xlabel)
if args.xlog:
    ax.set_xscale("log")
xmin, xmax = ax.get_xlim()
if args.xmin: xmin = args.xmin
if args.xmax: xmax = args.xmax
xspan=xmax-xmin
# Handle dates
if isinstance(xdata[0], datetime.datetime):
    if xspan.days > 3*365:
        ax.xaxis.set_major_locator(md.YearLocator())
        ax.xaxis.set_major_formatter(md.DateFormatter('%Y'))
    elif xspan.days > 60:
        ax.xaxis.set_major_locator(md.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(md.DateFormatter('%b'))
ax.set_xlim([xmin,xmax])

###############################################################################
# Y axis
###############################################################################
ax.set_ylabel(args.ylabel)
if args.ylog:
    ax.set_yscale("log")
ymin, ymax = ax.get_ylim()
if args.ymin: ymin = args.ymin
if args.ymax: ymax = args.ymax
ax.set_ylim([ymin,ymax])

###############################################################################
# Output
###############################################################################
sz=fig.get_size_inches()
if args.width: sz[0] = width # in
if args.height: sz[1] = height # in
fig.set_size_inches(sz,forward=True)
plt.savefig(args.output,dpi=args.dpi)

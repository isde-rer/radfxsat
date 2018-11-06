import os, sys
import pickle

G=[]
for f in sys.argv[1:]:
    f = open(f,'r')
    g=pickle.load(f)
    G = G + g
    f.close()
S = sorted(G, key=lambda x: x[0])    
f=open('foxtelem.pickle','w')
pickle.dump(S,f)
f.close()

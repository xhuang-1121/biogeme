from histogram import *
import sys

# The number of arguments must be at least 2: the name of the file
# with the raw data, and the size of the bin.
f = sys.argv[1]
of = f"_hist_{f}"
print(f)
s = float(sys.argv[2])
print(s)
weightedhistogram(s,f,of)
print(f"File {of} has been generated.")
with open('_hist.gp','w') as gp:
    print('set style data histogram ',file=gp)
    print('set style histogram cluster gap 0',file=gp)
    print('set style fill solid 1.0',file=gp)
    print('plot \'' + of + '\' using 2:xtic(1) t \''+ of + '\'',file=gp)
print("File _hist.gp has been generated.")


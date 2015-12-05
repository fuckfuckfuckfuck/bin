import scanCtp
import numpy as np

def process(ffile):
    ree = []
    ifile = open(ffile, 'r')
    datalines = ifile.readlines()
    for line in datalines:
        re = scanCtp.p.match(line)
        if (re == None): 
            print line
            continue
        re = re.groups() 
        ree.append(re)
    
    re2 = np.zeros((len(ree),1), dtype=('i4'))
# re2 = np.zeros((len(re),8), dtype=('f8'))
# re3 = np.zeros((len(re),1), dtype=('a8,i4'))
    for i in xrange(len(ree)):
        re2[i] = ree[i][0]

    ifile.close()
    return re2


re = process("Test.log")

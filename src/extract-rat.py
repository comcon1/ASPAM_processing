#!/usr/bin/env python3


import sys, getopt, time, os
import numpy as np
import pandas as pd

helpmsg = """
extractrat -i 15.12.2015 -t 9:00 -n 30 -c 1

 -i Start date in dd.mm.YYYY format
 -t Start time in HH:MM format
 -f Input filename
 -o Output filename
 -n Number of days to extract
 -c Channel to extract

Extract the data for the specified rat for the requested period.
"""

time2str = lambda x: \
    time.strftime( '%d.%m.%Y %H:%M', time.localtime(x) )

def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hf:i:t:n:c:o:')
    except getopt.error as msg:
        print(msg)
        print('for help use -h')
        sys.exit(2)

    stdate = sttime = fname = outf =''
    ndays = 0
    nchan = 0

    for o, a in opts:
        if o == '-h':
          print(helpmsg)
          sys.exit(0)
        elif o == '-i':
            stdate = a
        elif o == '-t':
            sttime = a
        elif o == '-n':
            ndays = int(a)
        elif o == '-c':
            nchan = int(a)
        elif o == '-f':
            fname = a
        elif o == '-o':
            outf = a

    if stdate == '' or sttime == '' or ndays == 0 or nchan == 0 or \
            fname == '' or outf == '':
        print('for help use -h')
        sys.exit(2)

    try:
        timestart = time.strptime(stdate + ' ' + sttime, '%d.%m.%Y %H:%M')
        tstampstart = time.mktime(timestart)
    except:
        print('Bad date or time format.')
        sys.exit(3)

    if not os.path.isfile(fname):
        print('Wrong file name.')
        sys.exit(41)

    try:
        print('Reading data from ', fname)
        a = pd.read_csv(fname, header=None, sep='\s+', comment='#').values
    except:
        print('Wrong file format. Check the last line.')
        sys.exit(42)

    if a[:,0].min() > tstampstart:
        TS = time.strftime('%d.%m.%Y %H:%M', time.localtime(a[:,0].min()) )
        print('File starts from %s' % (TS) )
        TS = time.strftime('%d.%m.%Y %H:%M', time.localtime(tstampstart) )
        print('And you request data from %s' % (TS) )
        sys.exit(51)

    tstampstop = min( tstampstart + 24*3600*ndays, a[:,0].max() )
    print( 'Requested interval from %s to %s for rat No. %d.' %
        ( time2str(tstampstart), time2str(tstampstop), nchan ) )

    i = a[:,0].searchsorted(tstampstart)
    j = a[:,0].searchsorted(tstampstop)

    np.savetxt(outf, a[i:j,[0,nchan]], fmt='%d')

    print('Separate rat data saved..')

if __name__ == '__main__':
    main()

time = sys.argv[0]

#!/usr/bin/env python3

import sys, getopt, time, os
sys.path.append('../libdaq')
from libdaq import RotCurveAnalyzer
import pandas as pd
import numpy as np
import matplotlib.pyplot as mpl

helpmsg = """
drawh5sec.py -i rat.xvg -o rat5h.pdf -d 9:00 -n 20:53

 -i Input extracted rat data
 -o Output filename (PDF format)
 -d Day-time start, HH:MM
 -n Night-time start, HH:MM

Calculate overnight 5s -- histograms and plot them.
5.58 - conversion coefficient into m/min.
Extract rat data from the whole datafile with `extract-rat.py` before run.

"""
cset = ['-r', '-g','-b']
time2str = lambda x: \
    time.strftime( '%d.%m.%Y %H:%M', time.localtime(x) )

def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hm:i:o:d:n:')
    except getopt.error as msg:
        print( msg )
        print( 'for help use -h' )
        sys.exit(2)

    infile = outf = daytime = nighttime = ''

    for o, a in opts:
        if o == '-h':
          print( helpmsg )
          sys.exit(0)
        elif o == '-i':
            infile = a
        elif o == '-o':
            outf = a
        elif o == '-d':
            daytime = a
        elif o == '-n':
            nighttime = a

    if infile == '' or outf == '' or daytime == '' or nighttime == '':
        print( 'for help use -h' )
        sys.exit(2)

    try:
        dts = daytime.split(':')
        nts = nighttime.split(':')
        mday = int(dts[0])*60+int(dts[1])
        mnight = int(nts[0])*60+int(nts[1])
        if mday > 60*24 or mnight > 60*24:
            raise ValueError('Numbers in time HH:MM')
    except Exception as e:
        print( e )
        print( 'Problems in time definition.' )
        sys.exit(51)

    try:
        rca = RotCurveAnalyzer(infile)
        print( 'RotCurveAnalyzer started for your data.' )
    except Exception as e:
        print( e )
        print( 'Wrong file format. Check the last line.' )
        sys.exit(42)

    data = rca.getData(-1,-1)
    dayint,lightint,nightint,resday,resli,resni = \
            rca.getFullDayNightData(mday, mday, mnight,
                                rca.df.index[0], rca.df.index[-1])
    ndays = len(nightint)
    print( '=============' )
    print( 'DAY-NIGHT INTERVALS:' )
    for i in range(min(len(nightint),len(resni)) ):
        print( '%s - %s  --  %d' % ( time2str(nightint[i][0]),
                            time2str(nightint[i][1]), resni[i][1] ) )

    '''
    final statistics cycle
    '''

    weekar = []
    for i in range(ndays):
        if i % 7 == 0:
            weekar.append([])
        night_interval_start = max(nightint[i][0], rca.df.index[0])
        night_interval_stop = min(nightint[i][1], rca.df.index[-1])

        _t = int (night_interval_stop - night_interval_start)
        __nighttime = '%02d:%02d' % ( (_t / 3600), ( (_t % 3600) / 60 ) )

        _i = rca.df.index.searchsorted(night_interval_start)
        _j =  rca.df.index.searchsorted(night_interval_stop)
        weekar[-1] += data[_i:_j, 1].tolist()

    for i in range(len(weekar)):
      weekar[i] = np.array(weekar[i])*5.58


    # drawing ..
    print( 'Drawing ..' )
    fig = mpl.figure(figsize=(5,10))
    mpl.subplots_adjust(top=0.9,bottom=0.1,hspace=0.15, left=0.19, right=0.95)
    ax = mpl.subplot(211)
    spints = np.array(range(2,20))*5.58

    fd = open(outf+'.data', 'w')
    fd.write(''.join(map(lambda x: '%-6.1f  ' %x, spints))+'\n')
    for w in range(3):
        h,e = np.histogram(weekar[w], spints, density=True)
        mpl.plot(e[:-1], h, cset[w], label=str(w+1))
        fd.write(''.join(map(lambda x: '%-8.5f' %x, h))+'\n')
    mpl.legend(loc='upper right')
    fd.close()

#    mpl.legend(fontsize=10)
    mpl.ylim(0,0.05)
    #mpl.text(0.05, 0.9, 'Velocities', transform=ax.transAxes)
    mpl.xlim(10,110)
    mpl.xlabel(u'Local velocity, m/min')
    mpl.ylabel(u'Velocity prob. density')

    mpl.savefig(outf)
    print('done.')


if __name__ == '__main__':
    main()



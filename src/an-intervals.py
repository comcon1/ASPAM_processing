#!/usr/bin/env python3

import sys, getopt, time, os
sys.path.append('../libdaq')
from libdaq import RotCurveAnalyzer
import numpy as np

helpmsg = """
an-intervals.py -i rat.xvg -o rat-tbl.txt -d 9:00 -n 20:53 -m 10

 -i Input extracted rat data
 -o Output filename (CSV format)
 -d Day-time start, HH:MM
 -n Night-time start, HH:MM
 -m Minimum retire interval, s
 -t turns-to-meters [0.456 by default]

Calculate per-daytime and per-nightime cumulative statistics for every training
day. Extract rat data from the whole datafile with `extract-rat.py` before run.

"""

time2str = lambda x: \
    time.strftime( '%d.%m.%Y %H:%M', time.localtime(x) )
turnstometers = 0.456

def analyseInterval(starti, stopi, data, day):
    global turnstometers
    '''
    starti - Interval beginning from night start
    stopi  - Interval end from night start
    day    - Day from training start
    data   - Speed array
    '''
    __trainWeek = int(day) / 7 + 1
    __periodStart = starti / 12.
    __periodLength = (stopi - starti) * 5.
    __distance = data[starti:stopi].sum() * float(turnstometers)
    __speed = data[starti:stopi].mean() * float(turnstometers) * 12.
    __energy = (data[starti:stopi]**2).sum() * float(turnstometers)**2 / 25.
    return [__trainWeek, __periodStart, __periodLength, __distance, __speed, __energy]

def main():
    global turnstometers
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hm:i:o:d:n:t')
    except getopt.error as msg:
        print(msg)
        print('for help use -h')
        sys.exit(2)

    infile = outf = daytime = nighttime = ''
    minint = 0

    for o, a in opts:
        if o == '-h':
          print(helpmsg)
          sys.exit(0)
        elif o == '-i':
            infile = a
        elif o == '-o':
            outf = a
        elif o == '-d':
            daytime = a
        elif o == '-n':
            nighttime = a
        elif o == '-m':
            minint = int(a)
        elif o == '-t':
            turnstometers = float(a)

    if infile == '' or outf == '' or daytime == '' or nighttime == '':
        print('for help use -h')
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
        print('Problems in time definition.')
        sys.exit(51)

    try:
        rca = RotCurveAnalyzer(infile)
        print('RotCurveAnalyzer started for your data.')
    except Exception as e:
        print(e)
        print('Wrong file format. Check the last line.')
        sys.exit(42)

    data = rca.getData(-1,-1)
    dayint,lightint,nightint,resday,resli,resni = \
            rca.getFullDayNightData(mday, mday, mnight, rca.df.index[0], rca.df.index[-1])
    ndays = len(nightint)
    print('=============')
    print('DAY-NIGHT INTERVALS:')
    for i in range(len(nightint)):
        print('%s - %s  --  %d' % ( time2str(nightint[i][0]), time2str(nightint[i][1]), resni[i][1] ) )


    '''
    final statistics cycle
    '''

    intArray = []
    for i in range(ndays):
        night_interval_start = max(nightint[i][0], rca.df.index[0])
        night_interval_stop = min(nightint[i][1], rca.df.index[-1])

        _t = int (night_interval_stop - night_interval_start)
        __nighttime = '%02d:%02d' % ( (_t / 3600), ( (_t % 3600) / 60 ) )

        _i = rca.df.index.searchsorted(night_interval_start)
        _j =  rca.df.index.searchsorted(night_interval_stop)
        _dd = data[_i:_j,1]

        __nightdistance = sum(_dd) * float(turnstometers)

        runFlag = False
        retireFlag = False
        runStart = 0
        retireStart = 0
        for x in range(_dd.shape[0]):
            if _dd[x] > 0.01:
                retireFlag = False
            if not runFlag and _dd[x] > 0.01:
                runFlag = True
                runStart = x
            if runFlag and _dd[x] < 0.01:
                if not retireFlag:
                    retireStart = x
                    retireFlag = True
                if retireFlag and (x - retireStart) >= minint/5.:
                    intArray.append(analyseInterval(runStart, retireStart, _dd, i+1))
                    runFlag = False
                    retireFlag = False
        # the last runInterval
        if runFlag:
            intArray.append(analyseInterval(runStart, _dd.shape[0], _dd, i+1))

    print('%d intervals found.' % len(intArray))
    f = open(outf, 'w')
    f.write(infile+'|||||\n')
    f.write('%-7s| %8s| %7s| %8s| %8s| %8s\n' % \
            ('Tr.week', 'Beg.,min', 'Int.T,s', 'S, m', 'V, m/min', 'E, m2/s2') )
    f.write('#------|---------|--------|---------|---------|---------\n')

    # end if night exists
    for a in intArray:
        f.write('%-7d| %8.1f| %7d| %8.2f| %8.2f| %8.2f\n' % tuple(a) )
    # for excel horizontal merge :)
    for i in range(10000-len(intArray)):
        f.write('#------|---------|--------|---------|---------|---------\n')

    f.close()
    print('File %s was written.' % (outf) )

if __name__ == '__main__':
    main()



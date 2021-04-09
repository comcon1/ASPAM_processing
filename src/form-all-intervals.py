#!/usr/bin/env python3

import sys, getopt, time, os
sys.path.append('../libdaq')
from libdaq import RotCurveAnalyzer
import pandas as pd
import numpy as np

helpmsg = """
an-intervals.py -i data.xvg -o rat-tbl.txt -d 9:00 -n 20:53 -m 10

 -i Input global data
 -o Output filename (CSV format)
 -s Start date-time (dd.mm.YYYY HH:MM)
 -p stoP date-time (
 -d Day-time start, HH:MM
 -n Night-time start, HH:MM
 -m Minimum retire interval, s
 -t turns-to-meters [0.456 by default]

@TODO ..write about..
"""

time2str = lambda x: \
    time.strftime( '%d.%m.%Y %H:%M', time.localtime(x) )
turnstometers = 0.456

def convert_arguments(start_dt, stop_dt, fname, outf, night_time, day_time):
    if start_dt == '' or stop_dt == '' or fname == '' or outf == '':
        print('Curcial parameters were not defined')
        print('for help use -h')
        sys.exit(2)

    try:
        timestart = time.strptime(start_dt, '%d.%m.%Y %H:%M')
        tstampstart = time.mktime(timestart)

        timestop = time.strptime(stop_dt, '%d.%m.%Y %H:%M')
        tstampstop = time.mktime(timestop)
    except:
        print('Bad date or time format.')
        sys.exit(3)

    if not os.path.isfile(fname):
        print('Wrong file name.')
        sys.exit(41)

    try:
        dts = day_time.split(':')
        nts = night_time.split(':')
        mday = int(dts[0])*60+int(dts[1])
        mnight = int(nts[0])*60+int(nts[1])
        if mday > 60*24 or mnight > 60*24:
            raise ValueError('Numbers in time HH:MM')
    except Exception as e:
        print( e )
        print('Problems in time definition.')
        sys.exit(51)


    return (tstampstart, tstampstop, mday, mnight)

def crop_dataset(data, tstampstart, tstampstop):
    if data.index[0] > tstampstart:
        TS = time.strftime('%d.%m.%Y %H:%M', time.localtime(data.index[0]) )
        print('File starts from %s' % (TS) )
        TS = time.strftime('%d.%m.%Y %H:%M', time.localtime(tstampstart) )
        print('And you request data from %s' % (TS) )
        sys.exit(51)

    print( 'Requested interval from %s to %s' %
        ( time2str(tstampstart), time2str(tstampstop) ) )

    df = data.loc[tstampstart:tstampstop].copy()

    print( 'Extracted interval from %s to %s' %
        ( time2str(df.index[0]), time2str(df.index[-1]) ) )

    return df

# tborders: rca.df.index min-max
# ndays = len(nightint) ?
def extractIntervals(data, nightint, minint, tborders):

    # auxilary function for formation of interval primary characteristics
    def formInterval(starti, stopi, data, day):
        global turnstometers
        '''
        starti - Interval beginning from night start
        stopi  - Interval end from night start
        day    - Day from training start
        data   - Speed array
        '''
        __trainWeek = int( day / 7 ) + 1
        __periodStart = starti / 12.
        __periodLength = (stopi - starti) * 5.
        __distance = data[starti:stopi].sum() * float(turnstometers)
        __speed = data[starti:stopi].mean() * float(turnstometers) * 12.
        __energy = (data[starti:stopi]**2).sum() * float(turnstometers)**2 / 25.
        return [__trainWeek, __periodStart, __periodLength, __distance, __speed, __energy]

    intArray = []
    for col in data.columns:
        # working with individual animal
        print('Extracting intervals from animal #%d..' % col )
        for i in range(len(nightint)):
            night_interval_start = max(nightint[i][0], tborders[0])
            night_interval_stop = min(nightint[i][1], tborders[1])

            _t = int (night_interval_stop - night_interval_start)
            __nighttime = '%02d:%02d' % ( (_t / 3600), ( (_t % 3600) / 60 ) )

            _dd = data.loc[night_interval_start:night_interval_stop, col]

            __nightdistance = _dd.sum() * float(turnstometers)

            runFlag = False
            retireFlag = False
            runStart = 0
            retireStart = 0
            for x in range(_dd.shape[0]):
                if _dd.iloc[x] > 0.01:
                    retireFlag = False
                if not runFlag and _dd.iloc[x] > 0.01:
                    runFlag = True
                    runStart = x
                if runFlag and _dd.iloc[x] < 0.01:
                    if not retireFlag:
                        retireStart = x
                        retireFlag = True
                    if retireFlag and (x - retireStart) >= minint/5.:
                        intArray.append([col] + formInterval(runStart, retireStart, _dd, i+1))
                        runFlag = False
                        retireFlag = False
            # the last runInterval
            if runFlag:
                intArray.append([col] + formInterval(runStart, _dd.shape[0], _dd, i+1))
        print('Extracted!')
        # end cycle over animals
    return intArray


def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hi:o:s:p:d:n:m:')
    except getopt.error as msg:
        print(msg)
        print('for help use -h')
        sys.exit(2)

    start_dt = stop_dt = fname = outf =''

    for o, a in opts:
        if o == '-h':
          print(helpmsg)
          sys.exit(0)
        elif o == '-s':
            start_dt = a
        elif o == '-p':
            stop_dt = a
        elif o == '-n':
            night_time = a
        elif o == '-d':
            day_time = a
        elif o == '-i':
            fname = a
        elif o == '-o':
            outf = a
        elif o == '-m':
            minint = int(a)

    tstampstart, tstampstop, mday, mnight = convert_arguments(
        start_dt, stop_dt, fname, outf, night_time, day_time)

    try:
        print('Reading data from ', fname)
        a = pd.read_csv(fname, header=None, sep='\s+', comment='#', index_col=0)
        df = crop_dataset(a, tstampstart, tstampstop)
        del(a)
    except Exception as e:
        print(e)
        print('Wrong file format. Check the last line.')
        sys.exit(42)

    print('Data loaded (first 5 lines): ')
    print(df.head())
    print('--')
    rca = RotCurveAnalyzer.fromDF(df[[1]])
    dayint,lightint,nightint,resday,resli,resni = \
            rca.getFullDayNightData(mday, mday, mnight, rca.df.index[0], rca.df.index[-1])


    print('Starting intervals extractions..')
    intervals = extractIntervals(df, nightint, minint, (rca.df.index[0], rca.df.index[-1]) )

    intDF = pd.DataFrame(intervals)
    del(intervals)

    intDF.columns = ['animalNum', 'trainWeek', 'periodStart', 'periodLength',
                        'distance', 'speed', 'energy']
    print(intDF.head())

    intDF.to_csv(outf)

    print('To be continued..')

if __name__ == '__main__':
    main()




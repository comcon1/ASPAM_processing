#!/usr/bin/python

import sys, getopt, time, os
import numpy as np
from ratlib import *

helpmsg = """
get-dn-average.py -i rat.xvg -o rat-tbl.txt

 -i Input extracted rat data
 -o Output filename (CSV format)
 -d Day-time start
 -n Night-time start

Calculate per-daytime and per-nightime cumulative statistics for every training
day. Extract rat data from the whole datafile with `extract-rat.py` before run.

"""

time2str = lambda x: \
    time.strftime( '%d.%m.%Y %H:%M', time.localtime(x) )

def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hi:o:d:n:')
    except getopt.error, msg:
        print msg
        print 'for help use -h'
        sys.exit(2)

    infile = outf = daytime = nighttime = ''

    for o, a in opts:
        if o == '-h':
          print helpmsg
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
        print 'for help use -h'
        sys.exit(2)

    try:
        dts = daytime.split(':')
        nts = nighttime.split(':')
        mday = int(dts[0])*60+int(dts[1])
        mnight = int(nts[0])*60+int(nts[1])
        if mday > 60*24 or mnight > 60*24:
            raise ValueError('Numbers in time HH:MM')
    except Exception as e:
        print e
        print 'Problems in time definition.'
        sys.exit(51)
    
    try:
        rca = dq.RotCurveAnalyzer(infile)
        print 'RotCurveAnalyzer started for your data.'
    except Exception as e:
        print e
        print 'Wrong file format. Check the last line.'
        sys.exit(42)

    data = rca.getData(-1,-1)
    dayint,lightint,nightint,resday,resli,resni = \
            rca.getFullDayNightData(mday, mday, mnight, data['t'][0], data['t'][-1]) 
    ndays = len(resday)
    print '============='
    print 'FULL DAYS:'
    for i in range(ndays):
        print '%d | %s - %s  --  %d' % (i, time2str(dayint[i][0]), time2str(dayint[i][1]), resday[i][1] )
    print '============='
    print 'DAY-LIGHT INTERVALS:'
    for i in range(ndays):
        print '%d | %s - %s  --  %d' % (i, time2str(lightint[i][0]), time2str(lightint[i][1]), resli[i][1] )
    print '============='
    print 'DAY-NIGHT INTERVALS:'
    print len(nightint), len(resni)
    for i in range(min(len(nightint), len(resni)) ):
        print '%d | %s - %s  --  %d' % (i, time2str(nightint[i][0]), time2str(nightint[i][1]), resni[i][1] )


    '''
    final statistics cycle
    '''
    print '''



    '''
    f = open(outf, 'w')
    f.write(infile+'||||||||\n')
    f.write('%11s|%8s|%8s|%8s|%8s|%8s|%8s|%8s|%8s|%8s|%8s\n' % ('Date', \
            'Daylen', 'Day S', 'Day RT', 'Day V', 'Day V0', \
            'Nightlen', 'Night S', 'Night RT', 'Night V', 'Night V0' \
            ) )
    f.write('#-----|------|------|------|-------|-------|-------|------|-------|-------|----\n')

    for i in range(ndays):
        light_interval_start = max(lightint[i][0], data['t'][0])
        light_interval_stop = min(lightint[i][1], data['t'][-1])

        __date = time.strftime('%d.%m.%Y', time.localtime(light_interval_start))

        _t = int(light_interval_stop - light_interval_start)

        __daytime = '%02d:%02d' % ( (_t / 3600), ( (_t % 3600) / 60 ) )

        _i = data['t'].searchsorted(light_interval_start)
        _j = data['t'].searchsorted(light_interval_stop)
        _dd = data['v0'][_i:_j]

        __daydistance = sum(_dd) * float(dq.params.root.turnstometers)

        try:
            __dayspeed = float(__daydistance) / _t * 60.
        except:
            __dayspeed = -1

        _nz = np.nonzero(_dd)[0]
        __dayrspeed = 0. if len(_nz) == 0 else np.mean(_dd[_nz]) \
                    * 12. * float(dq.params.root.turnstometers)
        __dayruntime = _nz.shape[0] / 12. 

        if i >= len(nightint):
            __nightdistance = -1
            __nightspeed = -1
            __nighttime = '0'
            __nightrspeed = -1
        else:
            night_interval_start = max(nightint[i][0], data['t'][0])
            night_interval_stop = min(nightint[i][1], data['t'][-1])


            _t = int (night_interval_stop - night_interval_start)
            __nighttime = '%02d:%02d' % ( (_t / 3600), ( (_t % 3600) / 60 ) )

            _i = data['t'].searchsorted(night_interval_start)
            _j =  data['t'].searchsorted(night_interval_stop)
            _dd = data['v0'][_i:_j]

            __nightdistance = sum(_dd) * float(dq.params.root.turnstometers)

            try:
                __nightspeed = float(__nightdistance) / _t * 60.
            except:
                __nightspeed = -1

            _nz = np.nonzero(_dd)[0]
            __nightrspeed = 0. if len(_nz) == 0 else np.mean(_dd[_nz]) \
                    * 12. * float(dq.params.root.turnstometers)
            __nightruntime = _nz.shape[0] / 12.
        # end if night exists
        f.write('%11s|  %-6s|%8.2f|%8.4f|%8.2f|%8.2f|  %-6s|%8.2f|%8.4f|%8.2f|%8.2f\n' \
                % (__date, \
                 __daytime,   __daydistance,   __dayruntime,   __dayspeed,   __dayrspeed, \
                 __nighttime, __nightdistance, __nightruntime, __nightspeed, __nightrspeed ) )
        f.flush()

    f.close()

if __name__ == '__main__':
    main()

time = sys.argv[0] 

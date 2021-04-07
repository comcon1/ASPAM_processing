#!/usr/bin/env python3
'''Some usefull time hooks basing on a simple time module. '''

import time
import matplotlib.mlab as mlab

def frange(start,stop, step=1.0):
    while start < stop:
        yield start
        start +=step

def upper_day(ut):
    uht = upper_hour(ut)
    gmt = time.localtime(uht)
    if gmt.tm_hour == 0:
        return uht
    else:
        return uht + (24 - gmt.tm_hour)*3600

def upper_hour(ut, mod=1):
    assert(24 % mod == 0) # 24 should divide on mod ticker!
    umt = upper_minute(ut)
    gmt = time.localtime(umt)
    if (gmt.tm_min == 0) and (gmt.tm_hour % mod == 0):
        return umt
    else:
        return upper_hour(umt + (60 - gmt.tm_min)*60, mod)

def upper_minute(ut):
    gmt = time.localtime(ut)
    if gmt.tm_sec == 0:
        return ut
    else:
        return ut + (60 - gmt.tm_sec)

def lower_minute(ut):
    gmt = time.localtime(ut)
    return ut - gmt.tm_sec

def lower_hour(ut):
    lmt = lower_minute(ut)
    gmt = time.localtime(lmt)
    return lmt - 60*gmt.tm_min

def lower_day(ut):
    lht = lower_hour(ut)
    gmt = time.localtime(lht)
    return lht - 3600*gmt.tm_hour

def form_periodic_days(daystartm, startut, stoput):
    '''Form intervals from DAYSTARTM minutes from 00:00 and with length of one
    day. Two timesteps make border. Inclusion scheme is the following:

    -----x[day1----------*-----------][day2---------->
    --->-][day12----------*----------]day13----------

    * marks start and stop of instrument observation.

    If daytime starts, for instance, at 8:00, then end is 7:59 of next day.'''

    umstart = time.localtime(upper_minute(startut))
    startut_m = umstart.tm_hour*60 + umstart.tm_min
    if startut_m == daystartm:
        _begin = time.mktime(umstart)
    elif startut_m < daystartm:
        _begin = time.mktime(umstart) + (daystartm - startut_m)*60 - 3600*24
    elif startut_m > daystartm:
        _begin = time.mktime(umstart) - (startut_m - daystartm)*60

    lmstop = time.localtime(lower_minute(stoput))
    stoput_m = lmstop.tm_hour*60 + lmstop.tm_min
    if stoput_m == daystartm:
        _end = time.mktime(lmstop)-1
    elif stoput_m > daystartm:
        _end = time.mktime(lmstop) - (stoput_m - daystartm)*60+3600*24 -1
    elif stoput_m < daystartm:
        _end = time.mktime(lmstop) + (daystartm - stoput_m)*60

    retar = list(frange(_begin, _end, 24*3600))
    pairs = [ (retar[i], retar[i+1]-1) for i in range(len(retar)-1) ]
    if pairs[0][0] < startut:
        pairs[0] = startut, pairs[0][1]
    if pairs[-1][1] > stoput:
        pairs[-1] = pairs[-1][0], stoput
    # debug print
    print( list(
            map(
             lambda x:
                time.strftime('%d.%m.%y %H:%M', time.localtime(x[0])) +
                " -> " +
                time.strftime(' %d.%m.%y %H:%M', time.localtime(x[1])),
            pairs) ) )
    #TODO: cut beg and end borders to the real borders?
    return pairs

def form_inday_intervals(startm, stopm, daybords):
    thefirst = daybords[0][0]
    thelast = daybords[-1][1]

    if startm < stopm:
        " Definitions: | - border, a - startm, o - stopm; "
        " Building the array of left borders. "
        _int = (stopm-startm)*60

        ltf = time.localtime(thefirst)
        umthefirst = ltf.tm_hour*60 + ltf.tm_min
#        00:00   |   [a       o    23:59
        if umthefirst <= startm:
            _begin = lower_day(thefirst) + startm*60
#        00:00       a       o |  23:59 [
        elif umthefirst >= stopm:
            _begin = upper_day(thefirst) + startm*60
#        "00:00       [a   |   o    23:59"
        elif umthefirst >startm and umthefirst<stopm:
            _begin = lower_day(thefirst) + startm*60

        ltl = time.localtime(thelast)
        umthelast = ltl.tm_hour*60 + ltl.tm_min
#        "[] 00:00   |   a       o    23:59"
        if umthelast <= startm:
            _end = lower_day(thelast)-24*3600+startm*60
#        "00:00       [a       o] |  23:59"
        elif umthelast >= stopm:
            _end = lower_day(thelast) + startm*60
#        "00:00       [a   |   o]    23:59"
        elif umthelast >startm and umthelast<stopm:
            _end = lower_day(thelast) + startm*60
    elif startm > stopm:
        _int = (startm-stopm)*60

        ltf = time.localtime(thefirst)
        umthefirst = ltf.tm_hour*60 + ltf.tm_min
#       [ 00:00   |   o]       a    23:59
        if umthefirst <= stopm:
            _begin = lower_day(thefirst) - 24*3600 + startm*60
#        00:00       o       [a |  23:59 [
        elif umthefirst >= startm:
            _begin = lower_day(thefirst) + startm*60
#        "00:00       o   |   [a    23:59"
        elif umthefirst > stopm and umthefirst < startm:
            _begin = lower_day(thefirst) + startm*60

        ltl = time.localtime(thelast)
        umthelast = ltl.tm_hour*60 + ltl.tm_min
#        "[ 00:00   |   o]       a    23:59"
        if umthelast <= stopm:
            _end = lower_day(thelast)-24*3600+startm*60
#        "00:00       o       [a |  23:59"
        elif umthelast >= startm:
            _end = lower_day(thelast) + startm*60
#        "[ 00:00       o]   |   a    23:59"
        elif umthelast > stopm and umthelast < startm:
            _end = lower_day(thelast) - 24*3600 + startm*60
    else:
        raise AttributeError('Startm should differs from stopm!')

    retar = frange(_begin, _end, 24*3600)
    retar = [ (i,i+_int) for i in retar]
    if len(retar) == 0:
        raise AttributeError('Empty intervals: no data at all')
    " ..Cutting suspending ends.. "
    if retar[0][0] < thefirst:
        retar[0] = thefirst, retar[0][1]
    if retar[-1][1] > thelast:
        retar[-1] = retar[-1][0], thelast

    print ( list (
              map(
                lambda x:
                  time.strftime('%d.%m.%y %H:%M', time.localtime(x[0])) +
                  ' -> ' +
                  time.strftime(' %d.%m.%y %H:%M', time.localtime(x[1])),
                retar) ) )
    return retar


def __form_periodic_intervals(starth, stoph, startut, stoput):
    ''' *DEPRECATED FUNCTION*
    From intervals from STARTH:00 to STOPH:00 over interval between two
    defined unix timestamps. Non-full intervals are not included.'''

    gmstart = time.localtime(startut)
    if stoph > starth:
        _int = (stoph-starth)*3600
        # left border
        uhstart = upper_hour(startut)
        uhstart_hour = time.localtime(uhstart).tm_hour
        if uhstart_hour <= starth:
            left_border = uhstart + (starth - uhstart_hour)*3600
        elif False:
            #TODO: criterion of inclusion of non-full interval
            pass
        else:
            left_border = upper_day(startut) + starth*3600
        # right border
        lba = frange(left_border, stoput, 86400)
        if ( lba[-1] > stoput ):
            lba = lba[:-1]
        if lba[-1] + _int > stoput:
            if False:
                #TODO: criterion of inclusion of non-full interval
                pass
            else:
                lba = lba[:-1]
        # final array generation
        retar = [ (i, i+_int) for i in list(lba) ]

    elif stoph < starth:
        # One should not be embarassed with code duplication because non-full
        # interval criteria are not included yet.
        _int = (24-stoph+starth)*3600
        # -- left border --
        uhstart = upper_hour(startut)
        uhstart_hour = time.localtime(uhstart).tm_hour
        if uhstart_hour <= starth:
            if uhstart_hour < stoph:
                if False:
                    #TODO: criterion of inclusion of non-full interval
                    pass
                else:
                    left_border = uhstart + (starth - uhstart_hour)*3600
            else:
                left_border = uhstart + (starth - uhstart_hour)*3600
        elif False:
            #TODO: criterion of inclusion of non-full interval
            pass
        else:
            left_border = upper_day(startut) + starth*3600
        # right border
        lba = frange(left_border, stoput, 86400)
        if ( lba[-1] > stoput ):
            lba = lba[:-1]
        if lba[-1] + _int > stoput:
            if False:
                #TODO: criterion of inclusion of non-full interval
                pass
            else:
                lba = lba[:-1]
        # final array generation
        retar = [ (i, i+_int) for i in list(lba) ]
    else:
        raise AttributeError('Empty time interval.')

    return retar


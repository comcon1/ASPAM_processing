#!/usr/bin/env python3

import pandas as pd
import numpy as np
import timeutils as tmu
import os


class RawCurveAnalyzer(object):

    def __init__(self, fname):
        print( 'Raw Curve Analyzer starts.' )
        self._fname = fname
        try:
            s = os.stat(self._fname)
        except OSError:
            print( 'No such file!' )
            return
        print( 'Analyzing file: %s (%.1f Kb)' % (self._fname, s.st_size/1024.) )
        self._ldr = pd.read_csv(fname, header=None, sep='\s+', comment='#', index_col=0)

    def __init__(self):
        self._ldr = pd.DataFrame([])

    def getData(self, start, stop, skip=1):
        '''Use -1 for start for the beginning and -1 for stop at the very end.
        One can extract skipped data.'''

        p0 = self._ldr.index.min() if start == -1 else start
        p1 = self._ldr.index.max() if stop == -1 else stop

        intermed = self._ldr.loc[p0:p1,:]
        return intermed[::skip].reset_index().values

    @property
    def df(self):
        return self._ldr

class RotCurveAnalyzer(RawCurveAnalyzer):
    '''Class for analyzing data of rat wheel rotations. '''

    @classmethod
    def fromDF(cls, dataFrame):
        forRet = cls()
        forRet._ldr = dataFrame
        return forRet

    def genPartialSums(self, period='h'):
        '''Generate array of sums over hours and days. '''
        pass

    def getDayNightData(self, daystart, morning, evening, startut, stoput):
        '''Generate array of sums over days, daytimes and nights. ``start'' and
        ``stop'' have the same meaning as in getData() method. Returns arrays
        for every rat with partial sums (days, lights, nights). '''
        data = self.getData(startut, stoput, raw=True)
        print( 'Data shape: ', data.shape )
        days = tmu.form_periodic_days(daystart, startut, stoput)
        # collect daylight data
        light_mask = np.zeros(data.shape[0], dtype=np.int8)
        try:
            daylight = tmu.form_inday_intervals(morning, evening, days)
            for a,b in daylight:
                light_mask[data[:,0].searchsorted(a):data[:,0].searchsorted(b)].fill(1)
        except AttributeError as e:
            print( '** ATTENTION ** ' + str(e) )
        # collect night data
        night_mask = np.zeros(data.shape[0], dtype=np.int8)
        try:
            daynight = tmu.form_inday_intervals(evening, morning, days)
            for a,b in daynight:
                night_mask[data[:,0].searchsorted(a):data[:,0].searchsorted(b)].fill(1)
        except AttributeError as e:
            print( '** ATTENTION ** ' + str(e) )

        resday = np.zeros((len(days),data.shape[1]))
        resday[:,0] = [ tmu.lower_day(i) for i,j in days ]
        resni = np.copy(resday)
        resli = np.copy(resday)
        i = 0
        for a,b in days:
            i0,i1 = data[:,0].searchsorted(a), data[:,0].searchsorted(b)
            print( 'NIGHT MINUTES', night_mask[i0:i1].sum() )
            _da = np.sum(data[i0:i1,1:], axis=0)
            print( 'TOTAL DAY', _da )
            _ni = np.sum(data[i0:i1,1:] * \
                np.vstack([night_mask[i0:i1]]*(data.shape[1]-1)).T, \
                axis=0)
            _li = np.sum(data[i0:i1,1:] * \
                np.vstack([light_mask[i0:i1]]*(data.shape[1]-1)).T, \
                axis=0)
            resday[i,1:] = _da
            resni[i,1:] = _ni
            resli[i,1:] = _li
            i+=1

        return resday, resli, resni


    def getFullDayNightData(self, daystart, morning, evening, startut, stoput):
        '''Generate array of sums over days, daytimes and nights. ``start'' and
        ``stop'' have the same meaning as in getData() method. Returns arrays
        for every rat with partial sums (days, lights, nights). '''
        data = self.getData(startut, stoput)
        print( 'Data shape: ', data.shape )
        days = tmu.form_periodic_days(daystart, startut, stoput)
        # collect daylight data
        light_mask = np.zeros(data.shape[0], dtype=np.int8)
        try:
            daylight = tmu.form_inday_intervals(morning, evening, days)
            for a,b in daylight:
                light_mask[data[:,0].searchsorted(a):data[:,0].searchsorted(b)].fill(1)
        except AttributeError as e:
            print( '** ATTENTION ** ' + str(e) )
        # collect night data
        night_mask = np.zeros(data.shape[0], dtype=np.int8)
        try:
            daynight = tmu.form_inday_intervals(evening, morning, days)
            for a,b in daynight:
                night_mask[data[:,0].searchsorted(a):data[:,0].searchsorted(b)].fill(1)
        except AttributeError as e:
            print( '** ATTENTION ** ' + str(e) )

        resday = np.zeros((len(days),data.shape[1]))
        resday[:,0] = [ tmu.lower_day(i) for i,j in days ]
        resni = np.copy(resday)
        resli = np.copy(resday)
        i = 0
        for a,b in days:
            i0,i1 = data[:,0].searchsorted(a), data[:,0].searchsorted(b)
            print( 'NIGHT MINUTES', night_mask[i0:i1].sum() )
            _da = np.sum(data[i0:i1,1:], axis=0)
            print( 'TOTAL DAY', _da )
            _ni = np.sum(data[i0:i1,1:] * \
                np.vstack([night_mask[i0:i1]]*(data.shape[1]-1)).T, \
                axis=0)
            _li = np.sum(data[i0:i1,1:] * \
                np.vstack([light_mask[i0:i1]]*(data.shape[1]-1)).T, \
                axis=0)
            resday[i,1:] = _da
            resni[i,1:] = _ni
            resli[i,1:] = _li
            i+=1

        return days, daylight, daynight, resday, resli, resni


#!/usr/bin/python

import numpy as np 
from matplotlib.mlab import *
from loader import Loader
from refils import RefillDetector
import timeutils as tmu
import os


class RawCurveAnalyzer(object):

    def __init__(self, fname):
        print 'Raw Curve Analyzer starts.'
        self._fname = fname
        try:
            s = os.stat(self._fname)
        except OSError:
            print 'No such file!'
            return
        print 'Analyzing file: %s (%.1f Kb)' % (self._fname, s.st_size/1024.)
        self._ldr = Loader(self._fname)
        self._rfl = None

    def getData(self, start, stop, skip=1):
        '''Use -1 for start for the beginning and -1 for stop at the very end.
        One can extract skipped data.'''
        p0 = 0 if start == -1 else self._ldr.getPartID(t=start)
        p1 = self._ldr.getNumParts() if stop == -1 else \
            self._ldr.getPartID(t=stop)
        p = np.array([], dtype=self._ldr._p.dtp)
        for j in range(p0, self._ldr.getNumParts()):
            print 'u'
            p0 = self._ldr.getPartNo(j)
            print p.shape, p0.shape
            ind = 0 if not p.shape[0] else \
                    p0['t'][:].searchsorted(p['t'][-1])
            p = np.concatenate( (p, p0[ind::skip] ))
            del p0
        return p

    def getPureData(self, start, stop, skip):
        p = self.getData(start, stop, skip)
        rfl = list(self.detectRefills()[:,0])
        while len(rfl):
            b = rfl.pop()
            a = rfl.pop()
            ia = p['t'].searchsorted(a-20)
            ib = p['t'].searchsorted(b+20)
            p['v'][:ia] -= (p['v'][ia-25:ia-20].mean() - p['v'][ib+20:ib+25].mean())
            print ia,ib
            p = p[list(set(range(p.shape[0]))-set(range(ia,ib)))]
        return p

    @property
    def loader(self):
        return self._ldr

class DrinkCurveAnalyzer(RawCurveAnalyzer):
    
    def detectRefills(self):
        if self._rfl is not None:
            return self._rfl
        rfd = RefillDetector(self._ldr)
        sa, sb = rfd.detect_shifts()
        fls = rfd.determine()
        self._rfl = fls
        return fls

class RotCurveAnalyzer(RawCurveAnalyzer):
    '''Class for analyzing data of rat wheel rotations. '''
        
    _cumdata = None
    _rawdata = None
    
    @property
    def rawdata(self):
        if self._rawdata is None:
            rawdata = self.getData(-1,-1)
            self._rawdata = np.array(rawdata.tolist(), dtype=np.int32)
        return self._rawdata
    
    @property
    def cumdata(self):
        '''Return numerical integral of data'''
        if (self._cumdata is None):
            self._cumdata = np.copy(self.rawdata)
            self._cumdata[:,1:] = np.cumsum(self.rawdata[:,1:], axis=0)
        return self._cumdata

    def genPartialSums(self, period='h'):
        '''Generate array of sums over hours and days. '''
        pass

    def getDayNightData(self, daystart, morning, evening, startut, stoput):
        '''Generate array of sums over days, daytimes and nights. ``start'' and 
        ``stop'' have the same meaning as in getData() method. Returns arrays
        for every rat with partial sums (days, lights, nights). '''
        data = self.getData(startut, stoput, raw=True)
        print 'DDDDDDDD', data.shape
        days = tmu.form_periodic_days(daystart, startut, stoput)
        # collect daylight data
        light_mask = np.zeros(data.shape[0], dtype=np.int8)
        try:
            daylight = tmu.form_inday_intervals(morning, evening, days)
            for a,b in daylight:
                light_mask[data[:,0].searchsorted(a):data[:,0].searchsorted(b)].fill(1)
        except AttributeError as e:
            print '** ATTENTION ** ' + str(e)
        # collect night data
        night_mask = np.zeros(data.shape[0], dtype=np.int8)
        try:
            daynight = tmu.form_inday_intervals(evening, morning, days)
            for a,b in daynight:
                night_mask[data[:,0].searchsorted(a):data[:,0].searchsorted(b)].fill(1)
        except AttributeError as e:
            print '** ATTENTION ** ' + str(e)
        
        resday = np.zeros((len(days),data.shape[1]))
        resday[:,0] = [ tmu.lower_day(i) for i,j in days ]
        resni = np.copy(resday)
        resli = np.copy(resday)
        i = 0
        for a,b in days:
            i0,i1 = data[:,0].searchsorted(a), data[:,0].searchsorted(b)
            print 'NIGHT MINUTES', night_mask[i0:i1].sum()
            _da = np.sum(data[i0:i1,1:], axis=0)
            print 'TOTAL DAY', _da
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
        data = self.getData(startut, stoput, raw=True)
        print 'DDDDDDDD', data.shape
        days = tmu.form_periodic_days(daystart, startut, stoput)
        # collect daylight data
        light_mask = np.zeros(data.shape[0], dtype=np.int8)
        try:
            daylight = tmu.form_inday_intervals(morning, evening, days)
            for a,b in daylight:
                light_mask[data[:,0].searchsorted(a):data[:,0].searchsorted(b)].fill(1)
        except AttributeError as e:
            print '** ATTENTION ** ' + str(e)
        # collect night data
        night_mask = np.zeros(data.shape[0], dtype=np.int8)
        try:
            daynight = tmu.form_inday_intervals(evening, morning, days)
            for a,b in daynight:
                night_mask[data[:,0].searchsorted(a):data[:,0].searchsorted(b)].fill(1)
        except AttributeError as e:
            print '** ATTENTION ** ' + str(e)
        
        resday = np.zeros((len(days),data.shape[1]))
        resday[:,0] = [ tmu.lower_day(i) for i,j in days ]
        resni = np.copy(resday)
        resli = np.copy(resday)
        i = 0
        for a,b in days:
            i0,i1 = data[:,0].searchsorted(a), data[:,0].searchsorted(b)
            print 'NIGHT MINUTES', night_mask[i0:i1].sum()
            _da = np.sum(data[i0:i1,1:], axis=0)
            print 'TOTAL DAY', _da
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


    def getData(self, start, stop, raw=False):
        '''Use -1 for start for the beginning and -1 for stop at the very
        end. raw=True for using simple rectangle matrix format for output.'''
        # avoid skipping when analyzing rotations
        ret = super(RotCurveAnalyzer, self).getData(start, stop, 1)
        if raw:
            ret = np.array(ret.tolist(), dtype=np.int32)
        return ret



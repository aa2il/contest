############################################################################################
#
# cwops.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring CWops mini tests.
#
############################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
############################################################################################

import sys
import datetime
from rig_io.ft_tables import *
from scoring import CONTEST_SCORING
from dx.spot_processing import Station
from pprint import pprint

############################################################################################
    
# Scoring class for CWops mini tests - Inherits the base contest scoring class
class CWOPS_SCORING(CONTEST_SCORING):
 
    def __init__(self,contest='CW Ops Mini-Test'):
        CONTEST_SCORING.__init__(self,contest,mode='CW')
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.sec_cnt = np.zeros((len(self.BANDS)))
        self.calls=set([])

        # Determine contest time - assumes this is dones wihtin a few hours of the contest
        now = datetime.datetime.utcnow()
        #print(now)
        #print(now.hour)
        if now.hour>=19 and now.hour<24:
            self.date0=datetime.datetime(now.year,now.month,now.day,19)
        elif now.hour>=0 and now.hour<19:
            self.date0=datetime.datetime(now.year,now.month,now.day,3)
        else:
            print('CWOPS_SCORING_INIT: Unable to determine contest time')
            sys.exit(0)
            
        self.date1 = self.date0 + datetime.timedelta(hours=1+30/3600.)
    
        

    # Scoring routine for CW Ops Mini Tests
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):
        #print 'rec=',rec
        keys=list(HIST.keys())

        # Pull out relavent entries
        call = rec["call"].upper()
        qth  = rec["qth"].upper()
        if len(qth)>2:
            qth = self.reverse_cut_numbers(qth)
        name = rec["name"].upper()
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        band = rec["band"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        if MY_MODE=='CW':
            mode='CW'
        else:
            print('Invalid mode',MY_MODE)
            sys.exit(1)

        self.calls.add(call)

        if False:
            print('call  =',call)
            print('name  =',name)
            print('qth   =',qth)
            print('calls =',self.calls)

        if not dupe:
            idx2 = self.BANDS.index(band)
            self.sec_cnt[idx2] += 1
            self.nqsos2 += 1;
        else:
            print('??????????????? Dupe?',call)
        #print call,self.nqsos2

        # Check for DX calls
        if call not in keys and '/' in call:
            dx_station = Station(call)
            #pprint(vars(dx_station))
            call2 = dx_station.homecall
            #print(HIST[call])
            #sys.exit(0)
        else:
            call2=call

        # Check against history
        if call2 in keys:
            #print 'hist=',HIST[call2]
            state=HIST[call2]['CWops']
            if len(state)==0:
                state=HIST[call2]['state']
            name9=HIST[call2]['name']
            #print call2,qth,state
            if qth!=state or name!=name9:
                print('\n$$$$$$$$$$ Difference from history $$$$$$$$$$$')
                print(call,':  Current:',qth,name,' - History:',state,name9)
                self.list_all_qsos(call,qsos)
                print(' ')

        else:
            print('\n++++++++++++ Warning - no history for call:',call)
            self.list_all_qsos(call,qsos)
            self.list_similar_calls(call,qsos)

        line='QSO: %5d %2s %10s %4s %-10s      %-10s %-3s %-10s      %-10s %-3s' % \
            (freq_khz,mode,date_off,time_off,MY_CALL,MY_NAME,MY_STATE,call,name,qth)
        
        return line
                        
    # Summary & final tally
    def summary(self):
        
        print('nqsos2=',self.nqsos2)
        print('band count =',self.sec_cnt)
        print('calls =',self.calls)
        mults = len(self.calls)
        print('mults=',mults)
        print('total score=',mults*self.nqsos2)

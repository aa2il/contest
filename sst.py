############################################################################################
#
# sst.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring K1USN Slow Speed Mini Tests (SSTs).
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
from dx.spot_processing import Station  #, Spot, WWV, Comment, ChallengeData

############################################################################################
    
# Scoring class for CWops mini tests - Inherits the base contest scoring class
class SST_SCORING(CONTEST_SCORING):
 
    def __init__(self,P):
        CONTEST_SCORING.__init__(self,'Slow Speed Mini-Test',mode='CW')
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.band_cnt = np.zeros(len(self.BANDS),np.int32)
        self.sec_cnt = np.zeros(len(SST_SECS))

        self.MY_CALL     = P.SETTINGS['MY_CALL']
        self.MY_NAME     = P.SETTINGS['MY_NAME']
        self.MY_STATE    = P.SETTINGS['MY_STATE']
        self.MY_SECTION = P.SETTINGS['MY_SEC']
        
        # Determine contest time - assumes this is dones wihtin a few hours of the contest
        now = datetime.datetime.utcnow()
        if now.strftime('%A') == 'Friday':
            start_time=20
        else:
            start_time=0
        self.date0=datetime.datetime(now.year,now.month,now.day,start_time)
        self.date1 = self.date0 + datetime.timedelta(hours=1+1./60.)

        # Playing with dates
        if False:
            print(now)
            print(now.weekday())
            print(now.strftime('%A'))
            print(self.date0)
            print(self.date1)
            sys.exit(0)

    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_STATE)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SECTION)
                    
    # Scoring routine for Slow Speed Mini Tests
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):
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
        idx = self.BANDS.index(band)
        self.band_cnt[idx] += 1
        
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        if MY_MODE=='CW':
            mode='CW'
        else:
            print('Invalid mode',MY_MODE)
            sys.exit(1)

        dx_station = Station(call)
        #print(dx_station)
        country    = dx_station.country
        qso_points = 1
        if country!='United States' and country!='Canada':
            self.countries.add(country)

        try:
            idx1 = SST_SECS.index(qth)
        except:
            print('\n',rec)
            print(qth,'not in list of of SST Sections - call=',call)
            sys.exit(0)
        self.sec_cnt[idx1] = 1
        
        self.total_points_all += qso_points
        if not dupe:
            self.nqsos2 += 1;
            self.total_points += qso_points
        else:
            print('??????????????? Dupe?',call)
        #print call,self.nqsos2

        # Check against history
        if call in keys:
            #print 'hist=',HIST[call]
            state=HIST[call]['state']
            name9=HIST[call]['name']
            #print call,qth,state
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
            (freq_khz,mode,date_off,time_off,
             self.MY_CALL,self.MY_NAME,self.MY_STATE,
             call,name,qth)
        
        return line
                        
    # Scoring routine for Slow Speed Mini Tests
    def qso_scoring_old(self,rec,dupe,qsos,HIST,MY_MODE):
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

        dx_station = Station(call)
        #print(dx_station)
        country    = dx_station.country
        self.countries.add(country)
        continent  = dx_station.continent
        if country=='United States':
            qso_points = 10
        elif continent=='NA':
            qso_points = 20
        else:
            qso_points = 30
        print(country,continent,qso_points)

        try:
            idx1 = SST_SECS.index(qth)
        except:
            print('\n',rec)
            print(qth,'not in list of of SST Sections - call=',call)
            sys.exit(0)
        self.sec_cnt[idx1] = 1
        
        self.total_points_all += qso_points
        if not dupe:
            self.nqsos2 += 1;
            self.total_points += qso_points
        else:
            print('??????????????? Dupe?',call)
        #print call,self.nqsos2

        # Check against history
        if call in keys:
            #print 'hist=',HIST[call]
            state=HIST[call]['state']
            name9=HIST[call]['name']
            #print call,qth,state
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

        dxcc = list( self.countries )
        dxcc.sort()
        print('Countries:')
        for i in range(len(dxcc)):
            print('   ',dxcc[i])
        print('States/Provs:')
        for i in range(len(SST_SECS)):
            if self.sec_cnt[i]>0:
                print(' ',SST_SECS[i],end='')
        mults = len(dxcc) + int( np.sum(self.sec_cnt) )
    
        print('\nNo. QSOs         =',self.nqsos2,\
              '\t(',self.nqsos1,')')
        print('Band Count       =',list(zip(self.BANDS,self.band_cnt)) )
        print('QSO Points       =',self.total_points,\
              '\t(',self.total_points_all,')')
        #print('State/Prov count =',self.sec_cnt,np.sum(self.sec_cnt))
        print('Mults            =',mults)
        print('Claimed score    =',self.total_points*mults,\
              '\t(',self.total_points_all*mults,')')
    
        

############################################################################################
#
# sst.py - Rev 1.0
# Copyright (C) 2021-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring K1USN Slow Speed Mini Tests (SSTs).
# Also for NS and NCJ Sprints.
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
    
TRAP_ERRORS = False
TRAP_ERRORS = True

############################################################################################
    
# Scoring class for slow-speed mini tests - Inherits the base contest scoring class
class SST_SCORING(CONTEST_SCORING):
 
    def __init__(self,P,contest):
        super().__init__(P,contest,mode='CW')
        #super().__init__(P,'Slow Speed Mini-Test',mode='CW')

        # Inits
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.band_cnt = np.zeros(len(self.BANDS),dtype=np.int32)
        self.sec_cnt = np.zeros((len(SST_SECS),len(self.BANDS)),dtype=np.int32)

        # Determine contest time - assumes this is dones within a few hours of the contest
        # Working on relaxing this restriction because I'm lazy sometimes!
        now = datetime.datetime.utcnow()
        weekday = now.weekday()
        print('now=',now,'\tweekday=',weekday,'\tcontest=',contest)
        if contest=='SPRINT':
            pass
        elif weekday in [1,2,3]:
            # If we finally getting around to running this on Tuesday, Weds or Thurs, roll back date to Monday
            now = now - datetime.timedelta(hours=24*weekday)
        elif weekday in [5,6]:
            # If we finally getting around to running this on Saturday or Sunday, roll back date to Friday
            now = now - datetime.timedelta(hours=24*(weekday-4))

        weekday = now.weekday()
        today = now.strftime('%A')
        if contest=='SPRINT':
            start_hour= 2
            start_min = 30
            duration  = 0.5
        elif today == 'Friday':
            start_hour= 20
            start_min = 0
            duration  = 1
        else:
            start_hour= 0
            start_min = 0
            duration  = 1            
        self.date0=datetime.datetime(now.year,now.month,now.day,start_hour,start_min)
        self.date1 = self.date0 + datetime.timedelta(hours=duration+1./60.)

        # Playing with dates
        if False:
            print('weekday=',weekday)
            print(now)
            print(now.day,now.weekday())
            print(today)
            print('Start:',self.date0)
            print('End:',self.date1)
            sys.exit(0)

        # Name of output file
        self.output_file = self.MY_CALL+'.LOG'
            
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
        if 'qth' in rec:
            qth  = rec["qth"].upper()
        else:
            qth=''
            print('No QTH for',call)
            print(rec)
            return
            sys.exit(0)
        if qth in ['BOND','CHAM','MADN'] and False:
            qth='IL'
            
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
            print('\n*************** WHOOOOOOOPS !!!!!!!!!!!!!!!!!!!!')
            print('\nrec=',rec)
            print('\n',qth,'not in list of of SST Sections - call=',call)
            idx1=None
            if TRAP_ERRORS:
                print('Giving up!\n')
                sys.exit(0)
        if idx1!=None:
            self.sec_cnt[idx1,idx] = 1
        
        self.total_points_all += qso_points
        if not dupe:
            self.nqsos2 += 1;
            self.total_points += qso_points
        else:
            print('??????????????? Dupe?',call)
        #print call,self.nqsos2

        # Sometimes, I'll put a "?" to indicate that I need to review
        if '?' in call+name+qth:
            print('\n??? Check this one again: ???')
            print('call=',call,'\t\tname=',name,'\t\tqth=',qth,'\ttime=',time_off)
            if TRAP_ERRORS:
                sys.exit(0)

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

        # Info for multi-qsos
        exch_in=name+' '+qth
        if call in self.EXCHANGES.keys():
            self.EXCHANGES[call].append(exch_in)
        else:
            self.EXCHANGES[call]=[exch_in]
                        
        # Count no. of CWops guys worked
        self.count_cwops(call,HIST,rec)
                
        line='QSO: %5d %2s %10s %4s %-10s      %-10s %-3s %-10s      %-10s %-3s' % \
            (freq_khz,mode,date_off,time_off,
             self.MY_CALL,self.MY_NAME,self.MY_STATE,
             call,name,qth)
        
        return line
                        
    # Summary & final tally
    def summary(self):

        dxcc = list( self.countries )
        dxcc.sort()
        print('Countries:')
        for i in range(len(dxcc)):
            print('   ',dxcc[i])
            
        print('States/Provs:')
        sec_cnts=np.sum(self.sec_cnt,axis=1)>0
        for i in range(len(SST_SECS)):
            if sec_cnts[i]>0:
                print(' ',SST_SECS[i],end='')
        print('')
                
        mults1 = np.sum(self.sec_cnt,axis=0)
        mults = [int(i) for i in mults1]
        
        print('No. QSOs         =',self.nqsos2,\
              '\t(',self.nqsos1,')')
        print('\nBand\tQSOs\tMults')        
        for i in range(len(self.BANDS)):
            print(self.BANDS[i],'\t',self.band_cnt[i],'\t',mults[i],'\t',end='')
            for j in range(len(SST_SECS)):
                if self.sec_cnt[j,i]>0:
                    print(' ',SST_SECS[j],end='')
            print('')
                
        print('Totals:\t',self.total_points,'\t',sum(mults),'\n')
        
        print('QSO Points       =',self.total_points,\
              '\t(',self.total_points_all,')')
        print('Claimed score    =',self.total_points*sum(mults),\
              '\t(',self.total_points_all*sum(mults),')')

        print('\n# CWops Members =',self.num_cwops,' =',
              int( (100.*self.num_cwops)/self.nqsos1+0.5),'%')
        print('# QSOs Running  =',self.num_running,' =',
              int( (100.*self.num_running)/self.nqsos1+0.5),'%')
        print('# QSOs S&P      =',self.num_sandp,' =',
              int( (100.*self.num_sandp)/self.nqsos1+0.5),'%')
    
        

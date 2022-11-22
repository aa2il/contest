############################################################################################
#
# mst.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring medium Speed mini-tests.
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
from utilities import reverse_cut_numbers

############################################################################################

TRAP_ERRORS = False
#TRAP_ERRORS = True

############################################################################################
    
# Scoring class for CWops CW Open - Inherits the base contest scoring class
class MST_SCORING(CONTEST_SCORING):

    def __init__(self,P,session=None):
        #CONTEST_SCORING.__init__(self,P,'ICWC Medium Speed Test',mode='CW')
        super().__init__(P,'ICWC Medium Speed Test',mode='CW')
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.sec_cnt = np.zeros((len(self.BANDS)),dtype=int)
        self.calls=set([])
        self.last_num_out=0
        self.prev_rec=None

        self.MY_CALL     = P.SETTINGS['MY_CALL']
        self.MY_NAME     = P.SETTINGS['MY_NAME']
        self.MY_SECTION  = P.SETTINGS['MY_SEC']
        self.MY_STATE    = P.SETTINGS['MY_STATE']
        
        # History file
        self.history = os.path.expanduser( '~/Python/history/data/master.csv' )

        # Determine contest time - assumes this is dones within a few hours of the contest
        # Working on relaxing this restriction because I'm lazy sometimes!
        now = datetime.datetime.utcnow()
        weekday = now.weekday()
        print('now=',now,'\t\t','weekday=',weekday)
        if weekday!=0:
            # If we finally getting around to running this on any day but Mon, roll back date to Mon
            # Note - Monday is day 0
            if weekday==1:
                weekday-=1
            elif session==3:
                weekday-=1
            now = now - datetime.timedelta(hours=24*(weekday-0))
        print('now2=',now,'\t\t','weekday=',weekday)

        day   = now.day
        hour  = now.hour
        today = now.strftime('%A')

        if session!=None:
            start_time=session
            if today=='Tuesday' and session>3:
                # Must be looking at Monday's session
                day-=1
        elif today=='Tuesday':
            # Must be looking at previous session
            if hour<3:
                day-=1
                start_time=19
            else:
                start_time=3
        elif hour>=19 and hour<24:
            start_time=19
        elif hour>=0 and hour<19:
            start_time=3
        else:
            print('MST_SCORING_INIT: Unable to determine contest time')
            sys.exit(0)
        self.date0=datetime.datetime(now.year,now.month,day,start_time)
            
        self.date1 = self.date0 + datetime.timedelta(hours=1+30/3600.)
        if False:
            print('session=',session)
            print('now=',now)
            print('today=',today)
            print('weekday=',weekday)
            print('hour=',hour)
            print('date0=',self.date0)
            print('date1=',self.date1)
            sys.exit(0)

        # Name of output file
        self.output_file = self.MY_CALL+'.LOG'
    
    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_STATE)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SECTION)

    # Scoring routine for CW Ops CW Open
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):
        #print 'rec=',rec
        keys=list(HIST.keys())

        # Pull out relavent entries
        call = rec["call"].upper()
        rx   = rec["srx_string"].strip().upper()
        a    = rx.split(',')
        try:
            num_in = str( int( a[0] ) )
        except:
            num_in = reverse_cut_numbers( a[0] )
            print('\nHmmmmmmmmmmm - problem with number in:',call,a[1],num_in)
        name_in = a[1]

        if TRAP_ERRORS and '?' in str(num_in)+name_in:
            print(rec)
            print('\nTrapped error - exiting')
            sys.exit(0)
        
        tx   = rec["stx_string"].strip().upper()
        b    = tx.split(',')
        num_out  = int( reverse_cut_numbers( b[0] ) )
        name_out = b[1]
        my_call = rec["station_callsign"].strip().upper()
                
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        band = rec["band"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        if num_out-self.last_num_out!=1 and self.last_num_out>0: 
            print('\n???????? Jump in serial out ???????',self.last_num_out,'to',num_out)
            print(self.prev_rec)
            print(rec)
            if TRAP_ERRORS:
                print('\nTrapped error - exiting')
                sys.exit(0)
            
        self.last_num_out = num_out
        self.prev_rec=rec

        if MY_MODE=='CW':
            mode='CW'
        else:
            print('Invalid mode',MY_MODE)
            sys.exit(1)

        self.calls.add(call)

        if False:
            print('call   =',call)
            print('serial =',num_in)
            print('name   =',name_in)
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
            name9=HIST[call2]['name']
            #print call2,qth,state
            if name_in!=name9:
                print('\n$$$$$$$$$$ Difference from history $$$$$$$$$$$')
                print(call,':  Current:',name_in,' - History:',name9)
                #self.list_all_qsos(call,qsos)
                print(' ')

        else:
            print('\n++++++++++++ Warning - no history for call:',call)
            #self.list_all_qsos(call,qsos)
            self.list_similar_calls(call,qsos)

        # Info for multi-qsos
        exch_in=name_in
        if call in self.EXCHANGES.keys():
            self.EXCHANGES[call].append(exch_in)
        else:
            self.EXCHANGES[call]=[exch_in]
                
#000000000111111111122222222223333333333444444444455555555556666666666777777777788
#123456789012345678901234567890123456789012345678901234567890123456789012345678901
#                              -----info sent------       -----info rcvd------
#QSO: freq  mo date       time  call      nr   ex1        call       nr   name
#QSO: ***** ** yyyy-mm-dd nnnn ********** nnnn aaaaaaaaaa ********** nnnn aaaaaaaaaa
#QSO: 14042 CW 2011-09-20 0000 N5TJ          1 JEFF       N6TR       1    TREE

        line='QSO: %5d %2s %10s %4s %-10s %4s %-11s %-10s %4s %-11s' % \
            (freq_khz,mode,date_off,time_off,
             my_call,num_out,name_out,
             call,num_in,name_in)
        
        return line
                        
    # Summary & final tally
    def summary(self):
        
        print('\nnqsos1=',self.nqsos1)
        print('nqsos2=',self.nqsos2)
        #print('band count =',self.sec_cnt)
        for i in range(len(self.BANDS)):
            print(self.BANDS[i],'\t',self.sec_cnt[i])
        print('calls =',self.calls)
        mults = len(self.calls)
        print('mults=',mults)
        print('total score=',mults*self.nqsos2)

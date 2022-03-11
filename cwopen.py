############################################################################################
#
# cwopen.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring CWops CW Open.
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
TRAP_ERRORS = True

############################################################################################
    
# Scoring class for CWops CW Open - Inherits the base contest scoring class
class CWOPEN_SCORING(CONTEST_SCORING):

    def __init__(self,P):
        CONTEST_SCORING.__init__(self,'CW-OPEN',mode='CW')
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.sec_cnt = np.zeros((len(self.BANDS)))
        self.calls=set([])
        self.last_num_out=0

        self.MY_CALL     = P.SETTINGS['MY_CALL']
        self.MY_NAME     = P.SETTINGS['MY_NAME']
        self.MY_SECTION  = P.SETTINGS['MY_SEC']
        self.MY_STATE    = P.SETTINGS['MY_STATE']
        
        # History file
        self.history = os.path.expanduser( '~/Python/history/data/master.csv' )
        
        # Determine contest date/time - first Sat in Sept.
        now = datetime.datetime.utcnow()
        day1=datetime.date(now.year,9,1).weekday()                     # Day of week of 1st of month 0=Monday, 6=Sunday
        sat2=1 + ((5-day1) % 7)                                        # Day no. for 1st Saturday = 1 since day1 is the 1st of the month
                                                                       #    plus no. days until 1st Saturday (day 5)
        start_time=0                                                   # 1st session is 0000-0400 UTC                           
        self.date0=datetime.datetime(now.year,9,sat2,start_time)       # Need to add more code for other sessions next year
        self.date1 = self.date0 + datetime.timedelta(hours=4)          # Each session is 4hrs long
        print('day1=',day1,'\tsat2=',sat2,'\tdate0=',self.date0)
        #sys.exit(0)

        # Manual override
        if False:
            self.date0 = datetime.datetime.strptime( "20210904 0000" , "%Y%m%d %H%M")  # Start of contest
            self.date1 = self.date0 + datetime.timedelta(hours=4)
        
    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_STATE)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SECTION)

    # Scoring routine for CW Ops CW Open
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):
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
            print('Hmmmmmmmmmmm:',call,a[0],num_in)
        name_in = a[1]
        #name = rec["name"].upper()

        if TRAP_ERRORS and '?' in str(num_in)+name_in:
            print(rec)
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

        if TRAP_ERRORS and num_out-self.last_num_out!=1:
            print('Jump in serial out???',self.last_num_out,num_out)
            sys.exit(0)
        else:
            self.last_num_out = num_out

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
                self.list_all_qsos(call,qsos)
                print(' ')

        else:
            print('\n++++++++++++ Warning - no history for call:',call)
            self.list_all_qsos(call,qsos)
            self.list_similar_calls(call,qsos)

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
        
        print('nqsos2=',self.nqsos2)
        print('band count =',self.sec_cnt)
        print('calls =',self.calls)
        mults = len(self.calls)
        print('mults=',mults)
        print('total score=',mults*self.nqsos2)

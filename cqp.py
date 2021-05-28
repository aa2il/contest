############################################################################################
#
# cqp.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring Commie-fornia QSO Party.
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
from dx.spot_processing import Station, Spot, WWV, Comment, ChallengeData
from pprint import pprint

############################################################################################

CQP_MULTS  = STATES + ['MR', 'QC', 'ON', 'MB', 'SK', 'AB', 'BC', 'NT']
CQP_STATES = STATES + PROVINCES + CA_COUNTIES + ['MR','DX']

# Scoring class for CQP - Inherits the base contest scoring class
class CQP_SCORING(CONTEST_SCORING):
 
    def __init__(self,contest):
        CONTEST_SCORING.__init__(self,contest)
        print('CQP Scoring Init')
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.sec_cnt = np.zeros(len(CQP_MULTS))
        self.calls = []

    # Scoring routine for CQP
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):
        #print('rec=',rec)
        keys=list(HIST.keys())
        #sys.exit(0)

        # Pull out relavent entries
        call = rec["call"].upper()
        rx   = rec["srx_string"].strip().upper()
        a    = rx.split(',') 
        #num_in = self.reverse_cut_numbers( a[0] )
        num_in = int( a[0] )
        qth_in = a[1]
        my_call = rec["station_callsign"].strip().upper()

        tx   = rec["stx_string"].strip().upper()
        b    = tx.split(',')
        num_out = self.reverse_cut_numbers( b[0] )
        qth_out = b[1]
        
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        band = rec["band"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        if MY_MODE=='CW':
            mode='CW'
        else:
            print('Invalid mode',MY_MODE)
            sys.exit(1)

        if False:
            print('rec=',rec)
            pprint(vars(dx_station))
            print('call     =',call)
            print('prefix   =',prefix)
            print('exch out =',num_out,qth_out)
            print('exch in  =',num_in,qth_in)
            #sys,exit(0)

        # Determine multipliers
        if qth_in in CA_COUNTIES:
            qth='CA'
        elif qth_in in ['NB', 'NL', 'NS', 'PE']:
            qth_in='MR'
            qth='MR'
        else:
            qth=qth_in
            
        if not dupe:
            try:
                idx1 = CQP_MULTS.index(qth)
                self.sec_cnt[idx1] += 1
                self.nqsos2 += 1;
                self.calls.append(call)
            except:
                print('\n$$$$$$$$$$$$$$$$$$$$$$',self.nqsos2)
                print(qth,' not found in list of CQP sections')
                print(rec)
                print('History=',call,HIST[call])
                print('$$$$$$$$$$$$$$$$$$$$$$')
                sys.exit(0)
        
        # Error checking
        if qth_in not in CQP_STATES:
            print('rec=',rec)
            print('call=',call)
            print('Received qth '+qth_in+' not recognized - srx=',rx)
            print('History=',HIST[call])
            sys.exit(0)

        # Compare to history
        if call in keys:
            if qth=='CA':
                state=HIST[call]['county']
            else:
                state=HIST[call]['state']
            #print call,qth,state
            if qth_in!=state:
                print('\n$$$$$$$$$$ Difference from history $$$$$$$$$$$')
                print(call,':  Current:',qth,' - History:',state)
                print('History=',call,HIST[call])
                self.list_all_qsos(call,qsos)
                print(' ')

        else:
            print('\n++++++++++++ Warning - no history for call:',call)
            self.list_all_qsos(call,qsos)
            #self.list_similar_calls(call,qsos)

            #print 'dist=',similar('K5WA','N5WA')
            #sys.exit(0)
        
#000000000111111111122222222223333333333444444444455555555556666666666777777777788
#123456789012345678901234567890123456789012345678901234567890123456789012345678901
#                              -----info sent------ -----info rcvd------
#QSO: freq  mo date       time call       nr   ex1  call       nr   ex1
#QSO: ***** ** yyyy-mm-dd nnnn ********** nnnn aaaa ********** nnnn aaaa 
#QSO: 28050 CW 2012-10-06 1600 K6AAA         1 SCLA W1AAA         1 ME 
#QSO: 28450 PH 2012-10-06 1601 K6AAA         2 SCLA K6ZZZ         2 AMAD 

        line='QSO: %5d %2s %10s %4s %-10s %4s %-4s %-10s %4s %-4s' % \
            (freq_khz,mode,date_off,time_off,
             my_call,num_out,qth_out,
             call,num_in,qth_in)
        
        return line
                        
    # Summary & final tally
    def summary(self):

        print('\nNo. raw QSOS (nqsos1)    =\t',self.nqsos1)
        print(  'No. unique QSOS (nqsos2) =\t',self.nqsos2)
        mults=0
        for i in range(len(self.sec_cnt)):
            print(i,'\t',CQP_MULTS[i],'\t',int(self.sec_cnt[i]))
            if self.sec_cnt[i]>0:
                mults += 1
        print('Multipiers    =\t',mults)
        print('Claimed Score =\t',3*mults*self.nqsos2)

        uniques = np.unique( self.calls )
        uniques.sort()
        print('\nThere were',len(uniques),'unique calls:\n',uniques)

        print('\nThe SEQUOIA Challenge:')
        for ch in ['S','E','Q','U','O','I','A']:
            print(ch,':\t',end=' ')
            for w in ['K','N','W']:
                call2=w+'6'+ch
                if call2 in uniques:
                    print(call2,'\t',end=' ')
                else:
                    print('\t',end=' ')
            print(' ')
            

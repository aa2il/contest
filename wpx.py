############################################################################################
#
# wpx.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring CQ WPX CW contest.
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

############################################################################################
    
# Scoring class for CQ WPX - Inherits the base contest scoring class
# Eventaully, all contests should use this model 
class CQ_WPX_SCORING(CONTEST_SCORING):
 
    def __init__(self,contest):
        CONTEST_SCORING.__init__(self,contest)
        print('FD Scoring Init')
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.sec_cnt = np.zeros((len(self.BANDS)))
        self.calls=set([])

    # Scoring routine for CQ WPX
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):
        #print 'rec=',rec
        #sys.exit(0)

        # Pull out relavent entries
        call = rec["call"].upper()
        rx   = rec["srx_string"].strip().upper()
        a    = rx.split(' ')                    # Note - there was a bug in 2019 - this should be a comma
        rst_in = self.reverse_cut_numbers( a[0] )
        num_in = self.reverse_cut_numbers( a[1] )
        tx   = rec["stx_string"].strip().upper()
        b    = tx.split(',')
        rst_out = self.reverse_cut_numbers( b[0] )
        num_out = self.reverse_cut_numbers( b[1] )
        
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        band = rec["band"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        if MY_MODE=='CW':
            mode='CW'
        else:
            print('Invalid mode',MY_MODE)
            sys.exit(1)

        # Determine multipliers
        dx_station = Station(call)
        prefix = dx_station.call_prefix + dx_station.call_number
        self.calls.add(prefix)

        if False:
            print('rec=',rec)
            pprint(vars(dx_station))
            print('call     =',call)
            print('prefix   =',prefix)
            print('exch out =',rst_out,num_out)
            print('exch in  =',rst_in,num_in)
            #sys,exit(0)

        if not dupe:
            idx2 = self.BANDS.index(band)
            self.sec_cnt[idx2] += 1
            self.nqsos2 += 1;
            
#000000000111111111122222222223333333333444444444455555555556666666666777777777788
#123456789012345678901234567890123456789012345678901234567890123456789012345678901
#                               --------info sent------- -------info rcvd--------
#QSO: freq  mo date       time call          rst exch   call          rst exch   t
#QSO: ***** ** yyyy-mm-dd nnnn ************* nnn ****** ************* nnn ****** n
#QSO:  3799 PH 1999-03-06 0711 HC8N          59  001    W1AW          59  001    0
        line='QSO: %5d %2s %10s %4s %-13s %-3s %-6s %-13s      %-3s %-6s' % \
            (freq_khz,mode,date_off,time_off,
             MY_CALL,rst_out,num_out,
             call,rst_in,num_in)
        
        return line
                        
    # Summary & final tally
    def summary(self):

        print('nqsos2=',self.nqsos2)
        print('band count =',self.sec_cnt)
        print('prefixes =',sorted( self.calls ))
        mults = len(self.calls)
        print('mults=',mults)
        print('total score=',mults*self.nqsos2)
            

############################################################################################
#
# iaru.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring IARU HF contest.
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

TRAP_ERRORS = False
TRAP_ERRORS = True

############################################################################################
    
# Scoring class for IARU HF contest - Inherits the base contest scoring class
# Eventaully, all contests should use this model 
class IARU_HF_SCORING(CONTEST_SCORING):
 
    def __init__(self,P):
        CONTEST_SCORING.__init__(self,'IARU-HF',mode='CW')
        print('IARU HF Scoring Init')

        self.MY_CALL     = P.SETTINGS['MY_CALL']
        self.MY_ITU_ZONE = P.SETTINGS['MY_ITU_ZONE']

        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.NQSOS = OrderedDict()
        zones = []
        for b in self.BANDS:
            zones.append((b,set([])))
            self.NQSOS[b]=0
        self.ZONES = OrderedDict(zones)
        self.nqsos=0

        # Determine contest time - assumes this is dones wihtin a few hours of the contest
        now = datetime.datetime.utcnow()
        #print(now)
        #date0 = datetime.datetime.strptime( "20210710 1200" , "%Y%m%d %H%M")  # Start of contest
        day=10
        self.date0=datetime.datetime(now.year,now.month,day,12)
        self.date1 = self.date0 + datetime.timedelta(hours=24)
        
    # Scoring routine for IARU HF
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):
        #print('rec=',rec)
        keys=list(HIST.keys())
        #print(keys)
        #sys.exit(0)

        # Pull out relavent entries
        call = rec["call"].upper()
        rx   = rec["srx_string"].strip().upper()
        a    = rx.split(',')
        rst_in = self.reverse_cut_numbers( a[0] )
        if len(a[1])<=2:
            num_in = self.reverse_cut_numbers( a[1] , 2)
        else:
            num_in = a[1]
        if num_in.isdigit():
            zone = int(num_in)
        else:
            zone = 0                    # Presumably, an HQ station
            
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
            print('Invalid mode',MY_MODE)          # Need to add SSB if I ever do it!
            sys.exit(1)

        # Some simple checks
        if rst_in!='599':
            print('*** WARNING *** RST in =',rst_in)
            if TRAP_ERRORS:
                sys.exit(0)

        # Some error checking
        dx_station = Station(call)
        if len(num_in)==0 or zone>75:
            print('Houston, we have problem - invalid zone')
            print('rec=',rec)
            pprint(vars(dx_station))
            print('call     =',call)
            print('exch out =',rst_out,num_out)
            print('exch in  =',rst_in,num_in)
            if TRAP_ERRORS:
                sys,exit(0)
        if dx_station.ituz!=zone and False:
            print('\nWarning - ITU Zone mismatch')
            print('rec=',rec)
            print('call     =',call)
            print('Zone     =',dx_station.ituz,zone)
            print(' ')
            sys,exit(0)

        # Determine multipliers
        self.nqsos+=1
        SPECIAL_CALLS=['TO5GR']
        if not dupe:
            if zone==self.MY_ITU_ZONE or zone==0:
                qso_points = 1
            elif dx_station.continent=='NA' or call in SPECIAL_CALLS:
                qso_points = 3
            elif dx_station.continent in ['SA','EU','OC','AF']:
                qso_points = 5
            else:
                print('\n*** IARU HF: Not Sure what to do with this??!! ***')
                pprint(vars(dx_station))
                sys.exit(0)
            
            self.ZONES[band].add(num_in)
            self.nqsos2 += 1;
            self.total_points += qso_points

#                              --------info sent------- -------info rcvd--------
#QSO: freq  mo date       time call          rst exch   call          rst exch  
#QSO: ***** ** yyyy-mm-dd nnnn ************* nnn ****** ************* nnn ******
#QSO: 21303 PH 1999-07-10 1202 K5TR          59  07     NU1AW         59  IARU
#QSO: 14199 PH 1999-07-10 1202 K5TR          59  07     K1JN          59  08
#0000000001111111111222222222233333333334444444444555555555566666666667777777777
#1234567890123456789012345678901234567890123456789012345678901234567890123456789
        line='QSO: %5d %2s %10s %4s %-13s %-3s %-6s %-13s      %-3s %-6s' % \
            (freq_khz,mode,date_off,time_off,
             self.MY_CALL,rst_out,num_out,
             call,rst_in,num_in)

        # Check against history
        if call in keys:
            #print('hist=',HIST[call])
            ITUz=HIST[call]['ITUz']
            #if int(ITUz)!=zone:
            if not ITUz in [str(zone),num_in]:
                print('\n$$$$$$$$$$ Difference from history $$$$$$$$$$$')
                print(call,':  Current:',num_in,' - History:',ITUz)
                self.list_all_qsos(call,qsos)
                print(' ')
                if not ITUz.isdigit():
                    sys.exit(0)

        else:
            print('\n++++++++++++ Warning - no history for call:',call)
            self.list_all_qsos(call,qsos)
            self.list_similar_calls(call,qsos)
            if dx_station.ituz!=zone and not call in SPECIAL_CALLS:
                print('Zone     =',dx_station.ituz,zone)
                pprint(vars(dx_station))
                sys.exit(0)
        
        return line
                        
    # Summary & final tally
    def summary(self):

        print('ZONES:',self.ZONES)
        mults=0
        for b in self.BANDS:
            zones = list( self.ZONES[b] )
            zones.sort()
            print('\n',b,'Zones:',zones)
            print(' No. QSOs,Mults:',self.NQSOS[b],len(zones))
            mults+=len(zones)

        print('\nNo. QSOs      =',self.nqsos)
        print('No. Uniques   =',self.nqsos2)
        print('QSO points    =',self.total_points)
        print('Multipliers   =',mults)
        print('Claimed Score =',self.total_points*mults)
        
# From log submission        
#QSOs in Log:	163
#Raw Score: 431 Qpts x 55 Mults = 23,705 (161 QSOs)



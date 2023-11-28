############################################################################################
#
# scoring.py - Rev 1.0
# Copyright (C) 2021-3 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Base class/routines for scoring contest results.
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
import re
from collections import OrderedDict
import numpy as np
from difflib import SequenceMatcher

# Need this for Makrothen and WW-DIGI - it was broke but looking up error helped to fix it
#from pyhamtools.locator import calculate_distance
####from pyhamtools import LookupLib, Callinfo

from dx.spot_processing import Station, Spot, WWV, Comment, ChallengeData
from pprint import pprint
from scp import *

############################################################################################

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

############################################################################################

# Base contest scorer class
class CONTEST_SCORING:
    def __init__(self,P,contest,mode=None):
        #print('Base Class Init')
        
        self.contest = contest
        self.my_mode = mode
        self.category_band='ALL'
        
        self.total_score = 0
        self.total_km    = 0
        self.max_km      = 0
        self.nskipped    = 0
        self.ndupes      = 0
        self.nqsos1      = 0
        self.nqsos2      = 0
        self.countries   = set([])
        self.longest     = None
        self.total_points = 0
        self.total_points_all = 0
        self.warnings    = 0
        self.trap_errors = True
        self.num_prev    = 0
        self.rec_prev    = []
        self.TRAP_ERRORS = False
        self.num_cwops   = 0
        self.num_running = 0
        self.num_sandp   = 0

        # History file
        self.history = os.path.expanduser( '~/Python/history/data/master.csv' )
        
        self.MY_CALL     = P.SETTINGS['MY_CALL']
        self.MY_NAME     = P.SETTINGS['MY_NAME']
        self.MY_STATE    = P.SETTINGS['MY_STATE']
        self.MY_SECTION  = P.SETTINGS['MY_SEC']
        self.MY_SEC      = self.MY_SECTION
        self.MY_PREC     = P.SETTINGS['MY_PREC']
        self.MY_CHECK    = int( P.SETTINGS['MY_CHECK'] )
        self.MY_GRID     = P.SETTINGS['MY_GRID']

        # Multi-qsos
        self.EXCHANGES = OrderedDict()

        # Init super check partial
        self.SCP=SUPER_CHECK_PARTIAL()

        
    # Function to count the no. of CWops memebrs worked in this contest
    # Also counts no. qsos made while running
    def count_cwops(self,call,HIST,rec):
        if call in HIST.keys():
            num=HIST[call]['cwops']
            if num.isdigit():
                self.num_cwops += 1
            #print('COUNT CWOPS:',call,num,self.num_cwops)

        #print(rec['running'])
        if 'running' in rec:
            if rec['running']=='1':
                self.num_running += 1
            else:
                self.num_sandp   += 1
        
        
    # Routine to group modes according to cw, digi or phone
    def group_modes(self,mode):
        if mode in ['FM','SSB','USB','LSB']:
            mode2='PH'
        elif mode=='FT8' or mode=='MFSK':
            mode2='DG'
        else:
            mode2=mode
        
        return mode2

    # Routine to convert freq in Hz to format needed for Cabrillo output
    # That is, KHz for HF or 50, 144, 432, ... for VHF/UHF
    def convert_freq(self,freq,band):
    
        if freq<30:
            freq_khz = int( 1000*freq +0.5 )
        elif band=='6m':
            freq_khz = 50
        elif band=='2m':
            freq_khz = 144
        elif band=='1.25m':
            freq_khz = 223
        elif band=='70cm':
            freq_khz = 432
        else:
            print('CONVERT_FREQ - Need more code!!',freq,band)
            sys.exit(0)
                    
        return freq_khz

    # Routine to check for dupes
    def check_dupes(self,rec,qsos,i,istart):

        # Count no. of raw qsos
        self.nqsos1+=1

        # Check for dupes
        call = rec["call"]
        band = rec["band"]
        if self.contest=='ARRL-FD':
            mode = self.group_modes( rec["mode"] )
        else:
            mode = rec["mode"]
        duplicate=False
        rapid=False
        for j in range(istart,i):
            rec2  = qsos[j]
            call2 = rec2["call"]
            band2 = rec2["band"]
            mode2 = rec2["mode"]

            #print(self.contest)
            #sys.exit(0)

            if self.contest[0:8]=='ARRL-VHF':
                if mode in ['FT8','FT4']:
                    grid  = rec["gridsquare"]
                else:
                    grid  = rec["qth"]
                if mode2 in ['FT8','FT4']:
                    grid2 = rec2["gridsquare"]
                else:
                    grid2 = rec2["qth"]
                dupe  = call==call2 and band==band2 and grid==grid2
                    
            elif self.contest=='ARRL-SS-CW':
                dupe  = call==call2
            elif self.contest=='ARRL-FD':
                mode2 = self.group_modes(mode2)
                dupe  = call==call2 and band==band2 and mode==mode2
            elif self.contest=='FT8-RU' and False:
                RST_IN  = rec["rst_rcvd"]
                if 'state' in rec :
                    qth = rec["state"]
                else:
                    qth = rec["srx"]

                dupe = rec==rec2

                if call=='J79WTA' and call2=='J79WTA':
                    print(rec)
                    print(rec2)
                    sys.exit(0)
                
            #elif self.contest=='CA-QSO-PARTY':
            elif self.contest[3:]=='QSO-PARTY':
                
                qth   = rec["qth"]
                qth2  = rec2["qth"]
                dupe  = call==call2 and band==band2 and qth==qth2
                
            else:
                dupe  = call==call2 and band==band2
                
            if dupe:
                if i-j<=2:
                    print("\n*** WARNING - RAPID Dupe",call,band,' ***')
                    if self.contest=='CA-QSO-PARTY':
                        srx   = rec["srx_string"]
                        srx2  = rec2["srx_string"]
                        print(srx)
                        print(srx2)
                        rapid = (srx==srx2)
                        print(rapid)
                    else:
                        rapid = True
                else:
                    print("\n*** WARNING - Dupe",call,band,' ***')
                print(j,rec2)
                print(i,rec)
                print(" ")
                duplicate = True
                #self.ndupes += 1

        return (duplicate,rapid)

    # Function to list all qsos with callsigns similar to a particular call
    def list_similar_calls(self,call2,qsos):
        thresh =0.7
        print('QSOs with calls similar to',call2,':')
        for i in range(0,len(qsos)):
            rec=qsos[i]
            call = rec["call"].upper()
            dx = similar(call,call2)
            if dx>=thresh and dx<1.0:
                if True:
                    if 'qth' in rec:
                        qth  = rec["qth"].upper()
                    else:
                        qth = ''
                    if 'name' in rec:
                        name = rec["name"].upper()
                    else:
                        name=''
                    band = rec["band"]
                    print('call=',call,'\t\tname=',name,'\t\tqth=',qth,'\t\tband=',band,'\t\tdist=',dx)
                else:
                    print(rec)

    # Function to list all qsos with a particular call
    def list_all_qsos(self,call2,qsos):
        print('All QSOs with ',call2,':')
        same=True
        name_old = None
        qth_old = None
        for rec in qsos:
            call = rec["call"].upper()
            if call==call2:
                if True:
                    if 'qth' in rec:
                        qth = rec["qth"].upper()
                    else:
                        qth = ''
                    if 'name' in rec:
                        name = rec["name"].upper()
                    else:
                        name = ''
                    if 'srx_string' in rec:
                        srx_string = rec["srx_string"].upper()
                    else:
                        srx_string = ''
                    band = rec["band"]
                    date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
                    time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
                    print(date_off,time_off,call,'\tname=',name,'\tqth=',qth,
                          '\tsrx=',srx_string,'\tband=',band)

                    if name_old:
                        same = same and (name==name_old) and (qth==qth_old)
                    name_old = name
                    qth_old = qth
                else:
                    print(rec)

        if not same:
            print('&*&*&*&*&*&*&*& NAME and/or QTH MISMATCH *&*&*&*&*&*&*&&*&')
            #sys.exit(0)

    #######################################################################################

    # Routine to sift through stations we had multiple contacts with to identify any discrepancies
    def check_multis(self,qsos):

        print('\nThere were multiple qsos with the following stations:')

        problem=False
        nproblems=0
        for call in self.EXCHANGES.keys():
            exchs=self.EXCHANGES[call]
            if len(exchs)>1:
                print(call,'\t',len(exchs),'\t',exchs[0])
                #print(exchs,type(exchs[0]))
                #sys.exit(0)

            if type(exchs[0]) is str:
                # Simple fixed item - make sure all the same
                mismatch = exchs.count(exchs[0]) != len(exchs)
            elif type(exchs[0]) is dict:
                # Multiple items in exchange
                mismatch=False
                for key in exchs[0].keys():
                    items=[]
                    for exch in exchs:
                        items.append(exch[key])
                    #print(key,items)
                    if key=='NR':
                        # Serial No. - make sure its increasing
                        same=sorted(items) == items
                    else:
                        # Simple fixed item - make sure all the same
                        same=items.count(items[0]) == len(items)
                    #print(same)
                    mismatch |= not same
                #sys.exit(0)
                
            if mismatch:
                if not problem:
                    nproblems+=1
                    print('There are discrepancies with multiple qsos with the following stations:')
                print('call=',call,'\texchanges=',exchs)
                problem=True
                
        if not problem:
            if nproblems>0:
                print('There are were no other discrepancies found.\n')
            else:
                print('There were no discrepancies found.\n')
        elif self.TRAP_ERRORS:
            print('\nCheck Multis - UNTRAPPED ERROR - REVIEW THIS !!!\n')
            #sys.exit(0)
    
    
        
    #######################################################################################

    # Routien to check consistency of serial out
    def check_serial_out(self,serial_out,rec,TRAP_ERRORS):
        
        if serial_out-self.num_prev!=1:
            print('\nCHECK_SERIAL_OUT: Hmmmm - Unexpected Jump in My Serial Number')
            print("Current #=",serial_out,"\tPrev #=",self.num_prev)
            if TRAP_ERRORS and False:
                print(self.rec_prev)
                print(rec)
                sys.exit(0)
        self.num_prev = serial_out
        self.rec_prev = rec
                    
    #######################################################################################

    # Scoring routine for WW Digi- PRObaBLY OBSOLETE 
    def ww_digi_OLD(self,rec,dupe,HIST):
        #print ' '
        #print rec

        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) + 0.0 )
        band = rec["band"]

        grid = rec["gridsquare"]
        field = grid[:2].upper()
        self.grid_fields[band].add(field)

        dx_station = Station(call)
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
    
        # Compute score for this entry
        dx_km = int( calculate_distance(grid,MY_GRID[:4]) +0.5 )
        qso_points = 1+int(dx_km/3000.)
        if dx_km > self.max_km:
            self.max_km=dx_km
            self.longest=rec
            
        if not dupe:
            self.total_km += dx_km
            self.nqsos2 += 1;
            self.total_points += qso_points

#                              ------info sent------- ------info rcvd-------
#QSO: freq  mo date       time call          exch     call          exch        t
#QSO: ***** ** yyyy-mm-dd nnnn ************* ******** ************* ********    n
#QSO:  3595 DG 2019-08-31 1711 HC8N          EI00     W1AW          FN32        0
#000000000111111111122222222223333333333444444444455555555556666666666777777777788
#123456789012345678901234567890123456789012345678901234567890123456789012345678901

        line='QSO: %5d DG %10s %4s %-13s %-8s %-13s %-8s     0' % \
            (freq_khz,date_off,time_off,MY_CALL,MY_GRID[:4],call,grid)

        if False:
            print(' ')
            print(rec)

            print(dx_station)
            pprint(vars(dx_station))
            
            print(call)
            print(freq_khz)
            print(band)
            print(grid)
            print(field)
            print(date_off)
            print(time_off)
            
            print(field)
            print(self.grid_fields)
            print(dx_km,qso_points,self.total_points)
            
            print(line)
            #sys,exit(0)
        
        return line

    #######################################################################################

    # Scoring routine for FT8 Round Up - OBSOLETE??
    def ft8_roundup_OLD(self,rec,dupe,HIST):
        #print ' '
        #print rec

        print('************** NOT SURE IF WE NEED THIS ANYMORE - TRY ARRL RTTY RU INSTEAD ******')
        sys.exit(0)

        keys=list(HIST.keys())

        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) + 0.0 )
        band = rec["band"]
        if 'state' in rec :
            qth = rec["state"]
        else:
            qth = rec["srx"]

        dx_station = Station(call)
        country = dx_station.country
        #print dx_station
        #pprint(vars(dx_station))
        #sys,exit(0)
            
        RST_OUT = rec["rst_sent"]
        RST_IN  = rec["rst_rcvd"]
        if RST_IN=='':
            RST_IN = '599'

        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        try:
            idx1 = RU_SECS.index(qth)
            self.sec_cnt[idx1] = 1
        except:
            print(qth,' not found in list of RU sections - ',call,country)
            self.countries.add(country)
        if not dupe:
            self.nqsos2 += 1;

#QSO: 21130 DG 2018-12-01 1912 AA2IL        579 CA        N9LJX        549 IN       

        line='QSO: %5d DG %10s %4s %-12s %3s %-9s %-12s %3s %-9s' % \
            (freq_khz,date_off,time_off,MY_CALL,RST_OUT,MY_STATE,call,RST_IN,qth)

        #print line
        #sys,exit(0)
        
        return line


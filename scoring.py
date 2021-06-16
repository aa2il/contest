############################################################################################
#
# scoring.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
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
from pyhamtools.locator import calculate_distance
#from pyhamtools import LookupLib, Callinfo

from dx.spot_processing import Station, Spot, WWV, Comment, ChallengeData
from pprint import pprint

############################################################################################

# Base contest scorer class
class CONTEST_SCORING:
    def __init__(self,contest,mode=None):
        #print('Base Class Init')
        
        self.contest = contest
        self.my_mode = mode
        
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

    # Routine to replace cut numbers with their numerical equivalents
    def reverse_cut_numbers(self,x):
        x=x.upper()
        x=x.replace('T','0')
        x=x.replace('O','0')
        x=x.replace('A','1')
        x=x.replace('N','9')

        # Strip leading 0's
        #return x
        try:
            return str(int(x))
        except:
            return x

    # Routine to group modes according to cw, digi or phone
    def group_modes(self,mode):
        if mode=='FM':
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
        elif band=='70m':
            freq_khz = 432
        else:
            print('CONVERT_FREQ - Need more code!!',freq)
        
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
        duplicate=False
        rapid=False
        for j in range(istart,i):
            rec2  = qsos[j]
            call2 = rec2["call"]
            band2 = rec2["band"]
            mode2 = rec2["mode"]
            if self.contest=='ARRL-SS-CW':
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
                
            else:
                dupe  = call==call2 and band==band2
            if dupe:
                if i-j<=2:
                    print("\n*** WARNING - RAPID Dupe",call,band,' ***')
                    rapid = True
                else:
                    print("\n*** WARNING - Dupe",call,band,' ***')
                print(j,rec2)
                print(i,rec)
                print(" ")
                duplicate = True

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
                    qth  = rec["qth"].upper()
                    name = rec["name"].upper()
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
        #for i in range(0,len(qsos)):
        #    rec=qsos[i]
        for rec in qsos:
            call = rec["call"].upper()
            if call==call2:
                if True:
                    qth  = rec["qth"].upper()
                    name = rec["name"].upper()
                    band = rec["band"]
                    print('call=',call,'\tname=',name,'\tqth=',qth,'\tband=',band)

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

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class contest_scoring:
    def __init__(self,contest):
        self.contest = contest
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

        if contest=='WW-DIGI':
            self.BANDS = ['160m','80m','40m','20m','15m','10m']
            grids = []
            for b in self.BANDS:
                grids.append((b,set([])))
            self.grid_fields = OrderedDict(grids)
            
            
    #######################################################################################

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
                    qth  = rec["qth"].upper()
                    name = rec["name"].upper()
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
        #for i in range(0,len(qsos)):
        #    rec=qsos[i]
        for rec in qsos:
            call = rec["call"].upper()
            if call==call2:
                if True:
                    qth  = rec["qth"].upper()
                    name = rec["name"].upper()
                    band = rec["band"]
                    print('call=',call,'\tname=',name,'\tqth=',qth,'\tband=',band)

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

    # Routine to check for dupes
    def check_dupes(self,rec,qsos,i,istart):

        # Count no. of raw qsos
        self.nqsos1+=1

        # Check for dupes
        call = rec["call"]
        band = rec["band"]
        if self.contest=='ARRL-FD':
            mode = self.group_modes( rec["mode"] )
        duplicate=False
        rapid=False
        for j in range(istart,i):
            rec2  = qsos[j]
            call2 = rec2["call"]
            band2 = rec2["band"]
            mode2 = rec2["mode"]
            if self.contest=='ARRL-SS-CW':
                dupe  = call==call2
            elif self.contest=='ARRL-FD':
                mode2 = self.group_modes(mode2)
                dupe  = call==call2 and band==band2 and mode==mode2
            else:
                dupe  = call==call2 and band==band2
            if dupe:
                if i-j<=2:
                    print("\n*** WARNING - RAPID Dupe",call,band,' ***')
                    rapid = True
                else:
                    print("\n*** WARNING - Dupe",call,band,' ***')
                print(j,rec2)
                print(i,rec)
                print(" ")
                duplicate = True

        return (duplicate,rapid)

    # Routine to replace cut numbers with their numerical equivalents
    def reverse_cut_numbers(self,x):
        x=x.upper()
        x=x.replace('T','0')
        x=x.replace('O','0')
        x=x.replace('A','1')
        x=x.replace('N','9')

        # Strip leading 0's
        #return x
        try:
            return str(int(x))
        except:
            return x

    #######################################################################################

    # Scoring routine for WW Digi
    def ww_digi(self,rec,dupe,HIST):
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

    #######################################################################################

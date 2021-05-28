############################################################################################
#
# rttyru.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring ARRL RTTY ROUNDUP, ARRL 10m and FT8 ROUNDUP.
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

# Need this for Makrothen and WW-DIGI - it was broke but looking up error helped to fix it
#from pyhamtools.locator import calculate_distance

############################################################################################
    
# Scoring class for ARRL RTTY RU - Inherits the base contest scoring class
class ARRL_RTTY_RU_SCORING(CONTEST_SCORING):
 
    def __init__(self,contest):
        CONTEST_SCORING.__init__(self,contest)
        print('RTTY RU Scoring Init')

        self.ft8ru    = contest=='FT8-RU'
        self.ten_m    = contest=='ARRL-10'
        if self.ten_m:
            self.secs = TEN_METER_SECS
        else:
            self.secs = RU_SECS
        self.sec_cnt  = np.zeros(len(self.secs))
        self.band_cnt = np.zeros(len(CONTEST_BANDS))
        #self.trap_errors = False                   # Make more forgiving so will run during a contest

    # Check validity of RST
    def check_rst(self,rst):
        # WSJT RST mapping:  (emperically determined from ALL.TXT - only partially determined)
        # 18 --> 599
        # 13 16 --> 589
        # 9 10 11 --> 579
        # 0 1 3 4 5 --> 569
        # -2 ... -6   ---> 559
        # -8 ... -15  ---> 549
        # -16  ---> 539
        
        if len(rst)!=3:
            return False
        elif rst[0]!='5' or  rst[2]!='9':
            return False
        else:
            return True

    # Scoring routine for ARRL RTTY Round Up
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):
        #print 'RU_SECS=',RU_SECS
        #sys.exit(0)
        #print rec

        keys=list(HIST.keys())

        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) + 0.0 )
        band = rec["band"]
        mode = rec["mode"]
        if 'state' in rec :
            qth = rec["state"]
        elif self.ft8ru:
            try:
                qth = rec["srx"]
            except:
                print('No STATE or SRX field for call',call,band,mode,' - cant determine QTH.')
                if self.trap_errors:
                    sys.exit(0)
                else:
                    return 
        elif 'qth' in rec :
            qth = rec["qth"]
        elif 'name' in rec :
            qth = rec["name"]
        elif 'srx' in rec :
            qth = rec["srx"]
        else:
            print(call,"*** CAN'T DETERMIINE QTH ***")
            sys.exit(0)
        qth=qth.upper() 

        if mode=='FT8' or mode=='FT4'  or mode=='MFSK':
            mode='DG'

        # Need to check this for RTTY RU
        #else:
        #    mode='RY'
            #print('Ugh',mode)
            #sys.exit(0)
            
        if 'country' in rec :
            country = rec["country"]
        else:
            dx_station = Station(call)
            country = dx_station.country

        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        try:
            idx1 = self.secs.index(qth)
            self.sec_cnt[idx1] = 1
            dx=False
        except:
            if country=='United States' or country=='Canada' or (self.ten_m and country=='Mexico'):
                print('\nrec=',rec)
                print('qth=',qth,' not found in list of RU sections - call=',call,country)
                sys.exit(0)
            else:
                self.countries.add(country)
                dx=True
                
        if not dupe:
            self.nqsos2 += 1;
            idx2 = CONTEST_BANDS.index(band)
            self.band_cnt[idx2] += 1

        #sys.exit(0)

        # Check RST
        RST_OUT = rec["rst_sent"]
        if not self.check_rst(RST_OUT):
            print('Invalid RST_OUT field for call',call,band,mode,RST_OUT)
            if self.trap_errors:
                sys.exit(0)
        
        RST_IN  = rec["rst_rcvd"]
        if not self.check_rst(RST_IN):
            print('Invalid RST_IN field for call',call,band,mode,RST_IN)
            if not self.ft8ru and not self.ten_m and dx:
                RST_IN='599'
            elif self.trap_errors:
                sys.exit(0)
                
        if False:
            if RST_IN=='':
                RST_IN = '599'
                print(call,'\t*** WARNING - Bad RST IN')
                #sys.exit(0)
            if dx and RST_IN==qth:
                RST_IN='599'
            if RST_IN!='599' and False:
                print('*** WARNING ***',call,'\tBad RST IN:',RST_IN)
                #sys.exit(0)

        
#                              --------info sent------- -------info rcvd--------
#QSO: freq  mo date       time call          rst exch   call          rst exch  
#QSO: ***** ** yyyy-mm-dd nnnn ************* nnn ****** ************* nnn ******
#QSO: 28079 RY 2003-01-04 1827 VE3IAY        599 ON     W5KFT         599 TX   
#QSO: 28079 RY 2003-01-04 1828 VE3IAY        599 ON     KP2D          599 035   

        #line='QSO: %5d %2s %10s %4s %-13s %3s %-6s %-13s %3s %-6s' % \
        #    (freq_khz,mode,date_off,time_off,MY_CALL,'599',MY_STATE,call,RST_IN,qth)
        line='QSO: %5d %2s %10s %4s %-12s %3s %-9s %-12s %3s %-9s' % \
            (freq_khz,mode,date_off,time_off,MY_CALL,RST_OUT,MY_STATE,call,RST_IN,qth)

        # Check against history
        if call in keys:
            state = HIST[call]['state']
            if state=='':
                state = HIST[call]['sec']
            #print call,qth,state
            if qth!=state and not dx:
                print('\n$$$$$$$$$$ Difference from history $$$$$$$$$$$')
                print(rec)
                print(line)
                print('CALL:',call,'\t Rx:',qth,'\t Hist:',state)
                print(HIST[call])
                #sys,exit(0)
                
        elif False:
            print('\n*** Warning - no history for call:',call)
            self.list_all_qsos(call,qsos)
            self.list_similar_calls(call,qsos)
                        
        #print line
        #sys,exit(0)
        
        return line

    # Summary & final tally
    def summary(self):

        missing=[]
        nstates=0
        for i in range(len(self.secs)):
            if self.sec_cnt[i]==0:
                missing.append(self.secs[i])
            else:
                nstates+=1
        print('\nNo. States:',nstates)
        print('Missing: ',missing)

        dxcc = list( self.countries )
        dxcc.sort()
        print('\nCountries:',len(dxcc))
        for i in range(len(dxcc)):
            print('   ',dxcc[i])
            
        mults = len(dxcc) + int( np.sum(self.sec_cnt) )
        print('\nBy Band:',self.band_cnt,sum(self.band_cnt))
    
        print('\nNo. QSOs        =\t',self.nqsos1)
        print('No. Unique QSOs =\t',self.nqsos2)
        print('Multipliers     =\t',mults)
        print('Claimed Score   =\t',self.nqsos2*mults)

    #######################################################################################

        

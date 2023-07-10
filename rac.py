############################################################################################
#
# rac.py - Rev 1.0
# Copyright (C) 2022 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring RAC winter contest
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
from rig_io.ft_tables import PROVINCES
from scoring import CONTEST_SCORING
from dx.spot_processing import Station
from pprint import pprint
from utilities import reverse_cut_numbers
import numpy as np

############################################################################################
    
# Scoring class for CWops mini tests - Inherits the base contest scoring class
class RAC_SCORING(CONTEST_SCORING):
 
    def __init__(self,P):
        super().__init__(P,'CANADA-WINTER',mode='CW')

        # NOTE - RAC also has CANADA-DAY contest in the summer, same deal
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.band_cnt = np.zeros(len(self.BANDS),dtype=np.int)
        self.sec_cnt  = np.zeros((len(self.BANDS),len(PROVINCES)),dtype=np.int)

        # Determine contest time -Contest occurs on 3rd? full weekend of Dec
        now = datetime.datetime.utcnow()
        year=now.year
        day1=datetime.date(year,12,1).weekday()                            # Day of week of 1st of month 0=Monday, 6=Sunday
        sat2=1 + ((5-day1) % 7) + 2*7                                      # Day no. for 3rd Saturday = 1 since day1 is the 1st of the month
                                                                           # No. days until 3rd Saturday (day 5) + 14 more days 
        self.date0=datetime.datetime(year,12,sat2,0)                   # Contest starts at 0000 UTC on Saturday (Friday night local) ...
        self.date1 = self.date0 + datetime.timedelta(hours=48)         # ... and ends at 1200 UTC on Sunday
        print('day1=',day1,'\tsat2=',sat2,'\tdate0=',self.date0)

        # Playing with dates
        if False:
            print(now)
            print(now.day,now.weekday())
            print(today)
            print(self.date0)
            print(self.date1)
            #sys.exit(0)

        # Name of output file
        self.output_file = self.MY_CALL+'_'+self.contest+'_'+str(self.date0.year)+'.LOG'
            
    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_STATE)
                    
    # Scoring routine for RAC Winter contest
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):
        #print('\nrec=',rec)
        keys=list(HIST.keys())

        # Pull out relavent entries
        call = rec["call"].upper()
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        rx   = rec["srx_string"].strip().upper().split(',')
        tx   = rec["stx_string"].strip().upper().split(',')

        band = rec["band"]
        idx1 = self.BANDS.index(band)
        self.band_cnt[idx1] += 1
        
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        if MY_MODE=='CW':
            mode='CW'
        else:
            print('Invalid mode',MY_MODE)
            sys.exit(1)

        # Check country - Canadian stations are worth many more pts
        dx_station = Station(call)
        if False:
            pprint(vars(dx_station))
            sys.exit(0)
        country    = dx_station.country
        
        # There was a lot of inconsistencies where I stored the exchange bx I was developing
        # the keyer code for this contest on the fly
        rst_in='599'
        if rx[0]=='5NN':
            if country=='Canada':
                qth = rx[1].upper()
            else:
                qth = reverse_cut_numbers( rx[1] )
        else:                
            if country=='Canada':
                if 'qth' in rec:
                    qth = rec["qth"].upper()
                else:
                    qth = rx[0]
            else:
                qth = reverse_cut_numbers( rx[0] )

        rst_out='599'
        if tx[0]=='5NN':
            serial_out = reverse_cut_numbers( tx[1] )
        else:                
            serial_out = reverse_cut_numbers( tx[0] )

        # Error checking
        if country=='Canada':
            qth2=oh_canada3(dx_station)
            if qth2!=qth:
                print('\nrec=',rec)
                print('Oh Canada: qth=',qth,'\tqth2=',qth2)
                sys.exit(0)
        
        # Determine point value for this QSO
        if country=='Canada':
            if 'RAC' in call:
                qso_points = 20
            else:
                qso_points = 10

            try:
                idx2 = PROVINCES.index(qth)
            except:
                print('\n',rec)
                print(qth,'not in list of of PROVINCES - call=',call)
                sys.exit(0)
            self.sec_cnt[idx1,idx2] = 1
                
        else:
            qso_points = 2

        self.total_points_all += qso_points
        if not dupe:
            self.nqsos2 += 1;
            self.total_points += qso_points
        else:
            print('??????????????? Dupe?',call)
        #print call,self.nqsos2

#         --------info sent------- -------info rcvd------
# freq mo date time call rst exch call rst exch
#00000000011111111112222222222333333333344444444445555555555666666666677777777778
#12345678901234567890123456789012345678901234567890123456789012345678901234567890
#QSO: 1825 CW 2003-07-01 1044 VE3KZ 599 ON VE4EAR 599 MB

        line='QSO: %5d %2s %10s %4s %-10s      %3s %-5s %-10s      %3s %-5s' % \
            (freq_khz,mode,date_off,time_off,
             self.MY_CALL,rst_out,serial_out,
             call,rst_in,qth)
        
        return line
                        
    # Summary & final tally
    def summary(self):

        print(self.sec_cnt)
        print('\nNo. QSOs         =',self.nqsos2,\
              '\t(',self.nqsos1,')')

        print('Band\tQSOs\tMults\tProvinces')
        total_mults=0
        for i in range(len(self.BANDS)):
            secs=self.sec_cnt[i]
            #print(secs)
            mults = np.sum(secs)
            total_mults+=mults
            print(self.BANDS[i],'\t',self.band_cnt[i],'\t',mults,'\t',end='')
            for j in range(len(PROVINCES)):
                if secs[j]>0:
                    print(' ',PROVINCES[j],end='')
            print(' ')
        print('Total:\t',sum(self.band_cnt),'\t',total_mults)
            
        print('\tQSO Points       =',self.total_points,\
              '\t(',self.total_points_all,')')
        print('Mults            =',total_mults)
        print('Claimed score    =',self.total_points*total_mults,\
              '\t(',self.total_points_all*mults,')')
    
        


# Routine to give QTH of a Canadian station
def oh_canada3_old(dx_station):

    """
    Prefixes	Province/Territory
    --------    ------------------
    VE1 VA1	Nova Scotia
    VE2 VA2	Quebec	
    VE3 VA3	Ontario	
    VE4 VA4	Manitoba	
    VE5 VA5	Saskatchewan	
    VE6 VA6	Alberta	
    VE7 VA7	British Columbia	
    VE8	        Northwest Territories	
    VE9	        New Brunswick	
    VE0*	International Waters
    VO1	        Newfoundland
    VO2	        Labrador
    VY1	        Yukon	
    VY2	        Prince Edward Island
    VY9**	Government of Canada
    VY0	        Nunavut	
    CY0***	Sable Is.[16]	
    CY9***	St-Paul Is.[16]	

    For the CQP:
    MR      Maritime provinces plus Newfoundland and Labrador (NB, NL, NS, PE)
    QC      Quebec
    ON      Ontario
    MB      Manitoba
    SK      Saskatchewan
    AB      Alberta
    BC      British Columbia
    NT 
    """

    qth=''
    #print('Oh Canada ... 1')
    #pprint(vars(dx_station))
    if dx_station.country=='Canada':
        prefix=dx_station.call_prefix +dx_station.call_number
        if prefix in ['VE1','VA1']:
            qth='NS'
        elif prefix in ['VE2','VA2']:
            qth='QC'
        elif prefix in ['VE3','VA3']:
            qth='ON'
        elif prefix in ['VE4','VA4']:
            qth='MB'
        elif prefix in ['VE5','VA5']:
            qth='SK'
        elif prefix in ['VE6','VA6']:
            qth='AB'
        elif prefix in ['VE7','VA7']:
            qth='BC'
        elif prefix in ['VE8']:
            qth='NT'
        elif prefix in ['VE9']:
            qth='NB'
        elif prefix in ['VO1','VO2']:
            qth='NL'
        elif prefix in ['VY0']:
            qth='NU'
        elif prefix in ['VY1']:
            qth='YT'
        elif prefix in ['VY2']:
            qth='PE'
        else:
            print('OH CANADA3 - Hmmmm',prefix)
            pprint(vars(dx_station))
            sys.exit(0)
            
    else:
        print('I dont know what I am doing here')
        
    return qth

################################################################################
    
        

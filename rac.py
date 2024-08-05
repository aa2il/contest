############################################################################################
#
# rac.py - Rev 1.0
# Copyright (C) 2022-4 by Joseph B. Attili, aa2il AT arrl DOT net
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
from rig_io.ft_tables import PROVINCES2,THIRTEEN_COLONIES
from scoring import CONTEST_SCORING
from dx.spot_processing import Station
from pprint import pprint
from utilities import reverse_cut_numbers,Oh_Canada
import numpy as np

############################################################################################

VERBOSITY=0
TRAP_ERRORS = False
TRAP_ERRORS = True
    
############################################################################################
    
# Scoring class for RAC & OC DX - Inherits the base contest scoring class
class RAC_SCORING(CONTEST_SCORING):
 
    def __init__(self,P):
        # Determine contest 
        now = datetime.datetime.utcnow()
        month=now.month
        year=now.year
        if P.TXT=='RAC':
            if month==12:
                P.TXT='CANADA-WINTER'              # Dont change - this is what RAC wants!
            else:
                P.TXT='CANADA-DAY'              # Dont change - this is what RAC wants!

        super().__init__(P,P.TXT,mode='CW')

        # NOTE - RAC also has CANADA-DAY contest in the summer, same deal
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.band_cnt = np.zeros(len(self.BANDS),dtype=np.int32)
        self.sec_cnt  = np.zeros((len(self.BANDS),len(PROVINCES2)),dtype=np.int32)
        self.contest_name = P.TXT
        self.RAC  = False
        self.OCDX = False
        self.PREFIXES = []
        self.nq          = 0
        self.ncdn        = 0
        self.nrac        = 0
        self.ndx         = 0

        if self.contest_name=='CANADA-DAY':
            
            # RAC Canada Day Contest occurs on July 1
            self.date0=datetime.datetime(year,7,1,0)                          # Contest starts at 0000 UTC on July 1
            self.date1 = self.date0 + datetime.timedelta(hours=24)             # ... and ends at 2359
            self.RAC  = True
            
        elif self.contest_name=='CANADA-WINTER':
            
            # RAC Winter Contest occurs in Dec - not sure of which weekend - 3rd or 4th full weekend?
            # Or perhaps its last full weekend in Dec? Let's go with that ...
            day1=datetime.date(year,12,1).weekday()                            # Day of week of 1st of month 0=Monday, 6=Sunday
            sat2=1 + ((5-day1) % 7) + 4*7                                      # Day no. for 5th Saturday = 1 since day1 is the 1st of the month
                                                                               # No. days until 5th Saturday (day 5) + 14 more days
            if sat2+1>31:
                print('\nRAC SCORING - need to make some adjustments!')
                print('sat2=',sat2)
                sat2-=7                                                        # Note a full weekend - role back to 4th Saturday
                print('sat2=',sat2)
            if sat2 in [24,25]:
                sat2-=7                                                        # I don't think they'd hold on Christmas?!
                #sys.exit(0)
                
            self.date0=datetime.datetime(year,12,sat2,0)                       # Contest starts at 0000 UTC on Saturday (Friday night local) ...
            self.date1 = self.date0 + datetime.timedelta(hours=48)             # ... and ends at 1200 UTC on Sunday
            self.RAC  = True
            
        elif self.contest_name=='OCDX':
            
            # OC DX Contest occurs on 2n? full weekend of Oct
            day1=datetime.date(year,10,1).weekday()                            # Day of week of 1st of month 0=Monday, 6=Sunday
            sat2=1 + ((5-day1) % 7) + 1*7                                      # Day no. for 3rd Saturday = 1 since day1 is the 1st of the month
                                                                               # No. days until 3rd Saturday (day 5) + 14 more days 
            self.date0=datetime.datetime(year,10,sat2,6)                       # Contest starts at 0600 UTC on Saturday (Friday night local) ...
            self.date1 = self.date0 + datetime.timedelta(hours=24)             # ... and ends at 0600 UTC on Sunday
            self.OCDX = True
        else:
            print('RAC SCORING - Unknown contest')
            sys.exit(0)

        # Playing with dates
        if True:
            print('\nContest Name=',self.contest_name)
            print('nnow=',now,'\tday=',now.day,now.weekday())
            print('date0=',self.date0)
            print('date1=',self.date1)
            #print('day1=',day1,'\tsat2=',sat2,'\tdate0=',self.date0)
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

        # Check for correct contest
        if "contest_id" in rec:
            id   = rec["contest_id"].upper()
        else:
            print('\nWarning - missing contest id')
            print(rec)
            print(self.contest_name)
            id=''
            #sys.exit(0)
        if self.contest_name=='OCDX' and id!='OCDX-QSO-PARTY':
            if VERBOSITY>0:
                print('contest=',self.contest,id)
                print('QSO not part of OC DX contest')
            return
        elif self.contest_name[0:7]=='CANADA' and id!='RAC-QSO-PARTY':
            if VERBOSITY>=0:
                print('contest=',self.contest,id)
                print('QSO not part of RAC contest')
            return

        # Pull out relavent entries
        call = rec["call"].upper()
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        rx   = rec["srx_string"].strip().upper().split(',')
        tx   = rec["stx_string"].strip().upper().split(',')

        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        if MY_MODE=='CW':
            mode='CW'
        else:
            print('Invalid mode',MY_MODE)
            sys.exit(1)

        # Begin error checking process
        if '?' in "".join(rx)+call:
            print('\n$$$$$$$$$$$$$ Questionable RX Entry $$$$$$$$$$$$$$')
            self.nq+=1
            print('Call   =',call)
            print('rx string =',rx)
            print('Date   =',rec["qso_date_off"])
            print('Time   =',rec["time_off"])
            print('rec=',rec)
            self.list_all_qsos(call,qsos)
            if TRAP_ERRORS:
                sys.exit(0)

        elif self.contest_name=='CANADA-DAY' and call in THIRTEEN_COLONIES and True:
            print('call=',call)
            print('QSO not part of RAC contest - skipped')
            return
                
        # Check country - Canadian stations are worth many more pts in RAC contests
        dx_station = Station(call)
        if False:
            pprint(vars(dx_station))
            sys.exit(0)
        country    = dx_station.country
        continent  = dx_station.continent
        prefix     = dx_station.prefix
        
        # There was a lot of inconsistencies where I stored the exchange bx I was developing
        # the keyer code for this contest on the fly - should all be conistent now
        rst_in='599'
        if rx[0]=='5NN' or True:
            if self.RAC and country=='Canada':
                qth = rx[1].upper()
            else:
                qth = reverse_cut_numbers( rx[1] )
                if not qth.isdigit():
                    print('\n*** ERROR *** NUM IN =',qth)
                    print('rec=',rec,'\n')
                    if TRAP_ERRORS:
                        print('call     =',call)
                        print('date     =',date_off)
                        print('time     =',time_off)
                        sys.exit(0)

        else:                
            if self.RAC and country=='Canada':
                if 'qth' in rec:
                    qth = rec["qth"].upper()
                else:
                    qth = rx[0]
            else:
                qth = reverse_cut_numbers( rx[0] )

        if self.OCDX and continent=='OC':
            self.PREFIXES.append(prefix)

        rst_out='599'
        if tx[0]=='5NN':
            serial_out = reverse_cut_numbers( tx[1] )
        else:                
            serial_out = reverse_cut_numbers( tx[0] )

        # Error checking
        if self.RAC and country=='Canada':
            qth2,junk=Oh_Canada(dx_station)
            if qth2!=qth:
                print("\n$$$$$$$$$$$$$ Province doesn't match callsign $$$$$$$$$$$$$$")
                print('\nrec=',rec)
                print('Oh Canada: qth=',qth,'\tqth2=',qth2)
                if TRAP_ERRORS and False:
                    sys.exit(0)

        # Keep track of band counts
        band = rec["band"]
        idx1 = self.BANDS.index(band)
        self.band_cnt[idx1] += 1
        
        # Determine point value for this QSO
        if self.RAC and country=='Canada':
            if 'RAC' in call:
                qso_points = 20
                self.nrac+=1
            else:
                qso_points = 10
                self.ncdn+=1

            try:
                idx2 = PROVINCES2.index(qth)
            except:
                print('\n',rec)
                print(qth,'not in list of of PROVINCES - call=',call)
                sys.exit(0)
            self.sec_cnt[idx1,idx2] = 1
                
        else:
            self.ndx+=1
            if self.RAC:
                qso_points = 2
            else:
                qso_points = 1

        self.total_points_all += qso_points
        if not dupe:
            self.nqsos2 += 1;
            self.total_points += qso_points
        else:
            print('??????????????? Dupe?',call)
        #print call,self.nqsos2

        # Info for multi-qsos
        if self.RAC and country=='Canada':
            exch_in=rst_in+' '+qth
            if call in self.EXCHANGES.keys():
                self.EXCHANGES[call].append(exch_in)
            else:
                self.EXCHANGES[call]=[exch_in]
                        
        # Count no. of CWops guys worked
        self.count_cwops(call,HIST,rec)
                
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

        print('\nBand\tQSOs\tMults\tProvinces')
        total_mults=0
        for i in range(len(self.BANDS)):
            secs=self.sec_cnt[i]
            #print(secs)
            mults = np.sum(secs)
            total_mults+=mults
            print(self.BANDS[i],'\t',self.band_cnt[i],'\t',mults,'\t',end='')
            for j in range(len(PROVINCES2)):
                if secs[j]>0:
                    print(' ',PROVINCES2[j],end='')
            print(' ')
        print('Total:\t',sum(self.band_cnt),'\t',total_mults)
            
        print('\nQSO Points       =',self.total_points,\
              '\t(',self.total_points_all,')')
        print('Mults            =',total_mults)
        print('Claimed score    =',self.total_points*total_mults,\
              '\t(',self.total_points_all*total_mults,')')

        print('Cdn:',self.ncdn,'\tRAC:',self.nrac,'\tDX:',self.ndx,'\tMults:',total_mults,'\tScore:',self.total_points*total_mults)
        
        if self.OCDX:
            print('\n************** Scoring routine for OCDX not complete !!!! ******************\n')
    
        print('\nNo. CWops Members =',self.num_cwops,' =',
              int( (100.*self.num_cwops)/self.nqsos1+0.5),'%')
        print('No. QSOs Running  =',self.num_running,' =',
              int( (100.*self.num_running)/self.nqsos1+0.5),'%')
        print('No. QSOs S&P      =',self.num_sandp,' =',
              int( (100.*self.num_sandp)/self.nqsos1+0.5),'%')

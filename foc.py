############################################################################################
#
# foc.py - Rev 1.0
# Copyright (C) 2022-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Routines for scoring FOC BW.
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
    
# Scoring class for FOC BW test - Inherits the base contest scoring class
class FOCBW_SCORING(CONTEST_SCORING):

    def __init__(self,P,session=None):
        super().__init__(P,'FOC-BW',mode='CW')
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.sec_cnt = np.zeros(len(self.BANDS),dtype=int)
        self.calls=set([])
        self.nfoc=0
        self.calls1=set([])
        self.calls2=set([])

        self.MY_CALL    = P.SETTINGS['MY_CALL']
        self.MY_NAME    = P.SETTINGS['MY_NAME']
        self.MY_STATE   = P.SETTINGS['MY_STATE']
        self.MY_SECTION = P.SETTINGS['MY_SEC']
        
        # Determine contest time - contest is held twice per year
        now = datetime.datetime.utcnow()
        if now.month in [3,9]:
            day1=datetime.date(now.year,now.month,1).weekday()            # Day of week of 1st of month 0=Monday, 6=Sunday
            if now.month==3:
                sat2=1 + ((5-day1) % 7) + 3*7                         # Day no. for 4th Saturday = 1 since day1 is the 1st of the month
            else:
                sat2=1 + ((5-day1) % 7) + 1*7                         # Day no. for 2nd Saturday = 1 since day1 is the 1st of the month
        else:
            print('Whoops!',now.month)
            sys.exit(0)

        self.date0=datetime.datetime(now.year,now.month,sat2,0)                # Contest starts at 0000 UTC on Saturday (Friday night local) ...
        self.date1 = self.date0 + datetime.timedelta(hours=24)     # ... and ends at 0000 UTC on Sunday
        
        if False:
            print('now=',now,now.year,now.month)
            print('date0=',self.date0)
            print('date1=',self.date1)
            sys.exit(0)

        # Name of output file
        self.output_file = self.MY_CALL+'_'+self.contest+'_'+str(self.date0.year)+'.LOG'
            
    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_STATE)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SECTION)
                    

    # Scoring routine for FOC BW
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2=None):
        #print('rec=',rec)
        keys=list(HIST.keys())

        # Pull out relavent entries
        call = rec["call"].upper()
        rx   = rec["srx_string"].upper()
        num  = rx.split(',')[1]
        if len(num)>2:
            num = reverse_cut_numbers(num)
        name = rec["name"].upper()
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        band = rec["band"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        if MY_MODE=='CW':
            mode='CW'
        else:
            print('Invalid mode',MY_MODE)
            sys.exit(1)

        self.calls.add(call)
        if num.isdigit() and int(num)>0:
            self.nfoc+=1
            self.calls1.add(call)
        else:
            self.calls2.add(call)

        if False:
            print('call  =',call)
            print('name  =',name)
            print('num   =',num)
            print('calls =',self.calls)
            sys.exit(0)

        if not dupe:
            idx2 = self.BANDS.index(band)
            self.sec_cnt[idx2] += 1
            self.nqsos2 += 1;
        else:
            print('??????????????? Dupe?',call)
        #print call,self.nqsos2

        # Sometimes, I'll put a "?" to indicate that I need to review
        if '?' in call+name+num:
            print('\n??? Check this one again: ???')
            print('call=',call,'\t\tname=',name,'\t\tnum=',num,'\ttime=',time_off)
            if TRAP_ERRORS:
                sys.exit(0)

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
            foc=HIST[call2]['foc']
            if len(foc)==0:
                foc=HIST[call2]['foc']
            name9=HIST[call2]['name']
            if num!=foc or name!=name9:
                print('\n$$$$$$$$$$ Difference from history $$$$$$$$$$$')
                print(call,':  Current:',name,num,' - History:',name9,foc)
                self.list_all_qsos(call,qsos)
                print(' ')

        else:
            
            print('\n++++++++++++ Warning - no history for call:',call)
            self.list_all_qsos(call,qsos)
            self.list_similar_calls(call,qsos)

        # Info for multi-qsos
        exch_in=name+' '+num
        if call in self.EXCHANGES.keys():
            self.EXCHANGES[call].append(exch_in)
        else:
            self.EXCHANGES[call]=[exch_in]
                        
        # Count no. of CWops guys worked
        self.count_cwops(call,HIST,rec)
                
#000000000111111111122222222223333333333444444444455555555556666666666777777777788
#123456789012345678901234567890123456789012345678901234567890123456789012345678901
#                              -----info sent------ -----info rcvd------

        line='QSO: %5d %2s %10s %4s %-10s      %-10s %-3s %-10s      %-10s %-3s' %    \
            (freq_khz,mode,date_off,time_off,self.MY_CALL,self.MY_NAME,self.MY_STATE, \
             call,name,num)
        
        return line
                        
    # Summary & final tally
    def summary(self):
        
        print('\nUnique calls =',self.calls,len(self.calls))
        print('\nFOC Member Calls =',self.calls1,len(self.calls1))
        print('\nNon-Member Calls =',self.calls2,len(self.calls2))
        print('\nnqsos1=',self.nqsos1)
        print('nqsos2=',self.nqsos2)
        print('\nBand\tQSOs')
        for i in range(len(self.BANDS)):
            print(self.BANDS[i],'\t',self.sec_cnt[i])
        print('\nTotals:\t',self.nqsos2)

        print('No. FOC Members worked =',self.nfoc)
        print('No. Non-Members worked =',self.nqsos1-self.nfoc)

        print('\n# CWops Members =',self.num_cwops,' =',
              int( (100.*self.num_cwops)/self.nqsos1+0.5),'%')
        print('# QSOs Running  =',self.num_running,' =',
              int( (100.*self.num_running)/self.nqsos1+0.5),'%')
        print('# QSOs S&P      =',self.num_sandp,' =',
              int( (100.*self.num_sandp)/self.nqsos1+0.5),'%')
        

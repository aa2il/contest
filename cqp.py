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
from fileio import parse_adif

############################################################################################

CQP_MULTS  = STATES + ['MR', 'QC', 'ON', 'MB', 'SK', 'AB', 'BC', 'NT']
#CQP_STATES = STATES + PROVINCES + CA_COUNTIES + ['MR','DX']
CQP_STATES = STATES + PROVINCES + CA_COUNTIES + ['MR']
COUNTRIES=['United States','Canada','Alaska','Hawaii'] 

# Scoring class for CQP - Inherits the base contest scoring class
class CQP_SCORING(CONTEST_SCORING):
 
    def __init__(self,P):
        CONTEST_SCORING.__init__(self,'CA-QSO-PARTY',mode='CW')
        print('CQP Scoring Init')
        
        self.BANDS       = ['160m','80m','40m','20m','15m','10m']
        self.sec_cnt     = np.zeros(len(CQP_MULTS))
        self.dx_cnt      = 0
        self.calls       = []
        self.county_cnt  = np.zeros(len(CA_COUNTIES))
        self.band_cnt    = np.zeros(len(self.BANDS))
        self.num_prev    = 0
        self.rec_prev    = []

        self.MY_CALL     = P.SETTINGS['MY_CALL']
        self.MY_NAME     = P.SETTINGS['MY_NAME']
        self.MY_SECTION  = P.SETTINGS['MY_SEC']
        self.MY_COUNTY   = P.SETTINGS['MY_COUNTY']

        # History file
        self.history = os.path.expanduser( '~/Python/history/data/master.csv' )
                
        # Determine contest date/time - first Sat in Oct.
        now = datetime.datetime.utcnow()
        day1=datetime.date(now.year,10,1).weekday()                     # Day of week of 1st of month 0=Monday, 6=Sunday
        sat2=1 + ((5-day1) % 7)                                         # Day no. for 1st Saturday = 1 since day1 is the 1st of the month
                                                                        #    plus no. days until 1st Saturday (day 5)
        start_time=16                                                   # 1600 UTC                           
        self.date0=datetime.datetime(now.year,10,sat2,start_time)       # Need to add more code for other sessions next year
        self.date1 = self.date0 + datetime.timedelta(hours=30)          # Contest is 30-hrs long
        print('day1=',day1,'\tsat2=',sat2,'\tdate0=',self.date0)
        #sys.exit(0)

        # Manual override
        if False:
            self.date0 = datetime.datetime.strptime( "20201003 1600" , "%Y%m%d %H%M")  # Start of contest
            self.date1 = self.date0 + datetime.timedelta(hours=30)

            
    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_COUNTY)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SECTION)

    # Scoring routine for CQP
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):
        #print('rec=',rec)
        keys=list(HIST.keys())
        keys2=list(HIST2.keys())
        #sys.exit(0)

        # Pull out relavent entries
        call = rec["call"].upper()
        rx   = rec["srx_string"].strip().upper()
        a    = rx.split(',') 
        try:
            num_in = int( self.reverse_cut_numbers( a[0] ) )
        except:
            print('rec=',rec)
            print('Problem with serial:',a)
            #sys.exit(0)

        qth_in = a[1]
        my_call = rec["station_callsign"].strip().upper()

        tx   = rec["stx_string"].strip().upper()
        b    = tx.split(',')
        num_out = int( self.reverse_cut_numbers( b[0] ) )
        qth_out = b[1]

        if num_out-self.num_prev!=1:
            print('\nHmmmm - we seem to have failure to communicate here!')
            print(num_out,self.num_prev)
            #print(self.rec_prev)
            #print(rec)
            #sys.exit(0)
        self.num_prev = num_out
        self.rec_prev = rec

        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        band = rec["band"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        if MY_MODE=='CW':
            mode='CW'
        else:
            print('Invalid mode',MY_MODE)
            sys.exit(1)

        dx_station = Station(call)
        country    = dx_station.country
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
            idx1 = CA_COUNTIES.index(qth_in)
            self.county_cnt[idx1] += 1
        elif qth_in in ['NB', 'NL', 'NS', 'PE']:
            qth_in='MR'
            qth='MR'
        else:
            qth=qth_in

        idx1 = self.BANDS.index(band)
        self.band_cnt[idx1] += 1
            
        if not dupe:
            try:
                if qth!='DX':
                    idx1 = CQP_MULTS.index(qth)
                    self.sec_cnt[idx1] += 1
                else:
                    self.dx_cnt += 1
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
        if( not country in COUNTRIES and qth_in!='DX') or \
          (country in COUNTRIES and qth_in not in CQP_STATES):
            pprint(vars(dx_station))
            print('rec=',rec)
            print('call=',call)
            print('Received qth '+qth_in+' not recognized - srx=',rx)
            print('History=',HIST[call])
            print('Country=',country)
            print('QTH in=',qth_in)
            sys.exit(0)

        # Compare to history
        if call in keys2:
            if qth_in!=HIST2[call]:
                print('\n$$$$$$$$$$ Difference from history2 $$$$$$$$$$$')
                print(call,':  Current:',qth_in,' - History:',HIST2[call])
                print(' ')
                if not call in ['W6COW','W6TCP','W6TED','KL7SB']:
                    sys.exit(0)
            
        elif call in keys:
            if qth=='CA':
                state=HIST[call]['county']
            else:
                state=HIST[call]['state']
            #print call,qth,state
            if qth_in!=state:
                print('\n$$$$$$$$$$ Difference from history $$$$$$$$$$$')
                print(call,':  Current:',qth_in,' - History:',state)
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
             my_call,str(num_out),qth_out,
             call,str(num_in),qth_in)
        
        return line
                        
    # Summary & final tally
    def summary(self):

        print('\nStates & Provinces:')
        mults=0
        for i in range(len(self.sec_cnt)):
            if self.sec_cnt[i]>0:
                mults += 1
                tag=''
            else:
                tag='*****'
            print(i,'\t',CQP_MULTS[i],'\t',int(self.sec_cnt[i]),'\t',tag)

        print('\nCA Counties:')
        for i in range(len(self.county_cnt)):
            if self.county_cnt[i]>0:
                tag=''
            else:
                tag='*****'
            print(i,'\t',CA_COUNTIES[i],'\t',int(self.county_cnt[i]),'\t',tag)

        print('\nRaw QSOs by Band:')
        for i in range(len(self.band_cnt)):
            print(i,'\t',self.BANDS[i],'\t',int(self.band_cnt[i]) )

        uniques = np.unique( self.calls )
        uniques.sort()
        print('\nThere were',len(uniques),'unique calls:\n',uniques)

        print('\nNo. raw QSOS (nqsos1)    =\t',self.nqsos1)
        print(  'No. unique QSOS (nqsos2) =\t',self.nqsos2)
        print('Multipiers    =\t',mults)
        print('Claimed Score =\t',3*mults*self.nqsos2)

        # They did this in 2020
        if False:
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
            


    # Routine to sift through station we had multiple contacts with to identify any discrepancies
    def check_multis(self,qsos):

        print('There were multiple qsos with the following stations:')
        qsos2=qsos.copy()
        qsos2.sort(key=lambda x: x['call'])
        calls=[]
        for rec in qsos2:
            calls.append(rec['call'])
        #print(calls)
        uniques = list(set(calls))
        uniques.sort()
        #print(uniques)

        for call in uniques:
            #print(call,calls.count(call))
            if calls.count(call)>1:
                num_last=0
                qth_last=''
                for rec in qsos:
                    if rec['call']==call:
                        mode = rec["mode"]
                        band = rec["band"]
                        qth  = rec["qth"].upper()
                        rx   = rec["srx_string"].strip().upper()
                        a    = rx.split(',') 
                        num_in = int( self.reverse_cut_numbers( a[0] ) )
                        print(call,'\t',band,'\t',mode,'\t',num_in,'\t',qth)
                        if num_last>=num_in or (len(qth_last)>0 and qth_last!=qth):
                            print('$$$$$$$$$$$$ POTENTIAL ERROR $$$$$$$$$$$$$$')
                            print('Serials not increasing &/or different QTH')
                        num_last=num_in
                        qth_last=qth
                print(' ')
                        
        #sys.exit(0)

        
    def read_hist2(self,fname):

        print('READ_HIST2 - fname=',fname)
        #HIST2=[]
        HIST2 = OrderedDict()
        if len(fname)>0:
            print('Well, we have a histroy file ...',fname)
            qsos = parse_adif(fname)
            print(len(qsos))
            print(qsos[0])

            for qso in qsos:
                #print(qso)
                call=qso['call']
                dxcc=int( qso['dxcc'] )
                if dxcc in [1,110,291]:        # Canada, HI, USA, need AK also
                    state=qso['state']
                    if state=='CA':
                        try:
                            county=qso['cnty'].split(',')
                            a=county[1]
                            b=a.split(' ')
                            if len(b)==1:
                                qth=a[0:4]
                            elif b[0]=='EL':
                                qth=b[0]+b[1][0:2]
                            else:
                                if b[0][0:3] in ['LOS','SAN']:
                                    qth=b[0][0]+b[1][0:3]
                                else:
                                    qth=a
                                
                        except:
                            #qth='*******************'
                            qth=''
                    else:
                        qth=state
                        if qth in ['NB','NL','NS','PE']:
                            qth='MR'
                else:
                    qth='DX'

                #rec={'call':call,'qth':qth}
                #print(rec)
                #HIST2.append( rec )
                if call in HIST2.keys():
                    qth2=HIST2[call]
                    if qth!=qth2:
                        print('Houston, there is a turd in the punch bowl')
                        print(qth,qth2)
                else:
                    HIST2[call]=qth
                        
            print('HIST2:',len(HIST2))
            for call in HIST2.keys():
                print(call,'\t',HIST2[call])
            #sys.exit(0)

        return HIST2
    

        

        

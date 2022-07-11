############################################################################################
#
# fd.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring ARRL Field Day
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

############################################################################################
    
TRAP_ERRORS = False
TRAP_ERRORS = True

############################################################################################
    
# Scoring class for ARRL Field Day - Inherits the base contest scoring class
class ARRL_FD_SCORING(CONTEST_SCORING):
 
    def __init__(self,P):
        CONTEST_SCORING.__init__(self,P,'ARRL-FD',mode='MIXED')
        print('FD Scoring Init')
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m','6m','2m','70cm']
        self.MODES = ['CW','DG','PH']
        self.sec_cnt = np.zeros((len(FD_SECS),len(self.MODES),len(self.BANDS)))
        self.band_mode_cnt = np.zeros((len(self.MODES),len(self.BANDS)))
        tmp=[]
        for b in self.BANDS:
            for m in self.MODES:
                tmp.append((b+' '+m,[]))
        self.CALLS = OrderedDict(tmp)

        self.MY_CALL    = P.SETTINGS['MY_CALL']
        self.MY_CAT     = P.SETTINGS['MY_CAT']
        self.MY_SECTION = P.SETTINGS['MY_SEC']
        
        # Determine contest time - assumes this is done within a few hours of the contest
        # Contest occurs on 4th full weekend of June
        now = datetime.datetime.utcnow()
        year=now.year
        #year=2020                                                     # Test from last time I did FD
        day1=datetime.date(year,6,1).weekday()                         # Day of week of 1st of month 0=Monday, 6=Sunday
        sat4=1 + ((5-day1) % 7) + 21                                   # Day no. for 4th Saturday = 1 since day1 is the 1st of the month
                                                                       #    no. days until 1st Saturday (day 5) + 7 more days
        self.date0=datetime.datetime(year,6,sat4,18) 
        self.date1 = self.date0 + datetime.timedelta(hours=33)         # ... and ends at 0300/0400 UTC on Monday
        print('day1=',day1,'\tsat4=',sat4,'\tdate0=',self.date0)
        #sys.exit(0)
        
        # Manual override
        if False:
            self.date0 = datetime.datetime.strptime( "20200627 1800" , "%Y%m%d %H%M")  # Start of contest
            self.date1 = self.date0 + datetime.timedelta(hours=27)

        # Name of output file
        self.output_file = self.MY_CALL+'_FIELD_DAY_'+str(self.date0.year)+'.LOG'


    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_STATE)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SECTION)
        
    # Scoring routine for ARRL Field Day for a single qso
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):

        #print('\n',rec)

        # Pull out relavent entries
        call = rec["call"].upper()
        keys = list(rec.keys())
        if 'arrl_sect' in keys:
            cat_in = rec["class"].upper()
            sec_in = rec["arrl_sect"].upper()
            rx=cat_in+' '+sec_in
        elif "srx_string" in keys:
            rx   = rec["srx_string"].strip().upper()
            a    = rx.split(',')   
            cat_in = a[0]
            sec_in = a[1]
        else:
            print('\nQSO-SCORING - Whoops!  Cant figure out contest exchange')
            print('rec=',rec)
            cmd = 'fgrep "'+self.MY_CALL+' '+call+'" $HOME/logs/ALL_ft8_contest.TXT'
            #print('cmd=',cmd)
            os.system(cmd)
            sys.exit(0)
            
        cat_out = self.MY_CAT
        sec_out = self.MY_SECTION
        
        freq=float(rec["freq"])
        band     = rec["band"]
        freq_khz = self.convert_freq(freq,band)
        mode = rec["mode"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        # Group phone & digi modes
        mode = self.group_modes(mode)

        # Check rx'ed category and section
        n   = cat_in[:-1]
        cat = cat_in[-1]
        if not n.isdigit() or cat not in ['A','B','C','D','E','F']:
            print('Received category '+cat_in+' not recognized - srx=',rx)
            sys.exit(0)
        if sec_in not in FD_SECS:
            #print('FD Secs=',FD_SECS)
            print('call=',call)
            print('Received section '+sec_in+' not recognized - srx=',rx)
            print('History=',HIST[call])
            sys.exit(0)
        
        if False:
            print('\n',rec)
            print('\nfreq  = ',freq_khz)
            print('mode    = ',mode)
            print('exch in : ',cat_in,sec_in)
            print('exch out: ',cat_out,sec_out)
            print(n)
            print(cat)

        # Count up the qsos
        if not dupe:

            # Sort QSOs by mode
            if mode=='PH':
                qso_points=1
            elif mode=='CW' or mode=='DG':
                qso_points=2
            else:
                print('FD - Unknown mode',mode)
                sys.exit(0)

            self.CALLS[band+' '+mode].append(call)        

            # Non-duplicate & points
            self.nqsos2 += 1;
            self.total_points += qso_points

            # Just for fun, keep a count of each section by badn and mode
            idx1 = FD_SECS.index(sec_in)
            idx2 = self.MODES.index(mode)
            idx3 = self.BANDS.index(band)
            self.sec_cnt[idx1,idx2,idx3]   = 1
            self.band_mode_cnt[idx2,idx3] += 1

            # Info for multi-qsos
            exch_in=cat_in+' '+sec_in
            if call in self.EXCHANGES.keys():
                self.EXCHANGES[call].append(exch_in)
            else:
                self.EXCHANGES[call]=[exch_in]
            
        else:
            self.ndupes+=1


        # There is no official template for this so let's try something that makes sense
        #                              ----------info sent----------- ----------info rcvd----------- 
        #QSO:  freq  mo date       time call       ex1 ex2    call       ex1 ex2
        #QSO: ****** ** yyyy-mm-dd nnnn ********** aaa aaa    ********** aaa aaa
        #QSO:  14042 CW 1999-09-05 0000 AA2IL      2E  SDG    N6TR       1A  SV 
    
        line='QSO: %5d %2s %10s %4s %-10s %-3s %-3s    %-10s %-3s %-3s' % \
            (freq_khz,mode,date_off,time_off,self.MY_CALL,self.MY_CAT,self.MY_SEC,call,cat_in,sec_in)
        #print(line)
        #sys.exit(0)
        return line


    # Routine to sift through station we had multiple contacts with to identify any discrepancies
    def check_multis(self,qsos):

        problem=False
        for call in self.EXCHANGES.keys():
            exchs=self.EXCHANGES[call]
            mismatch = exchs.count(exchs[0]) != len(exchs)
            if mismatch:
                if not problem:
                    print('There are discrepancies with multiple qsos with the following stations:')
                print('call=',call,'\texchanges=',exchs)
                problem=True
                
        if not problem:
            print('There are were no other discrepancies found.')
        elif TRAP_ERRORS:
            print('\nCheck Multis - TRAPPED ERROR\n')
            sys.exit(0)
    
    # Summary & final tally
    def summary(self):
        
        for k in self.CALLS.keys():
            calls=sorted( self.CALLS[k] )
            if len(calls)>0:
                print('\n'+k+' - ',len(calls),' unique calls:')
                n=0
                for call in calls:
                    txt='%-8s' % (call)
                    print(txt,end=' ')
                    n+=1
                    if n==8:
                        n=0
                        print('')
                print('')
        print('')
    
        for i in range(len(FD_SECS)):
            #print(i,FD_SECS[i],self.BANDS)
            #print(self.sec_cnt[i])
            cnt=np.sum(self.sec_cnt[i])
            if cnt==0:
                print(FD_SECS[i],' - Missing')

        print('\nBand\t',self.MODES,'\tTotal')
        for b in self.BANDS:
            idx3 = self.BANDS.index(b)
            print(b,'\t',self.band_mode_cnt[:,idx3],'\t',int(np.sum(self.band_mode_cnt[:,idx3],axis=0)) )
        print('By Mode:\t',np.sum(self.band_mode_cnt,axis=1),int( np.sum(self.band_mode_cnt) ) )

        print('\nNo. raw QSOS (nqsos1)         =',self.nqsos1)
        print('No. skipped (e.g. rapid dupe) =',self.nskipped)
        print('No. dupes                     =',self.ndupes)
        print('No. unique QSOS (nqsos2)      =',self.nqsos2)
        mults = 2
        print('Power Mult                    =',mults)
        print('QSO Score (sans bonus)        =',self.total_points*mults)
        
        bonus = 0
        bonus += 100*2          # Emergency power x2 transmitters
        bonus += 100            # Solar power
        bonus += 100            # Copied W1AW bulletin
        bonus += 50             # Web entry
        
        print('Bonus Points                  =',bonus)
        print('Total Claimed Score           =',self.total_points*mults + bonus)

    

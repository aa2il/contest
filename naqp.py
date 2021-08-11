############################################################################################
#
# naqp.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring NAQP CW & RTTY contests
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
    
# Scoring class for NAQP CW & RTTY - Inherits the base contest scoring class
class NAQP_SCORING(CONTEST_SCORING):
 
    def __init__(self,P,MODE):
        CONTEST_SCORING.__init__(self,'NAQP-'+MODE,mode=MODE)
        print('NAQP Scoring Init')

        self.MY_CALL     = P.SETTINGS['MY_CALL']
        self.MY_NAME     = P.SETTINGS['MY_NAME']
        self.MY_STATE    = P.SETTINGS['MY_STATE']
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.sec_cnt = np.zeros((len(NAQP_SECS),len(self.BANDS)))        

        # Determine contest time - assumes this is dones wihtin a few hours of the contest
        now = datetime.datetime.utcnow()
        day=7
        start_hour=18
        self.date0=datetime.datetime(now.year,now.month,day,start_hour)
        self.date1 = self.date0 + datetime.timedelta(hours=12)
                

    # Scoring routine for NAQP CW and RTTY
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):
        #print('rec=',rec)
        keys=list(HIST.keys())

        # Pull out relavent entries
        call = rec["call"].upper()
        qth  = rec["qth"].upper()
        name = rec["name"].upper()
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        band = rec["band"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        if MY_MODE=='CW':
            mode='CW'
        elif MY_MODE=='RTTY':
            mode='RY'
        else:
            print('Invalid mode',MY_MODE)
            sys.exit(1)

        """
        # In 2017, there was some inconsistancies in how the name & state were saved
        if call=='AA2IL' or qth==name:
            print('\n******** Houston, we have a problem:')
            print('\tcall=',call)
            print('\tqth=',qth)
            print('\tname=',name)
            sys.exit(0)
        elif len(qth)>2 and len(name)==2:
            tmp=qth
            qth=name
            name=tmp
        elif len(qth)==2 and len(name)==2 and (not (qth in NAQP_SECS)) or (name in NAQP_SECS):
            print('\n--- Check this one for to make sure name & qth are not reversed ---')
            print('call=',call,'\t\tname=',name,'\t\tqth=',qth)
        """

        # Sometimes, I'll put a "?" to indicate that I need to review
        if '?' in call+name+qth:
            print('\n??? Check this one again: ???')
            print('call=',call,'\t\tname=',name,'\t\tqth=',qth)
            self.list_all_qsos(call,qsos)
            if TRAP_ERRORS:
                sys.exit(0)

        # Misc fix-ups
        if qth=='PY':
            qth='DX'

        try:
            idx1 = NAQP_SECS.index(qth)
            idx2 = self.BANDS.index(band)
            self.sec_cnt[idx1,idx2] = 1
        except:
            print('\n$$$$$$$$$$$$$$$$$$$$$$')
            print(qth,' not found in list of NAQP sections',len(qth))
            print(rec)
            print('$$$$$$$$$$$$$$$$$$$$$$')
            if TRAP_ERRORS:
                sys.exit(0)
    
        if not dupe:
            self.nqsos2 += 1;

#                              ----------info sent----------- ----------info rcvd----------- 
#QSO: freq  mo date       time call            ex1        ex2 call            ex1        ex2 t
#QSO: ***** ** yyyy-mm-dd nnnn **********      aaaaaaaaaa aaa **********      aaaaaaaaaa aaa n
#QSO: 14042 CW 1999-09-05 0000 N5KO            TREY       CA  N6TR          1 TREE       OR

        line='QSO: %5d %2s %10s %4s %-10s      %-10s %-3s %-10s      %-10s %-3s' % \
            (freq_khz,mode,date_off,time_off, \
             self.MY_CALL,self.MY_NAME,self.MY_STATE,
             call,name,qth)
        #print line

        # Check against history
        if call in keys:
            state=HIST[call]['state']
            if state=='':
                sec  =HIST[call]['sec']
                if sec in STATES+PROVINCES:
                    state=sec
            name9=HIST[call]['name']
            #print call,qth,state
            if qth!=state or name!=name9:
                print('\n$$$$$$$$$$ Difference from history $$$$$$$$$$$')
                print(call,':  Current:',qth,name,' - History:',state,name9)
                self.list_all_qsos(call,qsos)
                print('hist=',HIST[call])
                print(' ')

        else:
            print('\n++++++++++++ Warning - no history for call:',call)
            self.list_all_qsos(call,qsos)
            self.list_similar_calls(call,qsos)

            #print 'dist=',similar('K5WA','N5WA')
            #sys.exit(0)

        return line
            
    # Summary & final tally
    def summary(self):

        mults1 = np.sum(self.sec_cnt,axis=0)
        mults = [int(i) for i in mults1]
        print('nqsos2=',self.nqsos2)
        print('mults=',mults,'  =  ',int(sum(mults)))
        print('total score=',sum(mults)*self.nqsos2)
        if False:
            for j in range(len(BANDS)):
                print(BANDS[j])
                for i in range(len(NAQP_SECS)):
                    if self.sec_cnt[i,j]==0:
                        print('Missing ',NAQP_SECS[i])


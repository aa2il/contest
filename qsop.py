############################################################################################
#
# qsop.py - Rev 1.0
# Copyright (C) 2022-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring state QSO parties.
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
from counties import *

############################################################################################
    
TRAP_ERRORS = False
TRAP_ERRORS = True

VERBOSITY=0
    
############################################################################################
    
# Scoring class for state QSP parties
class QSOP_SCORING(CONTEST_SCORING):
 
    def __init__(self,P,MODE,STATE):

        if STATE=='WA':
            contest_name=STATE+'-SALMON-RUN'
        else:
            contest_name=STATE+'-QSO-PARTY'
        
        CONTEST_SCORING.__init__(self,P,contest_name,mode=MODE)
        print('State QSO Party Scoring - ',STATE)

        self.MY_CALL     = P.SETTINGS['MY_CALL']
        self.MY_STATE    = P.SETTINGS['MY_STATE']

        self.STATE       = STATE
        self.MULTS       = []

        self.QSO_POINTS=[1,1,1]            # CW, PHONE, DIGI

        now = datetime.datetime.utcnow()
        year = now.strftime('%Y').upper()
        print('year=',year)
            
        self.date0 = datetime.datetime.strptime( year+"0101 0000" , "%Y%m%d %H%M")  # Whole year
        self.date1 = self.date0 + datetime.timedelta(days=365)
        self.COUNTIES=[]
        
        if STATE=='NY':
            self.QSO_POINTS=[2,1,1]
        elif STATE=='DE':
            # DE happens on the same weekend as New England and W7 QPs so the counties are a bit goofy
            for c in COUNTIES['DE']:
                self.COUNTIES.append('DE'+c)
        elif STATE=='W7':
            # 7th call area
            self.contest='7QP'
            for s in W7_STATES:
                state=s.replace('7QP','')
                for c in COUNTIES[s]:
                    self.COUNTIES.append(state+c)
        elif STATE=='W1':
            # New England
            self.contest='NEQP'
            for s in W1_STATES:
                for c in COUNTIES[s]:
                    self.COUNTIES.append(s+c)
        else:
            self.COUNTIES=COUNTIES[STATE]
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.band_cnt = np.zeros((len(self.BANDS)),dtype=int)
        self.sec_cnt = np.zeros((len(self.COUNTIES),),dtype=int)
        self.TRAP_ERRORS = TRAP_ERRORS

        # Manual override
        if False:
            self.date0 = datetime.datetime.strptime( "20221015 1400" , "%Y%m%d %H%M")  # NYQP
            self.date1 = self.date0 + datetime.timedelta(hours=12)
        
        # Name of output file - stupid web uploader doesn't recognize .LOG extenion!
        self.output_file = self.MY_CALL+'_'+STATE+'QP_'+MODE+'_'+str(self.date0.year)+'.CBR'
        #sys.exit(0)

    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_STATE)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SECTION)
                            
    # Scoring routine for State QSO Parties
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):
        if VERBOSITY>0:
            print('rec=',rec)
        keys=list(HIST.keys())

        # Check for correct contest
        id   = rec["contest_id"].upper()
        if id!=self.STATE+'-QSO-PARTY':
            if VERBOSITY>0:
                print('contest=',self.contest,id)
                print('QSO not part of',self.STATE,'QSO Party - skipping')
            return
        #else:
        #    print('\nrec=',rec)
        #    print('id=',id,'\t\t',self.STATE+'-QSO-PARTY')
        #    sys.exit(0)

        # Pull out relavent entries
        call = rec["call"].upper()
        try:
            qth = rec["qth"].upper()
        except:
            srx = rec["srx_string"].upper().split(',')
            qth = srx[1]
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        band = rec["band"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
        if MY_MODE=='CW':
            mode='CW'
        else:
            print('Invalid mode',MY_MODE)
            sys.exit(1)

        if qth=='DX':
            print('DX contact - skipping')
            return

        
        if dupe:
            print('\nDUPE!!!! rec=',rec)
            #sys.exit(1)
        

        if not dupe:
            #self.nqsos2 += 1;

            try:
                idx2 = self.BANDS.index(band)
                self.band_cnt[idx2] += 1
                if len(self.COUNTIES)>0:
                    qth2=qth.split('/')
                    for qth1 in qth2:
                        self.nqsos2 += 1;
                        if self.STATE=='W7' and len(qth2)>1 and len(qth1)==3:
                            qth1=qth2[0][0:2] + qth1
                        idx1 = self.COUNTIES.index(qth1)
                        self.sec_cnt[idx1] = 1
                        self.MULTS.append(qth1)
                        #self.sec_cnt[idx1,idx2] = 1
                else:
                    print('Consider adding list of counties for this party!\t',qth)
                    sys,exit(0)
            except Exception as e: 
                print('\n$$$$$$$$$$$$$$$$$$$$$$')
                print( 'QSO SCORING - ERROR:',str(e) )
                print('call=',call,'\tqth=',qth,' not found in list of Counties')
                print('counties=',self.COUNTIES)
                print('rec=',rec)
                self.list_all_qsos(call,qsos)
                print('$$$$$$$$$$$$$$$$$$$$$$')
                if TRAP_ERRORS:
                    sys.exit(0)
    
            # Info for multi-qsos
            exch_in=qth
            if call in self.EXCHANGES.keys():
                self.EXCHANGES[call].append(exch_in)
            else:
                self.EXCHANGES[call]=[exch_in]

        line=[]
        qth2=qth.split('/')
        for qth1 in qth2:
            line.append(
                'QSO: %5d %2s %10s %4s %-10s      %-10s %-3s %-10s      %-10s %-3s' % \
                (freq_khz,mode,date_off,time_off, \
                self.MY_CALL,'599',self.MY_STATE,
                 call,'599',qth1))
        """
        print(line)
        print(type(line))
        print(len(line))
        print(len(line[0]))
        sys.exit(0)
        """

        # Check against history - REVISIT!!!!
        if call in keys and False:
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

        self.MULTS = list( set( self.MULTS ))
        mults = self.sec_cnt
        if self.STATE in ['IL','NY']:
            pts_per_qso=2
        elif self.STATE=='W7':
            pts_per_qso=3
        elif self.STATE=='W1':
            pts_per_qso=2
        else:
            pts_per_qso=1
        
        print('\nNo. QSOs        =',self.nqsos1)
        print('No. Uniques     =',self.nqsos2)
        print('No. Skipped     =',self.nskipped)
        print('\nBand\tQSOs')
        for i in range(len(self.BANDS)):
            print(self.BANDS[i],'\t',self.band_cnt[i])
        print('\nQSOs            =',self.nqsos2)
        print('Mults           =',sum(mults),'\t',self.MULTS,
              '\t',len(self.MULTS),'/',len(self.COUNTIES))
        print('Claimed score=',sum(mults)*self.nqsos2*pts_per_qso)

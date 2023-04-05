############################################################################################
#
# naqp.py - Rev 1.0
# Copyright (C) 2022-3 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring state QSO parties
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

VERBOSITY=0

NY_COUNTIES = ['ALB',	'ALL',	'BRX',	'BRM',	'CAT',	'CAY',	'CHA',	'CHE',	'CGO',	'CLI',	'COL',	'COR',	'DEL',	'DUT',	'ERI',	'ESS',	'FRA',	'FUL',	'GEN',	'GRE',	'HAM',	'HER',	'JEF',	'KIN',	'LEW',	'LIV',	'MAD',	'MON',	'MTG',	'NAS',	'NEW',	'NIA',	'ONE',	'ONO',	'ONT',	'ORA',	'ORL',	'OSW',	'OTS',	'PUT',	'QUE',	'REN',	'ROC',	'RIC',	'SAR',	'SCH',	'SCO',	'SCU',	'SEN',	'STL',	'STE',	'SUF',	'SUL',	'TIO',	'TOM',	'ULS',	'WAR',	'WAS',	'WAY',	'WES',	'WYO',	'YAT']

IL_COUNTIES=['ADAM',	'ALEX',	'BOND',	'BOON',	'BROW',	'BURO',	'CALH',	'CARR',	'CASS',	'CHAM',	'CHRS',	'CLRK',	'CLAY',	'CLNT',	'COLE',	'COOK',	'CRAW',	'CUMB',	'DEKA',	'DEWT',	'DOUG',	'DUPG',	'EDGR',	'EDWA',	'EFFG',	'FAYE',	'FORD',	'FRNK',	'FULT',	'GALL',	'GREE',	'GRUN',	'HAML',	'HANC',	'HARD',	'HNDR',	'HENR',	'IROQ',	'JACK',	'JASP',	'JEFF',	'JERS',	'JODA',	'JOHN',	'KANE',	'KANK',	'KEND',	'KNOX',	'LAKE',	'LASA',	'LAWR',	'LEE',	'LIVG',	'LOGN',	'MACN',	'MCPN',	'MADN',	'MARI',	'MSHL',	'MASN',	'MSSC',	'MCDN',	'MCHE',	'MCLN',	'MNRD',	'MRCR',	'MNRO',	'MNTG',	'MORG',	'MOUL',	'OGLE',	'PEOR',	'PERR',	'PIAT',	'PIKE',	'POPE',	'PULA',	'PUTN',	'RAND',	'RICH',	'ROCK',	'SALI',	'SANG',	'SCHY',	'SCOT',	'SHEL',	'STAR',	'SCLA',	'STEP',	'TAZW',	'UNIO',	'VERM',	'WABA',	'WARR',	'WASH',	'WAYN',	'WHIT',	'WTSD',	'WILL',	'WMSN',	'WBGO',	'WOOD']

ID_COUNTIES=['ADA','ADM','BAN','BEA','BEN','BIN','BLA','BOI','BNR','BNV','BOU','BUT','CAM','CAN','CAR','CAS','CLA','CLE','CUS','ELM','FRA','FRE','GEM','GOO','IDA','JEF','JER','KOO','LAT','LEM','LEW','LIN','MAD','MIN','NEZ','ONE','OWY','PAY','POW','SHO','TET','TWI','VAL','WAS']

############################################################################################
    
# Scoring class for state QSP parties
class QSOP_SCORING(CONTEST_SCORING):
 
    def __init__(self,P,MODE,STATE):
        CONTEST_SCORING.__init__(self,P,STATE+'-QSO-PARTY',mode=MODE)
        print('State QSO Party Scoring - ',STATE)

        self.MY_CALL     = P.SETTINGS['MY_CALL']
        self.MY_STATE    = P.SETTINGS['MY_STATE']

        self.STATE       = STATE
        if STATE=='NY':
            self.date0 = datetime.datetime.strptime( "20221015 1400" , "%Y%m%d %H%M")  # NYQP
            self.date1 = self.date0 + datetime.timedelta(hours=12)
            self.COUNTIES=NY_COUNTIES
        elif STATE=='IL':
            self.date0 = datetime.datetime.strptime( "20221016 1700" , "%Y%m%d %H%M")  # NYQP
            self.date1 = self.date0 + datetime.timedelta(hours=8)
            self.COUNTIES=IL_COUNTIES
        elif STATE in ['ID','VA']:
            self.date0 = datetime.datetime.strptime( "20230101 0000" , "%Y%m%d %H%M")  # NYQP
            self.date1 = self.date0 + datetime.timedelta(days=365)
            self.COUNTIES=[]
            #self.COUNTIES=ID_COUNTIES
        else:
            print('QSOP_SCORING: Unknown state party -',STATE)
            sys.exit(0)
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.band_cnt = np.zeros((len(self.BANDS)))
        self.sec_cnt = np.zeros((len(self.COUNTIES),))
        self.TRAP_ERRORS = TRAP_ERRORS

        # Manual override
        if False:
            self.date0 = datetime.datetime.strptime( "20221015 1400" , "%Y%m%d %H%M")  # NYQP
            self.date1 = self.date0 + datetime.timedelta(hours=12)
        
        # Name of output file - stupid web uploader doesn't recognize .LOG extenion!
        self.output_file = self.MY_CALL+'_'+STATE+'QP_'+MODE+'_'+str(self.date0.year)+'.TXT'
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

        if not dupe:
            self.nqsos2 += 1;

            try:
                idx2 = self.BANDS.index(band)
                self.band_cnt[idx2] += 1
                if len(self.COUNTIES)>0:
                    qth2=qth.split('/')
                    for qth1 in qth2:
                        idx1 = self.COUNTIES.index(qth1)
                        self.sec_cnt[idx1] = 1
                        #self.sec_cnt[idx1,idx2] = 1
                else:
                    print('Consider adding list of counties for this party!\t',qth)
            except Exception as e: 
                print( str(e) )
                print('\n$$$$$$$$$$$$$$$$$$$$$$')
                print(qth,' not found in list of Counties')
                print(self.COUNTIES)
                print(rec)
                print('$$$$$$$$$$$$$$$$$$$$$$')
                if TRAP_ERRORS:
                    sys.exit(0)
    
            # Info for multi-qsos
            exch_in=qth
            if call in self.EXCHANGES.keys():
                self.EXCHANGES[call].append(exch_in)
            else:
                self.EXCHANGES[call]=[exch_in]
                
        line='QSO: %5d %2s %10s %4s %-10s      %-10s %-3s %-10s      %-10s %-3s' % \
            (freq_khz,mode,date_off,time_off, \
             self.MY_CALL,'599',self.MY_STATE,
             call,'599',qth)
        #print line

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

        #mults1 = np.sum(self.sec_cnt,axis=0)
        #mults = [int(i) for i in mults1]
        mults = self.sec_cnt
        
        print('\nNo. QSOs        =',self.nqsos1)
        print('No. Uniques     =',self.nqsos2)
        print('No. Skipped     =',self.nskipped)
        print('Band Count      =',self.band_cnt,'  =  ',int(sum(self.band_cnt)))
        print('Mults           =',mults,'  =  ',int(sum(mults)))
        print('Claimed score=',sum(mults)*self.nqsos2)
        if False:
            for j in range(len(BANDS)):
                print(BANDS[j])
                for i in range(len(NAQP_SECS)):
                    if self.sec_cnt[i,j]==0:
                        print('Missing ',NAQP_SECS[i])


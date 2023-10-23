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

COUNTIES={}

COUNTIES['AZ']=['APH','CHS','CNO','GLA','GHM','GLE','LPZ','MCP','MHV','NVO','PMA','PNL','SCZ',
                'YVP','YMA']

COUNTIES['CT']=['FAI','HAR','LIT','MID','NHV','NLN','TOL','WIN']

COUNTIES['DE']=['NDE','KDE','SDE']

COUNTIES['HI']=['NII','KAU','LHN','WHN','PRL','HON','MOL','KAL','LNI','MAU','KOH','HIL','KON','VOL']

COUNTIES['IA']=['ADR','ADM','ALL','APP','AUD','BEN','BKH','BOO','BRE','BUC','BNV','BTL','CAL','CAR',
                'CAS','CED','CEG','CHE','CHI','CLR','CLA','CLT','CLN','CRF','DAL','DAV','DEC','DEL',
                'DSM','DIC','DUB','EMM','FAY','FLO','FRA','FRE','GRE','GRU','GUT','HAM','HAN','HDN',
                'HRS','HEN','HOW','HUM','IDA','IOW','JAC','JAS','JEF','JOH','JON','KEO','KOS','LEE',
                'LIN','LOU','LUC','LYN','MAD','MAH','MRN','MSL','MIL','MIT','MNA','MOE','MTG','MUS',
                'OBR','OSC','PAG','PLA','PLY','POC','POL','POT','POW','RIN','SAC','SCO','SHE','SIO',
                'STR','TAM','TAY','UNI','VAN','WAP','WAR','WAS','WAY','WEB','WNB','WNS','WOO','WOR',
                'WRI',]

COUNTIES['ID']=['ADA','ADM','BAN','BEA','BEN','BIN','BLA','BOI','BNR','BNV','BOU','BUT','CAM','CAN',
                'CAR','CAS','CLA','CLE','CUS','ELM','FRA','FRE','GEM','GOO','IDA','JEF','JER','KOO',
                'LAT','LEM','LEW','LIN','MAD','MIN','NEZ','ONE','OWY','PAY','POW','SHO','TET','TWI',
                'VAL','WAS']

COUNTIES['IL']=['ADAM','ALEX','BOND','BOON','BROW','BURO','CALH','CARR','CASS','CHAM','CHRS','CLRK',
                'CLAY','CLNT','COLE','COOK','CRAW','CUMB','DEKA','DEWT','DOUG','DUPG','EDGR','EDWA',
                'EFFG','FAYE','FORD','FRNK','FULT','GALL','GREE','GRUN','HAML','HANC','HARD','HNDR',
                'HENR','IROQ','JACK','JASP','JEFF','JERS','JODA','JOHN','KANE','KANK','KEND','KNOX',
                'LAKE','LASA','LAWR','LEE','LIVG','LOGN','MACN','MCPN','MADN','MARI','MSHL','MASN',
                'MSSC','MCDN','MCHE','MCLN','MNRD','MRCR','MNRO','MNTG','MORG','MOUL','OGLE','PEOR',
                'PERR','PIAT','PIKE','POPE','PULA','PUTN','RAND','RICH','ROCK','SALI','SANG','SCHY',
                'SCOT','SHEL','STAR','SCLA','STEP','TAZW','UNIO','VERM','WABA','WARR','WASH','WAYN',
                'WHIT','WTSD','WILL','WMSN','WBGO','WOOD']

COUNTIES['IN']=['INADA','INALL','INBAR','INBEN','INBLA','INBOO','INBRO','INCAR','INCAS','INCLR',
                'INCLY','INCLI','INCRA','INDAV','INDEA','INDEC','INDEK','INDEL','INDUB','INELK',
                'INFAY','INFLO','INFOU','INFRA','INFUL','INGIB''INGRA','INGRE','INHAM','INHAN',
                'INHAR','INHND','INHNR','INHOW','INHUN','INJAC','INJAS','INJAY','INJEF','INJEN',
                'INJOH','INKNO','INKOS','INLAG','INLAK','INLAP','INLAW','INMAD','INMRN','INMRS',
                'INMRT','INMIA','INMNR','INMNT','INMOR','INNEW','INNOB','INOHI','INORA','INOWE',
                'INPAR','INPER','INPIK','INPOR','INPOS','INPUL','INPUT','INRAN','INRIP','INRUS',
                'INSCO','INSHE','INSPE','INSTA','INSTE','INSTJ','INSUL','INSWI','INTPP','INTPT',
                'INUNI','INVAN','INVER','INVIG','INWAB','INWRN','INWRK','INWAS','INWAY','INWEL',
                'INWHT','INWHL']

COUNTIES['KS']=['ALL','AND','ATC','BAR','BRT','BOU','BRO','BUT','CHS','CHT','CHE','CHY','CLK','CLY','CLO',
	        'COF','COM','COW','CRA','DEC','DIC','DON','DOU','EDW','ELK','ELL','ELS','FIN','FOR','FRA',
	        'GEA','GOV','GRM','GRT','GRY','GLY','GRE','HAM','HPR','HVY','HAS','HOG','JAC','JEF','JEW',
	        'JOH','KEA','KIN','KIO','LAB','LAN','LEA','LCN','LIN','LOG','LYO','MRN','MSH','MCP','MEA',
	        'MIA','MIT','MGY','MOR','MTN','NEM','NEO','NES','NOR','OSA','OSB','OTT','PAW','PHI','POT',
	        'PRA','RAW','REN','REP','RIC','RIL','ROO','RUS','RSL','SAL','SCO','SED','SEW','SHA','SHE',
	        'SMN','SMI','STA','STN','STE','SUM','THO','TRE','WAB','WAL','WAS','WIC','WIL','WOO','WYA']

COUNTIES['ME']=['AND','ARO','CUM','FRA','HAN','KEN','KNO','LIN','OXF','PEN',
                'PIS','SAG','SOM','WAL','WAS','YOR']

COUNTIES['MA']=['BAR','BER','BRI','DUK','ESS','FRA','HMD','HMP','MID','NAN',
                'NOR','PLY','SUF','WOR']

COUNTIES['MT']=['BEA','BIG','BLA','BRO','CRB','CRT','CAS','CHO','CUS','DAN','DAW','DEE','FAL','FER',
                'FLA','GAL','GAR','GLA','GOL','GRA','HIL','JEF','JUD','LAK','LEW','LIB','LIN','MAD',
                'MCC','MEA','MIN','MIS','MUS','PAR','PET','PHI','PON','PWD','PWL','PRA','RAV','RIC',
                'ROO','ROS','SAN','SHE','SIL','STI','SWE','TET','TOO','TRE','VAL','WHE','WIB','YEL']

COUNTIES['NH']=['BEL','CAR','CHE','COO','GRA','HIL','MER','ROC','STR','SUL']

COUNTIES['NV'] = ['CAR','CHU','CLA','DOU','ELK','ESM','EUR','HUM','LAN','LIN','LYO','MIN','NYE','PER',
                  'STO','WAS','WHI']

COUNTIES['NJ']=['ATLA','BERG','BURL','CAPE','CMDN','CUMB','ESSE','GLOU','HUDS','HUNT','MERC','MID',
                'MONM','MORR','OCEA','PASS','SALE','SOME','SUSS','UNIO','WRRN']

COUNTIES['NY'] = ['ALB','ALL','BRX','BRM','CAT','CAY','CHA','CHE','CGO','CLI','COL','COR','DEL',
                  'DUT','ERI','ESS','FRA','FUL','GEN','GRE','HAM','HER','JEF','KIN','LEW','LIV',
                  'MAD','MON','MTG','NAS','NEW','NIA','ONE','ONO','ONT','ORA','ORL','OSW','OTS',
                  'PUT','QUE','REN','ROC','RIC','SAR','SCH','SCO','SCU','SEN','STL','STE','SUF',
                  'SUL','TIO','TOM','ULS','WAR','WAS','WAY','WES','WYO','YAT']

COUNTIES['OH'] = ['ADAM','ALLE','ASHL','ASHT','ATHE','AUGL','BELM','BROW','BUTL','CARR','CHAM','CLAR',
                  'CLER','CLIN','COLU','COSH','CRAW','CUYA','DARK','DEFI','DELA','ERIE','FAIR','FAYE',
                  'FRAN','FULT','GALL','GEAU','GREE','GUER','HAMI','HANC','HARD','HARR','HENR','HIGH',
                  'HOCK','HOLM','HURO','JACK','JEFF','KNOX','LAKE','LAWR','LICK','LOGA','LORA','LUCA',
                  'MADI','MAHO','MARI','MEDI','MEIG','MERC','MIAM','MONR','MONT','MORG','MORR','MUSK',
                  'NOBL','OTTA','PAUL','PERR','PICK','PIKE','PORT','PREB','PUTN','RICH','ROSS','SAND',
                  'SCIO','SENE','SHEL','STAR','SUMM','TRUM','TUSC','UNIO','VANW','VINT','WARR','WASH',
                  'WAYN','WILL','WOOD','WYAN']

COUNTIES['OR'] = ['BAK','BEN','CLK','CLT','COL','COO','CRO','CUR','DES','DOU','GIL','GRA','HAR',
                  'HOO','JAC','JEF','JOS','KLA','LAK','LAN','LCN','LNN','MAL','MAR','MOR','MUL',
                  'POL','SHE','TIL','UMA','UNI','WAL','WCO','WSH','WHE','YAM']

COUNTIES['RI']=['BRI','KEN','NEW','PRO','WAS']

COUNTIES['TX']=['ANDE','ANDR','ANGE','ARAN','ARCH','ARMS','ATAS','AUST','BAIL','BAND','BAST','BAYL',
                'BEE','BELL','BEXA','BLAN','BORD','BOSQ','BOWI','BZIA','BZOS','BREW','BRIS','BROO',
                'BROW','BURL','BURN','CALD','CALH','CALL','CMRN','CAMP','CARS','CASS','CAST','CHAM',
                'CHER','CHIL','CLAY','COCH','COKE','COLE','COLN','COLW','COLO','COML','COMA','CONC',
                'COOK','CORY','COTT','CRAN','CROC','CROS','CULB','DALM','DALS','DAWS','DSMI','DELT',
                'DENT','DEWI','DICK','DIMM','DONL','DUVA','EAST','ECTO','EDWA','EPAS','ELLI','ERAT',
                'FALL','FANN','FAYE','FISH','FLOY','FOAR','FBEN','FRAN','FREE','FRIO','GAIN','GALV',
                'GARZ','GILL','GLAS','GOLI','GONZ','GRAY','GRSN','GREG','GRIM','GUAD','HALE','HALL',
                'HAMI','HANS','HDMN','HRDN','HARR','HRSN','HART','HASK','HAYS','HEMP','HEND','HIDA',
                'HILL','HOCK','HOOD','HOPK','HOUS','HOWA','HUDS','HUNT','HUTC','IRIO','JACK','JKSN',
                'JASP','JDAV','JEFF','JHOG','JWEL','JOHN','JONE','KARN','KAUF','KEND','KENY','KENT',
                'KERR','KIMB','KING','KINN','KLEB','KNOX','LAMA','LAMB','LAMP','LSAL','LAVA','LEE',
                'LEON','LIBE','LIME','LIPS','LIVO','LLAN','LOVI','LUBB','LYNN','MADI','MARI','MART',
                'MASO','MATA','MAVE','MCUL','MLEN','MMUL','MEDI','MENA','MIDL','MILA','MILL','MITC',
                'MONT','MGMY','MOOR','MORR','MOTL','NACO','NAVA','NEWT','NOLA','NUEC','OCHI','OLDH',
                'ORAN','PPIN','PANO','PARK','PARM','PECO','POLK','POTT','PRES','RAIN','RAND','REAG',
                'REAL','RRIV','REEV','REFU','ROBE','RBSN','ROCK','RUNN','RUSK','SABI','SAUG','SJAC',
                'SPAT','SSAB','SCHL','SCUR','SHAC','SHEL','SHMN','SMIT','SOME','STAR','STEP','STER',
                'STON','SUTT','SWIS','TARR','TAYL','TERL','TERY','THRO','TITU','TGRE','TRAV','TRIN',
                'TYLE','UPSH','UPTO','UVAL','VVER','VZAN','VICT','WALK','WALL','WARD','WASH','WEBB',
                'WHAR','WHEE','WICH','WILB','WILY','WMSN','WLSN','WINK','WISE','WOOD','YOAK','YOUN',
                'ZAPA','ZAVA']

COUNTIES['UT'] = ['BEA','BOX','CAC','CAR','DAG','DAV','DUC','EME','GAR','GRA','IRO','JUA','KAN',
                  'MIL','MOR','PIU','RIC','SAL','SNJ','SNP','SEV','SUM','TOO','UIN','UTA','WST',
                  'WSH','WAY','WEB']

COUNTIES['VT']=['ADD','BEN','CAL','CHI','ESS','FRA','GRA','LAM','ORA','ORL',
                'RUT','WAS','WNH','WND']

# There is a different set of abbrevs for the 7QP and Salman RUn (State QP)
COUNTIES['WA7QP'] = ['ADA','ASO','BEN','CHE','CLL','CLR','COL','COW','DOU','FER','FRA','GAR','GRN',
                  'GRY','ISL','JEF','KLI','KNG','KTP','KTT','LEW','LIN','MAS','OKA','PAC','PEN',
                  'PIE','SAN','SKG','SKM','SNO','SPO','STE','THU','WAH','WAL','WHA','WHI','YAK']

COUNTIES['WA'] = ['ADA','ASO','BEN','CHE','CLAL','CLAR','COL','COW','DOU','FER','FRA','GAR','GRAN',
                  'GRAY','ISL','JEFF','KING','KITS','KITT','KLI','LEW','LIN','MAS','OKA','PAC',
                  'PEND','PIE','SAN','SKAG','SKAM','SNO','SPO','STE','THU','WAH','WAL','WHA','WHI','YAK']

COUNTIES['WY'] = ['ALB','BIG','CAM','CAR','CON','CRO','FRE','GOS','HOT','JOH','LAR','LIN','NAT',
                  'NIO','PAR','PLA','SHE','SUB','SWE','TET','UIN','WAS','WES']

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
        if STATE=='NY':
            self.QSO_POINTS=[2,1,1]
            
        """
        elif STATE=='IL':
            self.date0 = datetime.datetime.strptime( "20221016 1700" , "%Y%m%d %H%M")  # ILQP
            self.date1 = self.date0 + datetime.timedelta(hours=8)
            self.COUNTIES=IL_COUNTIES
        elif STATE in ['W1','W7','DE','HI','IA','ID','IN','NJ','KS','NH','OH','TX','VA','WA']:
        """
        if 1:
            self.date0 = datetime.datetime.strptime( "20230101 0000" , "%Y%m%d %H%M")  # Whole year
            self.date1 = self.date0 + datetime.timedelta(days=365)
            self.COUNTIES=[]
            if STATE=='DE':
                # DE happens on the same weekend as New England and W7 QPs so the counties are a bit goofy
                for c in COUNTIES['DE']:
                    self.COUNTIES.append('DE'+c)
            elif STATE=='W7':
                # 7th call area
                self.contest='7QP'
                for s in ['AZ','ID','MT','NV','OR','UT','WA7QP','WY']:
                    for c in COUNTIES[s]:
                        self.COUNTIES.append(s+c)
            elif STATE=='W1':
                # New England
                self.contest='NEQP'
                for s in ['CT','ME','MA','NH','RI','VT']:
                    for c in COUNTIES[s]:
                        self.COUNTIES.append(c+s)
            else:
                self.COUNTIES=COUNTIES[STATE]
        #else:
        #    print('QSOP_SCORING: Unknown state party -',STATE)
        #    sys.exit(0)
        
        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        self.band_cnt = np.zeros((len(self.BANDS)),dtype=int)
        self.sec_cnt = np.zeros((len(self.COUNTIES),),dtype=int)
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
                print( 'QSO SCORING - ERROR:',str(e) )
                print('\n$$$$$$$$$$$$$$$$$$$$$$')
                print('call=',call,'\tqth=',qth,' not found in list of Counties')
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

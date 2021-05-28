# Routines for scoring ARRL Sweepstakes

import sys
import datetime
from rig_io.ft_tables import *
from scoring import CONTEST_SCORING
from dx.spot_processing import Station  #, Spot, WWV, Comment, ChallengeData

#######################################################################################
    
# Scoring class for CWops mini tests - Inherits the base contest scoring class
class ARRL_SS_SCORING(CONTEST_SCORING):
 
    def __init__(self,contest):
        CONTEST_SCORING.__init__(self,contest)
        
        self.sec_cnt = np.zeros(len(ARRL_SECS))

    # Scoring routine for ARRL CW Sweepstakes
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):
        #print rec

        keys=list(HIST.keys())

        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) +0.5 )
        band = rec["band"]
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        if 'srx_string' in rec:
            if False:
                rexch  = rec["srx_string"].strip().upper().split(' ')
                serial = rexch[0]
                prec   = rexch[1]
                call2  = rexch[2]
                check  = rexch[3]
                sec    = rexch[4]
            else:
                rexch  = rec["srx_string"].strip().upper()
                #print rexch

                # Check for call
                call_ok = rexch.find(call)>=0
                if call_ok:
                    rexch=rexch.replace(call,'')
                    call2=call
                else:
                    print('\n*** CALL MISMATCH or NOT FOUND ***')
                    print(rec)
                    print(call)
                    print(rexch)
                    call2='????'

                # Find serial
                s=''
                i=0
                for ch in rexch:
                    if not ch.isalpha():
                        s=s+ch
                        i+=1
                    else:
                        break
                if s=='':
                    print('\n*** ERROR - No serial number - setting to 0')
                    print(rec)
                    print(rexch)
                    s='0'

                try:
                    serial=int(s)
                    print('serial=',serial,i)
                except:
                    print('BAD serial',s)
                    serial=0

                # Find prec
                #print(rexch[i:])
                for ch in rexch[i:]:
                    if ch.isalpha():
                        i+=1
                        s=s+ch
                        break
                prec=ch
                if not prec in ['Q','A','B','U','M','S']:
                    print('\n*** ERROR - Bad PREC:',prec,'\tcall=',call)
                    print(rec)
                    #sys,exit(0)
                #print 'prec=',prec,i

                # Find check
                s=''
                for ch in rexch[i:]:
                    #print ch,ch.isalpha()
                    if not ch.isalpha():
                        i+=1
                        s=s+ch
                    else:
                        break

                try:
                    check=int(s)
                    #print('check=',check,i)
                except:
                    print('BAD Check',s)
                    check=-1

                # Find section
                sec=''
                for ch in rexch[i:]:
                    #print ch,ch.isalpha()
                    if ch.isalpha():
                        i+=1
                        sec=sec+ch
                    else:
                        break
                if sec=='PEI':
                    sec='PE'
                #print 'sec=',sec,i

            try:
                idx = ARRL_SECS.index(sec)
                self.sec_cnt[idx] += 1
            except:
                print('Well that didnt work - sec=',sec)

            if not dupe:
                self.nqsos2 += 1;

        else:
            print(" ")
            print("*** ERROR - Problem with record")
            print(rec)
            print(" ")

        # Construct sent data
        try:
            serial_out = int( rec["stx"] )
        except:
            print('BAD Serial Out:',rec["stx"] )
            serial_out = -1
            
        #exch_out = '%3.3d %c %s %2s %3s' % (serial_out,MY_PREC,MY_CALL,MY_CHECK,MY_SECTION)
        #print exch_out
        #sys.exit(0)
            
#                              --------info sent------- -------info rcvd--------
#QSO: freq  mo date       time call       nr   p ck sec call       nr   p ck sec
#QSO: ***** ** yyyy-mm-dd nnnn ********** nnnn a nn aaa ********** nnnn a nn aaa
#QSO: 21042 CW 1997-11-01 2102 N5KO          3 B 74 STX K9ZO          2 A 69 IL
#0000000001111111111222222222233333333334444444444555555555566666666667777777777
#1234567890123456789012345678901234567890123456789012345678901234567890123456789

        #exch_in = '%3.3d %c %s %2d %3s' % (serial,prec,call2,check,sec)
        line='QSO: %5d CW %10s %4s %-10s %4d %1s %2s %-3s %-10s %4d %1s %2d %-3s' % \
            (freq_khz,date_off,time_off,MY_CALL,serial_out,MY_PREC,MY_CHECK,MY_SECTION,call,serial,prec,check,sec)

        # Check against history
        if call in keys:
            sec9=HIST[call]['sec']
            check9=HIST[call]['check']
            if sec!=sec9 or str(check)!=check9:
                print('\n$$$$$$$$$$ Difference from history $$$$$$$$$$$')
                print(rec)
                print(line)
                print(call,sec,check)
                print(HIST[call])
                #sys,exit(0)
                
        
        #print line
        #sys,exit(0)
        
        return line

    # Summary & final tally
    def summary(self):
        
        mults=0
        for i in range(len(ARRL_SECS)):
            print(i,'\t',ARRL_SECS[i],'\t',int( self.sec_cnt[i] ))
            if self.sec_cnt[i]>0:
                mults+=1

        print(' ')
        for i in range(len(ARRL_SECS)):
            if self.sec_cnt[i]==1:
                print('Only one: ',ARRL_SECS[i])

        print(' ')
        for i in range(len(ARRL_SECS)):
            if self.sec_cnt[i]==0:
                print('Missing: ',ARRL_SECS[i])

        print('\nnqsos=',self.nqsos2)
        print('mults=',mults)
        print('score=',2*self.nqsos2*mults)

    

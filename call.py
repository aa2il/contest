############################################################################################
#
# call.py - Rev 1.0
# Copyright (C) 2022 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for contacts with a specific call.
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
from fileio import write_adif_record

#######################################################################################
    
# Scoring class for Sat Comm - Inherits the base contest scoring class
class SPECIFIC_CALL(CONTEST_SCORING):
 
    def __init__(self,P,CALLS):
        CONTEST_SCORING.__init__(self,P,'Specific Call',mode='MIXED')

        # Init
        self.P=P
        self.CALLS=[call.upper() for call in CALLS]
        #print('CALLS=',CALLS)
        #print('CALLS=',self.CALLS)
        #sys.exit(0)

        # Determine contest time - this one is for all time!
        self.date0 = datetime.datetime.strptime( "20000101 0000" , "%Y%m%d %H%M")
        self.date1 = datetime.datetime.strptime( "21000101 0000" , "%Y%m%d %H%M")

        # Name of output file
        self.output_file = self.MY_CALL+'.LOG'
        
    # Contest-dependent header stuff
    def output_header(self,fp):
        pass
                    
    # Scoring routine for specific call
    # Really just spits out a list of QSOs 
    def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE,HIST2=None):
        #print('rec=',rec)
        #print('nqsos=',self.nqsos1)

        fmt = '%4s   %-10s %6s   %4s   %-10s   %-4s    %-10s'
        if self.nqsos1==1:
            hdr=fmt % ('','Call','Freq ','Mode','Date','Time','Contest')
            print('\n',hdr)

        # Pull out relavent entries
        call = rec["call"].upper()
        if call in self.CALLS:
            self.nqsos2 += 1;

            freq_khz = int( 1000*float(rec["freq"]) +0.5 )
            mode     = rec["mode"].upper()
            date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
            time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')
            if 'contest_id' in rec.keys():
                contest_id=rec['contest_id']
            else:
                contest_id=''
                
            line=fmt % ('QSO:',call,str(freq_khz),mode,date_off,time_off,contest_id)
            print(line)
            #print(rec)
            return line
            
    # Routine to check for dupes
    def check_dupes(self,rec,qsos,i,istart):

        # Count no. of raw qsos
        self.nqsos1+=1
        return (False,False)

    # Summary & final tally
    def summary(self):

        print('\ncalls =',self.CALLS)
        print('nqsos1=',self.nqsos1)
        print('nqsos2=',self.nqsos2)
        #print('band count =',self.sec_cnt)

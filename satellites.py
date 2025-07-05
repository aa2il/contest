############################################################################################
#
# satellites.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Routines for Satellite contacts - basically just spits out a list cof sat contacts.
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
class SATCOM(CONTEST_SCORING):
 
    def __init__(self,P):
        CONTEST_SCORING.__init__(self,P,'Satellites Worked',mode='MIXED')

        # Init
        self.P=P

        # Determine contest time - this one is for all time!
        self.date0 = datetime.datetime.strptime( "20000101 0000" , "%Y%m%d %H%M")
        self.date1 = datetime.datetime.strptime( "21000101 0000" , "%Y%m%d %H%M")

        # Make a separate ADIF file that we can use to make cert request
        MY_CALL = P.SETTINGS['MY_CALL']
        self.fp_adif = open("Satellites_"+MY_CALL.replace('/','_')+".adif","w")
        print("ADIF file name=", self.fp_adif) 

        #<ADIF_VER:5>2.2.7
        #<PROGRAMID:6>fldigi
        #<PROGRAMVERSION:6>4.1.19
        #<EOH>
        #WSJT-X ADIF Export<eoh>
        self.fp_adif.write('ADIF Export<eoh>\n')

        
    # Contest-dependent header stuff
    def output_header(self,fp):
        pass
                    
    # Scoring routine for satellites.
    # Really just spits out a list of QSOs 
    # Not quite same API as regular contests
    def satellites(self,fp,qsos):

        print('nqsos=',len(qsos))
        hdr='Date\t\tTime\t\tSatellite\tMode\tCall\t\tGrid'
        print('\n',hdr)
        fp.write(hdr+'\n')
        
        for rec in qsos:
            #keys = list(rec.keys())
            if 'sat_name' in rec:
                #print(rec)
                if 'qso_date_off' in rec:
                    d=rec['qso_date_off']
                    t=rec['time_off']
                else:
                    d=rec['qso_date']
                    t=rec['time_on']
                Date =datetime.datetime.strptime(d,'%Y%m%d').strftime('%b %d, %Y')
                if 'srx_string' in rec:
                    srx=rec['srx_string']
                else:
                    srx=''
                print(Date,'\t',t,'\t',rec['sat_name'],'  \t',rec['mode'],
                      ' \t',rec['call'],'   \t',srx)
                fp.write('%12s\t%6s\t\t%-8s\t%-3s\t%-10s\t%s\n' %
                         (Date,t,rec['sat_name'],rec['mode'],rec['call'],
                          srx))

                # Make a separate ADIF file that contains all sat contacts
                write_adif_record(self.fp_adif,rec,self.P,True)
                self.fp_adif.write('\n')
        
        self.fp_adif.close()
        sys.exit(0)



    # Summary & final tally
    def summary(self):

        pass

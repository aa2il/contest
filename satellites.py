############################################################################################
#
# satellites.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
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

#######################################################################################
    
# Scoring class for Sat Comm - Inherits the base contest scoring class
class SATCOM(CONTEST_SCORING):
 
    def __init__(self,contest):
        CONTEST_SCORING.__init__(self,contest)

        pass

    # Scoring routine for satellites.
    # Really just spits out a list of QSOs 
    # Not quite same API as regular contests
    def satellites(self,fp,qsos):

        print('nqsos=',len(qsos))
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
                print(Date,rec['sat_name'],t,rec['call'],
                      srx,rec['mode'])
                fp.write('%s\t%s\t%s\t%s\t%s\t%s\n' %
                         (Date,rec['sat_name'],t,rec['call'],
                          srx,rec['mode']))
        sys.exit(0)



    # Summary & final tally
    def summary(self):

        pass

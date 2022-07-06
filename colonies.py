############################################################################################
#
# cabrillo.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for 13 colonies special event each July.
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

############################################################################################

BONUS_STATIONS=['WM3PEN','GB13COL','TM13COL']

############################################################################################
    
# Scoring class for 13 Colonies - Inherits the base contest scoring class
class THIRTEEN_COLONIES(CONTEST_SCORING):
 
    def __init__(self,P):
        CONTEST_SCORING.__init__(self,P,'13 Colonies Special Event',mode='MIXED')

        # Init
        self.P=P

        # Determine contest time - assumes this is dones within a few days of the contest
        now = datetime.datetime.utcnow()
        start_time=13
        self.date0=datetime.datetime(now.year,7,1,start_time)
        self.date1 = self.date0 + datetime.timedelta(days=7)

        # Make a separate ADIF file that we can use to make cert request
        MY_CALL = P.SETTINGS['MY_CALL']
        self.fp_adif = open("13_Colonies_"+MY_CALL.replace('/','_')+".adif","w")
        print("ADIF file name=", self.fp_adif) 

        #<ADIF_VER:5>2.2.7
        #<PROGRAMID:6>fldigi
        #<PROGRAMVERSION:6>4.1.19
        #<EOH>
        #WSJT-X ADIF Export<eoh>
        self.fp_adif.write('ADIF Export<eoh>\n')

        # Name of output file
        self.output_file = self.MY_CALL+'_13COLONIES_'+str(self.date0.year)+'.LOG'

    # Contest-dependent header stuff
    def output_header(self,fp):
        return True
                    
    # Scoring routine for 13 Colonies Special Event
    # Really just spits out a list of QSOs for each SES
    # Not quite same API as regular contests
    #def qso_scoring(self,rec,dupe,qsos,HIST,MY_MODE):
    def cols13(self,fp,qsos):

        # Init - make list of SES stations
        nqsos13=0
        stations=BONUS_STATIONS.copy()
        for a in 'ABCDEFGHIJKLM':                       # Z some years also
            stations.append('K2'+a)
        print('Stations=',stations)

        n=len(stations)
        worked      = n*[False]
        worked_cw   = n*[False]
        worked_digi = n*[False]

        # For each SES, make a list of QSOs
        n=-1
        for station in stations:
            n+=1

            # Print headers
            if station=='WM3PEN':
                print('\nDate\t\tTime\t\tFreq\tRSTin\tMode\tRSTout' )
                fp.write('\n%s\t\t%s\t%7s\t\t%s\t%s\t%s\n' %
                         ('Date','Time','Freq','RSTin','Mode','RSTout' ) )
            print('\n',station)
            fp.write('\n%s\n' % station)

            for rec in qsos:
                call = rec["call"].upper()
                if call==station:
                    #print rec
                    if 'rst_rcvd' not in rec:
                        rec['rst_rcvd']=rec['rst_in']
                    if 'rst_sent' not in rec:
                        if 'rst_out' in rec:
                            rec['rst_sent']=rec['rst_out']
                        else:
                            rec['rst_sent']='599'
                    Date =datetime.datetime.strptime( rec['qso_date_off'] ,'%Y%m%d').strftime('%b %d, %Y')
                    frq  = int( 1e3*float(rec['freq']) +0.5)
                    mode = rec['mode']
                    print(Date,'\t',rec['time_off'],'\t',frq,'\t',rec['rst_rcvd'], \
                          '\t',mode,'\t',rec['rst_sent'])   
                    fp.write('%s\t%s\t%7s\t\t%s\t%s\t%s\n' %
                             (Date,rec['time_off'],frq,rec['rst_rcvd'],rec['mode'],rec['rst_sent'] ) )
                    nqsos13+=1

                    # Fix-up freq 
                    #frq  = int( 1e3*float(rec['freq']) +0.5)
                    #rec['freq'] = str( 1e-3*frq )
                    
                    # Keep track of worked status
                    worked[n]=True
                    if mode=='CW':
                        worked_cw[n]=True
                    elif mode=='FT8' or mode=='MFSK':
                        worked_digi[n]=True

                    # Make a separate ADIF file that we can use to make cert request
                    if mode=='CW':
                        write_adif_record(self.fp_adif,rec,self.P)
                        self.fp_adif.write('\n')
        
        self.fp_adif.close()
        print("\nThere were ",nqsos13," QSOs with the 13 Colonies.\n")
        #print(worked)
        #print(worked_cw)
        #print(worked_digi)

        clean_sweep      = True
        clean_sweep_cw   = True
        clean_sweep_digi = True
        #print(BONUS_STATIONS,len(BONUS_STATIONS))
        #print(stations,len(stations))
        for i in range(len(BONUS_STATIONS),len(stations)):
            print(i,stations[i],worked[i])
            clean_sweep      = clean_sweep      and worked[i]
            clean_sweep_cw   = clean_sweep_cw   and worked_cw[i]
            clean_sweep_digi = clean_sweep_digi and worked_digi[i]
            if False:
                print(i,stations[i])
                print(worked[i],worked_cw[i],worked_digi[i])
                print(clean_sweep,clean_sweep_cw,clean_sweep_digi)

        if clean_sweep:
            print('Clean sweep!')
            fp.write('Clean sweep!')
        if clean_sweep_cw:
            print('CW Clean sweep!')
            fp.write('CW Clean sweep!')
        if clean_sweep_digi:
            print('DIGI Clean sweep!')
            fp.write('DIGI Clean sweep!')
        print(' ')
        
        sys.exit(0)

    # Summary & final tally
    def summary(self):

        pass

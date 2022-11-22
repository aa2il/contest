############################################################################################
#
# cqww.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Routines for scoring CQ WW contests
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
from pprint import pprint
from utilities import reverse_cut_numbers

############################################################################################

#TRAP_ERRORS = False
TRAP_ERRORS = True

############################################################################################
    
# Scoring class for CQ WW - Inherits the base contest scoring class
class CQ_WW_SCORING(CONTEST_SCORING):
 
    def __init__(self,P,MODE):
        CONTEST_SCORING.__init__(self,P,'CQ-WW-'+MODE,MODE)
        print('CQ WW Scoring Init')

        self.BANDS = ['160m','80m','40m','20m','15m','10m']
        mults  = []
        states = []
        zones  = []
        dxccs  = []
        self.NQSOS = OrderedDict()
        for b in self.BANDS:
            mults.append((b,set([])))
            states.append((b,set([])))
            zones.append((b,set([])))
            dxccs.append((b,set([])))
            self.NQSOS[b]=0
        self.mults = OrderedDict(mults)
        self.states = OrderedDict(states)
        self.zones = OrderedDict(zones)
        self.dxccs = OrderedDict(dxccs)
        self.MY_CQ_ZONE = int( P.SETTINGS['MY_CQ_ZONE'] )

        # Point to proper scoring function
        if MODE=='CW':                   # or contest=='CQ-WW-SSB':

            # The CW Contest occurs on the last full weekend of Nov ?
            self.qso_scoring = self.qso_scoring_cw
            month=11
            ndays=21                                                   # 4th Sat
            
        elif MODE=='RTTY':
            
            # The CW Contest occurs on the last full weekend of Sept ?
            self.qso_scoring = self.qso_scoring_rtty
            month=9
            ndays=21                                                   # 4th Sat
            
        else:
            print('CQ WW SCORING - Unknown Contest MODE',MODE)
            sys.exit(0)

        # Determine start & end dates/times
        now = datetime.datetime.utcnow()
        year=now.year
        #year=2020               # Debug - Last time I participated

        day1=datetime.date(year,month,1).weekday()                     # Day of week of 1st of month - 0=Monday, 6=Sunday
        sat2=1 + ((5-day1) % 7) + ndays                                # Day no. for 4th Saturday = 1 since day1 is the 1st of the month
                                                                       #    no. days until 1st Saturday (day 5) + 7 more days 
        
        self.date0=datetime.datetime(year,month,sat2,0) 
        self.date1 = self.date0 + datetime.timedelta(hours=48)         # ... and ends at 0300/0400 UTC on Monday
        
        # Manual override
        if False:
            self.date0 = datetime.datetime.strptime( "20190928 0000" , "%Y%m%d %H%M")  # Start of contest
            self.date0 = datetime.datetime.strptime( "20201128 0000" , "%Y%m%d %H%M")  # Start of contest
            self.date1 = self.date0 + datetime.timedelta(hours=48)
            
        if False:
            print('now=',now)
            print('day1=',day1,'\tsat2=',sat2)
            print('date0=',self.date0)
            print('date1=',self.date1)
            sys.exit(0)

        # Name of output file
        self.output_file = self.MY_CALL+'_CQ-WW-'+MODE+'_'+str(self.date0.year)+'.LOG'
        
            
    # Contest-dependent header stuff
    def output_header(self,fp):
        fp.write('LOCATION: %s\n' % self.MY_STATE)
        fp.write('ARRL-SECTION: %s\n' % self.MY_SEC)
        fp.write('GRID-LOCATOR: %s\n' % self.MY_GRID)

    # Scoring routine for CQ WW CW & SSB - not sure why rtty is separate???
    def qso_scoring_cw(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):
        #print ' '
        #print rec

        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) + 0.0 )
        band = rec["band"]
        if 'qth' in rec :
            qth = rec["qth"]
        else:
            qth = ''

        dx_station = Station(call)
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        # Minor corrections
        if qth=='':
            qth=dx_station.cqz
        elif qth=='AK':
            qth=1
        try:
            zone=int(qth)
        except:
            print('\nProblem converting zone:',qth)
            print(rec)
            zone = int( dx_station.cqz )
            if TRAP_ERRORS:
                sys.exit(0)

        warning=False
        problem=False
        
        if not dupe:
            self.nqsos2 += 1;
            if dx_station.country=='United States':
                qso_points=0
            elif dx_station.continent=='NA':
                qso_points=2
            else:
                qso_points=3
            self.total_points += qso_points

            self.mults[band].add(str(zone))
            self.mults[band].add(dx_station.country)

        if MY_MODE=='CW':
            mode='CW'
            rst_out=599
            rst_in=599
        elif MY_MODE=='SSB':
            mode='PH'
            rst_in=59
        else:
            mode='??'

            
#QSO:  3799 PH 2000-10-26 0711 AA1ZZZ          59  05     K9QZO         59  04     0
        line='QSO: %5d %2s %10s %4s %-13s %3d %2.2d %-13s %3d %2.2d  0' % \
            (freq_khz,mode,date_off,time_off,self.MY_CALL,rst_out,int(self.MY_CQ_ZONE),call,rst_in,zone)

        if warning or problem:
            print(' ')
            print(rec)

            print(dx_station)
            pprint(vars(dx_station))
            
            print('Call =',call)
            print('Freq =',freq_khz)
            print('Band =',band)
            print('Zone =',zone,dx_station.cqz)
            print('State=',state)
            print('Date =',date_off)
            print('Time =',time_off)
            
            print(line)
            if problem:
                sys,exit(0)

        return line
                        
    # Scoring routine for CQ WW RTTY
    def qso_scoring_rtty(self,rec,dupe,qsos,HIST,MY_MODE,HIST2):
        #print ' '
        #print rec

        # Pull out relavent entries
        call = rec["call"]
        freq_khz = int( 1000*float(rec["freq"]) + 0.0 )
        band = rec["band"]
        if 'name' in rec :
            name = rec["name"]
        else:
            name = ''
        if 'qth' in rec :
            qth = rec["qth"]
        else:
            qth = ''
        if 'cqz' in rec :
            cqz = rec["cqz"]
        else:
            cqz = ''
        if 'country' in rec :
            country = rec["country"]
        else:
            country = ''
        #if 'state' in rec :
        #    state = rec["state"]
        #else:
        #    state = ''
        if 'rst_rcvd' in rec :
            rst_in = reverse_cut_numbers( rec['rst_rcvd'] )
        else:
            rst_in = '599'
            
        # There was some inconsitencies in where things were stored
        if cqz.isdigit() and False:
            # The CQZ field is hosed !!!!!!!!!!!!
            zone  = int(cqz)
            if country in ['USA','Canada']:
                if name.isdigit():
                    state = qth.upper()
                else:
                    state = name.upper()
            else:
                state=''
        elif qth.isdigit() and not name.isdigit():
            zone  = int(qth)
            state = name.upper()
        elif not qth.isdigit() and name.isdigit():
            zone  = int(name)
            state = qth.upper()
        elif qth.isdigit() and name.isdigit():
            zone  = int(qth)
            zone2  = int(name)
            state = ''
            if zone!=zone2 or (zone>=3 and zone<=5):
                print('*** ERROR *** Cant resolve zone and state XX')
                problem=True
        else:
            print('*** ERROR *** Cant resolve zone and state')
            print('call=',call)
            print('name=',name)
            print('qth=',qth)
            print('cqz=',cqz)
            print('country=',country)
            print('rec=',rec)
            problem=True

        if rst_in!='599':
            print('*** ERROR *** Problem with RST IN ***')
            print('call=',call)
            print('rst=',rst_in)
            problem=True


        dx_station = Station(call)
        date_off = datetime.datetime.strptime( rec["qso_date_off"] , "%Y%m%d").strftime('%Y-%m-%d')
        time_off = datetime.datetime.strptime( rec["time_off"] , '%H%M%S').strftime('%H%M')

        # Minor corrections
        if state=='' or zone==31:
            state='DX'

        warning=False
        problem=False
        
        if ((state in STATES) and zone!=CQ_ZONES[state] ) or \
           ( not (state in STATES) and zone!=dx_station.cqz):
            print('*** Zone Mismatch ***')
            print('call=',call)
            print('zone=',zone)
            print('state=',state)
            warning=True;
            self.warnings += 1
            if TRAP_ERRORS:
                sys.exit(0)
            
        if zone>=3 and zone<=5 and not (state in CQ_STATES):
            # This is not quite right for some parts of Canada but go with it for now
            print('\n*** Expected US/Canada  ***')
            print('zone=',zone)
            print('state=',state)
            problem=True;
        elif (zone<3 or zone>5) and state!='DX':
            # This is not quite right for some parts of Canada but go with it for now
            print('\n*** Expected DX ***')
            problem=True;

        if not dupe:
            self.nqsos2 += 1;
            self.NQSOS[band]+=1
            if dx_station.country=='United States':
                qso_points=1
            elif dx_station.continent=='NA':
                qso_points=2
            else:
                qso_points=3
            self.total_points += qso_points

            self.mults[band].add(str(zone))
            self.mults[band].add(dx_station.country)
            if state!='DX':
                self.mults[band].add(state)
                   
            self.zones[band].add(str(zone))
            #print(self.zones)
            if dx_station.country in ['United States','Canada']:
                self.states[band].add(state)
            self.dxccs[band].add(dx_station.country)
            
            # Info for multi-qsos
            exch_in=rst_in+' '+str(zone)+' '+state
            if call in self.EXCHANGES.keys():
                self.EXCHANGES[call].append(exch_in)
            else:
                self.EXCHANGES[call]=[exch_in]
                        
#QSO: 14073 RY 2008-09-27 0005 HC8N 599 10 DX WC2C   599 05 NY 
        line='QSO: %5d RY %10s %4s %-13s 599 %2.2d %-2s %-13s 599 %2.2d %-3s  0' % \
            (freq_khz,date_off,time_off,self.MY_CALL,int(self.MY_CQ_ZONE),self.MY_STATE,call,zone,state)

        if warning or problem:
            print(' ')
            print(rec)

            print(dx_station)
            pprint(vars(dx_station))
            
            print('Call =',call)
            print('Freq =',freq_khz)
            print('Band =',band)
            print('Zone =',zone,dx_station.cqz)
            print('State=',state)
            print('Date =',date_off)
            print('Time =',time_off)
            
            print(line)
            if problem and TRAP_ERRORS:
                sys,exit(0)

        return line
                        
    # Summary & final tally
    def summary(self):

        print(self.states)
        print(self.zones)

        print('nqsos2=',self.nqsos2)
        print('num warnings=',self.warnings)

        #print('MULTS:',self.mults)
        mults=0
        nstates=0
        nzones=0
        ndxccs=0
        nqsos3=0
        for b in self.BANDS:
            print('\n',b,'# QSOs=',self.NQSOS[b])
            nqsos3+=self.NQSOS[b]
            
            m = list( self.mults[b] )
            m.sort()
            print(b,' Mults:',m,len(m))
            mults+=len(m)

            s = list( self.states[b] )
            s.sort()
            print(b,' States:',s,len(s))
            nstates+=len(s)
            
            d = list( self.dxccs[b] )
            d.sort()
            print(b,' DXCCs :',d,len(d))
            ndxccs+=len(d)

            z = list( self.zones[b] )
            z.sort()
            print(b,' Zones :',z,len(z))
            nzones+=len(z)
            
        print('\nnqsos         =',self.nqsos2,nqsos3)
        print('qso points    =',self.total_points)
        print('# states      =',nstates)
        print('# dxccs       =',ndxccs)
        print('# zones       =',nzones)
        print('# mults       =',mults)
        print('Claimed score =',self.total_points*mults)
    

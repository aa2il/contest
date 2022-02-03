#! /usr/bin/python3
############################################################################################
#
# cabrillo.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Program to convert contest log to cabrillo format and compute claimed score.
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# NOTE:
#     Most up-to-date contest module is the RTTY CONTEST.
#     Use it as model for subsequent contests
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
import os
import datetime
import argparse
import numpy as np
from load_history import *
from fileio import *

from scoring import *
from fd import *
from arrl_ss import *
from vhf import *
from cwops import *
from cwopen import *
from sst import *
from naqp import *
from wpx import *
from iaru import *
from cqp import *
from wwdigi import *
from mak import *
from rttyru import *
from cqww import *
from colonies import *
from satellites import *
from settings import *

#######################################################################################

# User params
DIR_NAME = '~/.fldigi/logs/'

#######################################################################################

# Process command line args
arg_proc = argparse.ArgumentParser()
arg_proc.add_argument('-mak', action='store_true',help='Makrothen RTTY')
arg_proc.add_argument('-cwss', action='store_true',help='ARRL CW Sweepstakes')
arg_proc.add_argument('-wwcw', action='store_true',help='CQ WW CW')
arg_proc.add_argument('-wwrtty', action='store_true',help='CQ WW RTTY')
arg_proc.add_argument('-rttyru', action='store_true',help='ARRL RTTY Round Up')
arg_proc.add_argument('-ft8ru', action='store_true',help='FT8 Round Up')
arg_proc.add_argument('-ten', action='store_true',help='ARRL 10 Meter')
arg_proc.add_argument('-vhf', action='store_true',help='ARRL VHF')
arg_proc.add_argument('-fd', action='store_true',help='ARRL Field Day')
arg_proc.add_argument('-wwdigi', action='store_true',help='World Wide Digi DX')
arg_proc.add_argument('-cwops', action='store_true',help='CW Ops Mini-Test')
arg_proc.add_argument('-cwopen', action='store_true',help='CW Ops CW Open')
arg_proc.add_argument('-sst', action='store_true',help='Slow Speed Mini-Test')
arg_proc.add_argument('-cols13', action='store_true',help='13 Colonies Special Event')
arg_proc.add_argument('-sats', action='store_true',help='Satellites Worked')
arg_proc.add_argument('-naqpcw', action='store_true',help='NAQP CW')
arg_proc.add_argument('-naqprtty', action='store_true',help='NAQP RTTY')
arg_proc.add_argument('-wpx', action='store_true',help='CQ WPX')
arg_proc.add_argument('-iaru', action='store_true',help='IARU HF')
arg_proc.add_argument('-cqp', action='store_true',help='Cal QSO Party')
arg_proc.add_argument("-i", help="Input ADIF file",
                              type=str,default=None)
arg_proc.add_argument("-o", help="Output Cabrillo file",
                              type=str,default='AA2IL.txt')
arg_proc.add_argument("-hist", help="History File",
                              type=str,default='')
args = arg_proc.parse_args()
fname = args.i
output_file = args.o
fnames=''

history = ''
sc=None

category_band='ALL'

P=CONFIG_PARAMS('.keyerrc')
HIST2=None

#######################################################################################

# Contest-specific stuff
if args.mak:
    contest='MAKROTHEN-RTTY'
    MY_MODE='RTTY'
    date0 = datetime.datetime.strptime( "20191012" , "%Y%m%d")  # Start of contest
    date1 = date0 + datetime.timedelta(hours=48)
    fname = 'mak_rtty_2019.adif'

elif args.rttyru:
    sc = ARRL_RTTY_RU_SCORING(P,'ARRL-RTTY')
    contest=sc.contest
    MY_MODE='MIXED'          # sc.my_mode
    date0=sc.date0
    date1=sc.date1
    history = sc.history
    
    #fname1='aa2il_2019.adif'
    fname1='aa2il_2022.adif'
    fnames = [DIR_NAME+'/'+fname1]

    DIR_NAME = '~/.local/share/WSJT-X - CONTEST'
    #fname2 = '2019_rtty_ru.adi'
    fname2 = 'wsjtx_log.adi'
    fnames.append( DIR_NAME+'/'+fname2 )
    output_file = sc.output_file

elif args.ft8ru:
    sc = ARRL_RTTY_RU_SCORING(P,'FT8-RU')
    contest=sc.contest
    MY_MODE=sc.my_mode
    date0=sc.date0
    date1=sc.date1
    
    fname = 'wsjtx_log.adi'
    DIR_NAME = '~/.local/share/WSJT-X - CONTEST'
    output_file = sc.output_file
    
elif args.ten:
    contest='ARRL 10'
    MY_MODE='CW'
    date0 = datetime.datetime.strptime( "20201212 0000" , "%Y%m%d %H%M")  # Start of contest
    date1 = date0 + datetime.timedelta(hours=48)
    DIR_NAME = '../pyKeyer'
    fname = 'AA2IL.adif'
    output_file = 'AA2IL_10m_2020.LOG'
    
elif args.vhf:
    sc = ARRL_VHF_SCORING(P)
    contest=sc.contest
    MY_MODE=sc.my_mode
    category_band=sc.category_band
    date0=sc.date0
    date1=sc.date1
    history = sc.history
    output_file = sc.output_file

    # Need to merge FT8 and CW/Phone logs
    fnames=[]
    #DIR_NAME='.'
    for fname in ['AA2IL.adif','wsjtx_log.adi']:
    #for fname in ['AA2IL_VHF_Sep2021.adif','wsjtx_VHF_Sep2021.adi']:
        f=os.path.expanduser( DIR_NAME+'/'+fname )
        fnames.append(f)

elif args.fd:
    contest='ARRL-FD'
    MY_MODE='MIXED'
    date0 = datetime.datetime.strptime( "20200627 1800" , "%Y%m%d %H%M")  # Start of contest
    date1 = date0 + datetime.timedelta(hours=27)
    history = '../history/data/master.csv'
    output_file = 'AA2IL_FD_2020.LOG'

    # Need to merge FT8 and CW logs
    fnames=[]
    #DIR_NAME = '~/logs/field_day_2020/'
    DIR_NAME = '~/AA2IL/Contesting/Field_Day/field_day_2020/'
    fnames=[]
    for fname in ['AA2IL.adif','ft8_contest.adi','pi2_ft8_contest.adi']:
    #for fname in ['ft8_contest.adi']:
    #for fname in ['pi2_ft8_contest.adi']:
        f=os.path.expanduser( DIR_NAME+'/'+fname )
        fnames.append(f)
    
elif args.wwdigi:
    sc = WWDIGI_SCORING(P)
    contest=sc.contest
    MY_MODE=sc.my_mode
    date0=sc.date0
    date1=sc.date1
    
    #print(contest)
    #print(MY_MODE)
    #print(date0)
    #sys.exit(0)
    
    contest='WW-DIGI'
    MY_MODE='DIGI'
    
    if True:
        # Manual override
        date0 = datetime.datetime.strptime( "20190831 1200" , "%Y%m%d %H%M")  # Start of contest
        date1 = date0 + datetime.timedelta(hours=24)

    fname = '2019_rtty_ru.adi'
    DIR_NAME = '~/.local/share/WSJT-X - CONTEST'
    output_file = 'AA2IL.LOG'

elif args.cwss:
    sc = ARRL_SS_SCORING(P)
    contest=sc.contest
    MY_MODE=sc.my_mode
    date0=sc.date0
    date1=sc.date1
    
    fname = 'AA2IL.adif'
    DIR_NAME = '../pyKeyer/'
    #history = '../history/data/SSCW.txt'
    history = '../history/data/SSCW-2021-LAST-2.txt'
    output_file = 'AA2IL_CWSS_2021.LOG'

elif args.naqprtty:
    contest='NAQP-RTTY'
    MY_MODE='RTTY'
    date0 = datetime.datetime.strptime( "20180224 1800" , "%Y%m%d %H%M")  # Start of contest
    date1 = datetime.datetime.strptime( "20180225 0600" , "%Y%m%d %H%M")  # End of contest
    date0 = datetime.datetime.strptime( "20180721 1800" , "%Y%m%d %H%M")  # Start of contest
    date1 = datetime.datetime.strptime( "20180722 0600" , "%Y%m%d %H%M")  # End of contest
    history = '../data/NAQP_CallHistory_AOCC072717.txt'

    date0 = datetime.datetime.strptime( "20190223 1800" , "%Y%m%d %H%M")  # Start of contest
    date1 = date0 + datetime.timedelta(hours=12)
    history = '../history/data/master.csv'
    fname = 'naqp.adif'
    DIR_NAME = '~/.fllog/'
    
elif args.naqpcw:
    sc = NAQP_SCORING(P,'CW')
    contest=sc.contest
    MY_MODE=sc.my_mode
    date0=sc.date0
    date1=sc.date1

    print(contest)
    print(MY_MODE)
    print(date0)
    #sys.exit(0)
    
    if False:
        # Manual override
        date0 = datetime.datetime.strptime( "20190112 1800" , "%Y%m%d %H%M")  # Start of contest
        date1 = date0 + datetime.timedelta(hours=12)

    fname = 'AA2IL.adif'
    DIR_NAME = '../pyKeyer/'
    history = '../history/data/master.csv'

    """
    #history = '../data/NAQPCW.txt'
    #history = '../data/NAQP_CallHistory_AOCC072717.txt'
    history = 'data/NAQP_Call_History_Aug2018.txt'
    history = '../history/data/master.csv'
    #DIR_NAME = './'
    #fname = 'AA2IL.LOG'
    DIR_NAME = '../pyKeyer/'
    fname = 'AA2IL.adif'
    DIR_NAME = '../../logs/'
    fname = 'aa2il_2019.adif'
    """

elif args.wwcw:
    contest='CQ-WW-CW'
    MY_MODE='CW'
    date0 = datetime.datetime.strptime( "20201128 0000" , "%Y%m%d %H%M")  # Start of contest
    date1 = date0 + datetime.timedelta(hours=48)

    history = '../history/data/master.csv'
    fname = 'AA2IL.adif'
    DIR_NAME = '../pyKeyer/'
    
elif args.wwrtty:
    contest='CQ-WW-RTTY'
    MY_MODE='RTTY'
    date0 = datetime.datetime.strptime( "20190928 0000" , "%Y%m%d %H%M")  # Start of contest
    date1 = date0 + datetime.timedelta(hours=48)
    fname = 'cqww_rtty_2019.adif'

elif args.wpx:
    MODE='CW'
    MODE='RTTY'
    sc = CQ_WPX_SCORING(P,MODE)
    contest=sc.contest
    MY_MODE=sc.my_mode
    category_band=sc.category_band
    date0=sc.date0
    date1=sc.date1
    history = sc.history
    output_file = sc.output_file

    if MY_MODE=='CW':
        DIR_NAME = '../pyKeyer/'
        fname = 'AA2IL.adif'
    else:
        DIR_NAME = '../../logs/fllog/'
        fname = 'cq_wpx_rtty_2019.adif'
        fname = 'cq_wpx_rtty_2022.adif'

elif args.iaru:
    sc = IARU_HF_SCORING(P)
    contest=sc.contest
    MY_MODE=sc.my_mode
    date0=sc.date0
    date1=sc.date1
    
    if False:
        # Manual override
        date0 = datetime.datetime.strptime( "20210710 1200" , "%Y%m%d %H%M")  # Start of contest
        date1 = date0 + datetime.timedelta(hours=24)
        
    fname = 'AA2IL.adif'
    DIR_NAME = '../pyKeyer/'
    history = '../history/data/master.csv'

elif args.cqp:
    print('P=',P)
    sc = CQP_SCORING(P)
    contest=sc.contest
    MY_MODE=sc.my_mode
    date0=sc.date0
    date1=sc.date1
    history = sc.history

    HIST2=sc.read_hist2(args.hist)
    
    fname = 'AA2IL_6.adif'
    DIR_NAME = '../pyKeyer'
    fnames = [DIR_NAME+'/'+fname]
    #fname = 'AA2IL.adif'                   # In 2020, used both calls
    #fnames.append( DIR_NAME+'/'+fname )
    output_file = 'AA2IL_CQP_2021.LOG'
    
elif args.sst:
    sc = SST_SCORING(P)
    contest=sc.contest
    MY_MODE=sc.my_mode
    date0=sc.date0
    date1=sc.date1

    if False:
        # Manual override
        date0 = datetime.datetime.strptime( "20210301 0000" , "%Y%m%d %H%M")  # Start of contest - 5PM local
        date1 = date0 + datetime.timedelta(hours=1+1./60.)
        
    history = '../history/data/master.csv'
    fname = 'AA2IL.adif'
    DIR_NAME = '../pyKeyer/'

elif args.cwops:
    sc = CWOPS_SCORING(P)
    contest=sc.contest
    MY_MODE=sc.my_mode
    date0=sc.date0
    date1=sc.date1

    if False:
        # Manual override
        date0 = datetime.datetime.strptime( "20210804 1900" , "%Y%m%d %H%M")  # Start of contest - noon/11AM local
        #date0 = datetime.datetime.strptime( "20210429 0300" , "%Y%m%d %H%M")  # Start of contest - 7PM/8PM local
        date1 = date0 + datetime.timedelta(hours=1+30/3600.)
        
    history = '../history/data/master.csv'
    fname = 'AA2IL.adif'
    DIR_NAME = '../pyKeyer/'

elif args.cwopen:
    sc = CWOPEN_SCORING(P)
    contest=sc.contest
    MY_MODE=sc.my_mode
    category_band=sc.category_band
    date0=sc.date0
    date1=sc.date1
    history = sc.history

    fname = 'AA2IL.adif'
    DIR_NAME = '../pyKeyer/'

elif args.cols13:
    sc=THIRTEEN_COLONIES(P)
    contest=sc.contest
    MY_MODE=sc.my_mode
    date0=sc.date0
    date1=sc.date1
    history = ''

    if False:
        # Manual override
        date0 = datetime.datetime.strptime( "20210701 1300" , "%Y%m%d %H%M")  # Start of contest
        date1 = datetime.datetime.strptime( "20210708 0400" , "%Y%m%d %H%M")  # Start of contest

    # Need to merge FT8/FT4 and CW/Phone logs
    if not fname:
        fname = 'AA2IL.adif'
        DIR_NAME = '../pyKeyer'
        fnames = [DIR_NAME+'/'+fname]
        fname = 'wsjtx_log.adi'
        DIR_NAME = '~/.local/share/WSJT-X'
        fnames.append( DIR_NAME+'/'+fname )
    else:
        fnames=[fname]

elif args.sats:
    sc = SATCOM(P)
    contest=sc.contest
    MY_MODE=sc.my_mode
    category_band=sc.category_band
    date0=sc.date0
    date1=sc.date1
    history = ''
    
    fname = 'AA2IL.adif'
    DIR_NAME = '../pyKeyer'
    fnames = [DIR_NAME+'/'+fname]
    fname = 'vhf.adif'
    DIR_NAME = '~/logs'
    fnames.append( DIR_NAME+'/'+fname )

else:
    print('Need to specify a single contest')
    sys.exit(0)

#print(fnames)
#print(type(fnames))
if type(fnames) == list:   
    input_files  = fnames
else:
    input_files  = [DIR_NAME + '/' + fname]
#sys.exit(0)

################################################################################

# Function to open output Cabrillo file and write out header
def open_output_file(P,outfile):
    fp = open(outfile, 'w')

    contest = P.contest_name
    #MY_SECTION = P.SETTINGS['MY_SEC']
    #MY_STATE = P.SETTINGS['MY_STATE']
    MY_CALL = P.SETTINGS['MY_CALL']
    MY_POWER='LOW'
    
    fp.write('START-OF-LOG:3.0\n')
    fp.write('CONTEST: %s\n' % contest)

    try:
        skip_header=sc.output_header(fp)
        if skip_header:
            return fp
    except Exception as e: 
        # Need to add a routine to each contest - copy from sst.py, etc.
        print( str(e) )
        print('OPEN_OUTPUT_FILE - Needs some easy work!  See CABRILLO.PY for how to dow this')
        sys.exit(0)

    """
    if contest=='IARU-HF' or \
       contest=='WW-DIGI' or contest=='ARRL-FD' :
        fp.write('LOCATION: %s\n' % MY_SECTION)
        fp.write('ARRL-SECTION: %s\n' % MY_SECTION)
    elif contest=='MAKROTHEN-RTTY' or contest=='ARRL-RTTY' or contest=='NAQP-CW' or \
         contest=='NAQP-RTTY' or contest=='FT8-RU' or \
    contest=='CQ-WW-RTTY' or contest=='CQ-WW-CW' or\
         contest=='ARRL 10':
        fp.write('LOCATION: %s\n' % MY_STATE)
    elif contest=='13 Colonies Special Event' or \
         contest=='Satellites Worked':
        return fp
    else:
        print('OPEN_OUTPUT_FILE: Unknown contest -',contest)
        sys.exit(0)
    """

    fp.write('CALLSIGN: %s\n' % MY_CALL)
    fp.write('CATEGORY-OPERATOR: SINGLE-OP\n');
    fp.write('CATEGORY-TRANSMITTER: ONE\n');
    fp.write('CATEGORY-POWER: %s\n' % MY_POWER);
    
    if contest=='FT8-RU' or contest=='ARRL-RTTY':
        fp.write('CATEGORY-ASSISTED: ASSISTED\n');
    else:
        fp.write('CATEGORY-ASSISTED: NON-ASSISTED\n');
    
    fp.write('CATEGORY-BAND: %s\n' % category_band);
    fp.write('CATEGORY-STATION: FIXED\n');

    #if contest!='WW-DIGI':
    if contest!='FT8-RU':
        fp.write('CATEGORY-MODE: %s\n' % MY_MODE);
    
    #fp.write('CLAIMED-SCORE: \n',);
    fp.write('OPERATORS: %s\n' % MY_CALL);
    fp.write('CLUB: \n',);
    fp.write('NAME: Joseph B. Attili\n');
    fp.write('ADDRESS: PO Box 2036\n');
    fp.write('ADDRESS: Ramona, CA 92065\n');
    fp.write('ADDRESS-CITY: Ramona\n');
    fp.write('ADDRESS-STATE-PROVINCE: CA\n');
    fp.write('ADDRESS-POSTALCODE: 92065\n');
    fp.write('ADDRESS-COUNTRY: USA\n');
    fp.write('EMAIL: aa2il@arrl.net\n');
    fp.write('SOAPBOX:\n');
    fp.write('SOAPBOX:\n');
    fp.write('SOAPBOX:\n');
    
    return fp




# Function to compute time duration of a qso
# Useful for fixing logs where time_on wasn't set to time_off
def qso_time(rec):
    if 'qso_date' in rec :
        date_on = rec["qso_date"]
    if 'qso_date_off' in rec :
        date_off = rec["qso_date_off"]
    if 'time_on' in rec :
        ton = rec["time_on"]
#        print "time on  = ",ton
    if 'time_off' in rec :
        toff = rec["time_off"]
#        print "time off = ",toff

    dt = 24.*3600.*( int(date_off) - int(date_on) ) + \
         3600.*( int(toff[0:2]) - int(ton[0:2]) ) + \
         60.*(int(toff[2:4]) - int(ton[2:4])) + \
         1.*( int(toff[4:6]) - int(ton[4:6]) )
    return dt


#######################################################################################

# Start of main
print('\n****************************************************************************')
print('\nCabrillo converter beginning for',contest)
print('Start Date=',date0)
print('Stop Date =',date1)
print('\nInput file(s):',input_files)
print('OUTPUT FILE=',output_file)

P.contest_name=contest

# Init
istart  = -1
cum_gap = 0
if contest=='ARRL-FD':
    sc = ARRL_FD_SCORING(contest)
#elif contest=='CW Ops Mini-Test':
    # This is all done above now - model for rest of code eventually
    #    sc = CWOPS_SCORING(contest)
elif contest=='MAKROTHEN-RTTY':
    sc = MAKROTHEN_SCORING(contest)
elif contest=='CQ-WW-RTTY' or contest=='CQ-WW-CW':
    sc = CQ_WW_SCORING(contest)
elif contest=='ARRL 10': \
    sc = ARRL_RTTY_RU_SCORING(contest)
elif not sc:
    #sc = contest_scoring(contest)
    print('\nUnrecognized contest - aborting -',contest,'\n')
    sys.exit(0)

# Read adif input file(s)
qsos2=[]
for f in input_files:
    fname=os.path.expanduser( f )
    print('\nInput file:',fname)
    
    p,n,ext=parse_file_name(fname)
    print('fname=',fname)
    print('p=',p)
    print('n=',n)
    print('e=',ext)

    if ext=='.LOG':
        qsos1 = parse_simple_log(fname,args)
    else:
        qsos1 = parse_adif(fname)
    #print qsos1
    #qsos.append(qsos1)
    qsos2 = qsos2 + qsos1
    #print qsos2
    
    #print(qsos1[0])
    #print(qsos1[-1])
    print("There are ",len(qsos1),len(qsos2)," QSOs")

#sys.exit(0)
    
# Ignore entries outside contest window &
# Sort list of QSOs by date/time - needed if we merge multiple logs (e.g. for ARRL RTTY w/ FT8
qsos=[]
nqsos=0
first_time=True
for rec in qsos2:
    nqsos+=1
    keys = list(rec.keys())
    if len(keys)==0:
        print('Skipping blank record')
        print('\n',nqsos,rec)
        continue
    
    if 'qso_date_off' in keys:
        date_off = datetime.datetime.strptime( rec['qso_date_off']+" " + rec["time_off"] , "%Y%m%d %H%M%S")
    elif 'qso_date' in keys:
        date_off = datetime.datetime.strptime( rec['qso_date']+" " + rec["time_on"] , "%Y%m%d %H%M%S")
    else:
        print('\nHmmmmmmmmmm - cant figure out date!')
        print(rec)
        print(keys)
        sys.exit(0)
        
    if date_off>=date0 and date_off<=date1:
        rec["time_stamp"]=date_off
        qsos.append(rec)
    elif date_off>date1:
        if first_time:
            print('\n***********************************************************************')
            print('************ WARNING *** Extra QSO(s) found after contest end *********')
            print('***********************************************************************\n')
            first_time=False
        
qsos.sort(key=lambda x: x['time_stamp'])

# Other qso fix-ups to make things easier later on
if contest=='NAQP-CW' or contest=='NAQP-RTTY':
    for rec in qsos:
        if 'qth' not in rec:
            rec["qth"]  = rec["srx_string"].upper()

# Open output file
fp=open_output_file(P,output_file)

# Load history file
print('History file:',history,'\n')
HIST = load_history(history)

# Loop over all qsos
j=-1
lines=[]
for i in range(len(qsos)):
    rec=qsos[i]
    #print('\n',i,rec)
    #date_off = datetime.datetime.strptime( rec["qso_date_off"]+" "+rec["time_off"] , "%Y%m%d %H%M%S")
    date_off = rec['time_stamp']

    # Ignore entries outside contest window - this is now done above so can eventually clean this up
    if date_off>=date0 and date_off<=date1:
        #print i,rec

        if False:
            print(rec)
            print(date0,' - ',date1,' ... ',date_off)
            sys.exit(0)
        
        if istart<0:
            istart=i

        # Compute qso rate
        if j<0:

            # First QSO - init rate calcs
            j=i
            date_off2 = date_off
            mins = 10
            rate_window = datetime.timedelta(minutes=mins)

            # Actual start time
            gap_min0 = (date_off - date0).total_seconds() / 60.0
            cum_gap = gap_min0
            print('Start time gap:',gap_min0,'minutes')
            if False:
                print('Date off=',date_off)
                print('Date 0  =',date0)
                sys.exit(0)
            
        else:
            while date_off2<date_off - rate_window:
                j += 1
                date_off2 = qsos[j]['time_stamp']
            qrate = (i-j+1) / (mins/60.)
            df = float(rec['freq']) - float(qsos[i-1]['freq'])
            print('rate = ',qrate,' per hour\t\t',rec['mode'],rec['band'],df==0)
            if j==i:
                gap_min = (date_off - qsos[i-1]['time_stamp']).total_seconds() / 60.0
                print('Time gap:',gap_min,'minutes')
                if gap_min>30:
                    cum_gap += gap_min

        dupe,rapid = sc.check_dupes(rec,qsos,i,istart)
        if rapid and (contest!='FT8-RU' or False):
            print('<<<<<<<<<<< RAPID dupe skipped >>>>>>>>>>>>>>\n')
            sc.nskipped+=1
            continue

        if contest=='13 Colonies Special Event':
            # This one has a different API - leaving it like this for now
            # but would be nice to be consistent!
            sc.cols13(fp,qsos)
            sys.exit(0)

        elif contest=='Satellites Worked':
            # This one also has a different API - leaving it like this for now
            # but would be nice to be consistent!
            sc.satellites(fp,qsos)
            sys.exit(0)

        else:
            # This is how things should be for all contests
            # Added arg HIST2 for CQP
            line = sc.qso_scoring(rec,dupe,qsos,HIST,MY_MODE,HIST2)
            
        #print(line)
        dupe=False
        for L in lines:
            if L==line:
                print('@@@@@@@@@@@@@@@@@@@@@@@@ Duplicate line found\n',line)
                dupe=True
        if not dupe:
            lines.append(line)
            fp.write('%s\n' % line)

fp.write('END-OF-LOG:\n')
fp.close()

print(" ")
if contest=='WW-DIGI':
    avg_dx_km = sc.total_km / sc.nqsos2
    print('\nLongest DX:',sc.max_km,'km')
    print(sc.longest)
    print('\nAverage DX:',avg_dx_km,'km')
    
    #print 'GRID FIELDS:',sc.grid_fields
    mults=0
    for b in sc.BANDS:
        fields = list( sc.grid_fields[b] )
        fields.sort()
        print(b,'Grid Fields:',fields)
        mults+=len(fields)

    print('\nnqsos         =',sc.nqsos2)
    print('qso points    =',sc.total_points)
    print('mults         =',mults)
    print('Claimed score =',sc.total_points*mults)

    print('\n&&&&&&&&&&&&&&&& Need to update code &&&&&&&&&&&&&&&&&&&&&&&&&&&')
    
else:
    sc.check_multis(qsos)
    sc.summary()
    
print(" ")

# Actual stop time & average qso rate
print('Start time gap:\t\t%8.1f minutes\t=%8.1f hours' % (gap_min0,gap_min0/60.) )
gap_min = (date1 - date_off).total_seconds() / 60.0
cum_gap += gap_min
print('Stop time gap:\t\t%8.1f minutes' % gap_min)
print('Total time off:\t\t%8.1f minutes\t=%8.1f hours' % (cum_gap, cum_gap/60.) )
duration = (date1 - date0).total_seconds() / 60.0
print('Contest duration:\t%8.1f minutes \t=%8.1f hours' %(duration,duration/60.) )
op_time=duration-cum_gap
print('Operating time:\t\t%8.1f minutes \t=%8.1f hours' % (op_time,op_time/60.) )
ave_rate = sc.nqsos2/(op_time/60.)
print('Average rate:\t\t%8.1f per hour\n' % ave_rate)
        

# Not quite sure how to use these yet
#my_lookuplib = LookupLib(lookuptype="countryfile")
#cic = Callinfo(my_lookuplib)
#print cic.get_all("AA2IL")

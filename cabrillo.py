#! /usr/bin/python3
############################################################################################
#
# cabrillo.py - Rev 1.0
# Copyright (C) 2021-3 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Program to convert contest log to cabrillo format and compute claimed score.
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
import matplotlib.pyplot as plt

from load_history import load_history
from fileio import *
from params import *

#######################################################################################

# Function to open output Cabrillo file and write out header
def open_output_file(P,outfile):
    fp = open(outfile, 'w')

    contest = P.contest_name
    MY_CALL = P.SETTINGS['MY_CALL']
    MY_POWER='LOW'
    MY_CLUB = P.SETTINGS['MY_CLUB']
    
    fp.write('START-OF-LOG:3.0\n')
    fp.write('CONTEST: %s\n' % contest)

    try:
        skip_header=P.sc.output_header(fp)
        if skip_header:
            return fp
    except Exception as e: 
        # Need to add a routine to each contest - copy from sst.py, etc.
        print( str(e) )
        print('OPEN_OUTPUT_FILE - Needs some easy work!  See CABRILLO.PY for how to dow this')
        sys.exit(0)

    """
    elif contest=='MAKROTHEN-RTTY' or contest=='ARRL-RTTY' or \
         contest=='NAQP-RTTY' or contest=='FT8-RU' or \
         contest=='CQ-WW-CW' or\
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
    
    if P.ASSISTED or contest in ['FT8-RU','ARRL-RTTY']:
        fp.write('CATEGORY-ASSISTED: ASSISTED\n');
    else:
        fp.write('CATEGORY-ASSISTED: NON-ASSISTED\n');
    
    fp.write('CATEGORY-BAND: %s\n' % P.category_band);
    fp.write('CATEGORY-STATION: FIXED\n');

    #if contest!='WW-DIGI':
    if contest!='FT8-RU':
        fp.write('CATEGORY-MODE: %s\n' % P.sc.my_mode);
    
    #fp.write('CLAIMED-SCORE: \n',);
    MY_CALL2 = MY_CALL.split('/')[0]
    fp.write('OPERATORS: %s\n' % MY_CALL2);
    #MY_CLUB='SOUTHERN CALIFORNIA CONTEST CLUB'
    fp.write('CLUB: %s\n' % MY_CLUB);
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
print('\nCabrillo converter beginning ...')
P=PARAMS()
if True:
    print("P=")
    pprint(vars(P))
print('Start Date=',P.sc.date0)
print('Stop Date =',P.sc.date1)
print('\nInput file(s):',P.input_files)
print('OUTPUT FILE=',P.output_file)

P.contest_name=P.sc.contest

# Init
istart  = -1
cum_gap = 0
if P.sc.contest=='MAKROTHEN-RTTY':
    sc = MAKROTHEN_SCORING(contest)
elif P.sc.contest=='ARRL 10': \
    sc = ARRL_RTTY_RU_SCORING(contest)
elif not P.sc:
    #sc = contest_scoring(contest)
    print('\nUnrecognized contest - aborting -',P.sc.contest,'\n')
    sys.exit(0)

# Read adif input file(s)
qsos2=[]
for f in P.input_files:
    fname=os.path.expanduser( f )
    print('\nInput file:',fname)
    
    p,n,ext=parse_file_name(fname)
    print('fname=',fname)
    print('p=',p)
    print('n=',n)
    print('e=',ext)

    if ext=='.LOG':
        qsos1 = parse_simple_log(fname,args)
    elif ext=='.csv':
        print('Reading CSV file ...')
        qsos1,hdr=read_csv_file(fname)
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
        
    if date_off>=P.sc.date0 and date_off<=P.sc.date1:
        rec["time_stamp"]=date_off
        qsos.append(rec)
    elif date_off>P.sc.date1:
        if first_time:
            print('\n***********************************************************************')
            print('************ WARNING *** Extra QSO(s) found after contest end *********')
            print('***********************************************************************\n')
            first_time=False
        
qsos.sort(key=lambda x: x['time_stamp'])

# Open output file
print('Output File=',P.output_file)
fp=open_output_file(P,P.output_file)

# Load history file
print('History file:',P.history,'\n')
HIST,fname9 = load_history(P.history)

# Loop over all qsos
j=-1
lines=[]
times=[0]
rates=[0]
time_cw=[0]
dts=[10*60]
times5=[0]
tlast=P.sc.date0
nqsos=0
op_time=0
for i in range(len(qsos)):
    rec=qsos[i]
    #print('\n',i,rec)
    #date_off = datetime.datetime.strptime( rec["qso_date_off"]+" "+rec["time_off"] , "%Y%m%d %H%M%S")
    date_off = rec['time_stamp']

    # Ignore entries outside contest window - this is now done above so can eventually clean this up
    if date_off>=P.sc.date0 and date_off<=P.sc.date1:
        nqsos+=1
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
            t0 = date_off
            print('t0=',t0,'\n',nqsos,'\tFirst call=',rec['call'],'\t',rec['band'])

            # Actual start time
            gap_min0 = (date_off - P.sc.date0).total_seconds() / 60.0
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
            try:
                df = float(rec['freq']) - float(qsos[i-1]['freq'])
                t1 = rec['time_stamp']
            except:
                print('Problem with freq and/or time_stamp:')
                print('rec=',rec)
                sys.exit(0)
                
            if j==i:
                gap_min = (date_off - qsos[i-1]['time_stamp']).total_seconds() / 60.0
                if P.sc.contest!='Specific Call':
                    print('Time gap:',gap_min,'minutes')
                if gap_min>30:
                    cum_gap += gap_min
                    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Time Gap %%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
                    print(date_off,rec['call'],qsos[i-1]['call'])

            #print('t1=',t1)
            dt=(t1-t0).total_seconds() / 60.0
            if P.sc.contest!='Specific Call':
                op_time=( (t1 - P.sc.date0).total_seconds()/60.0 - cum_gap)/60.
                if False:
                    print(nqsos,'\t',op_time,'\tdt=',int(dt+.5),
                          '\t\trate = ',qrate,' per hour\t\t',
                          rec['call'],'\t',rec['mode'],'\t',
                          rec['band'],'\t',df==0)
                times.append(dt/60.)
                rates.append(qrate)
                if rec['mode']=='CW':
                    time_cw.append(dt/60.)
                else:
                    time_cw.append(np.nan)

        # Keep track of instantaneous rate as well
        #if not rapid:
        dt1=(date_off-P.sc.date0).total_seconds() / 3600.
        times5.append(dt1)
        dt2 = (date_off-tlast).total_seconds()
        dts.append(dt2)
        tlast = date_off
        last_rec = rec
        
        # Check for rapid dupes - this often happens with FT4/8
        dupe,rapid = P.sc.check_dupes(rec,qsos,i,istart)
        if rapid and (P.sc.contest!='FT8-RU' or False):
            print('<<<<<<<<<<< RAPID dupe skipped >>>>>>>>>>>>>>\n')
            P.sc.nskipped+=1
            continue

        # Check for operating time limit - NAQP has this (as do others)
        if op_time>P.TIME_LIMIT:
            print('<<<<<<<<<<< Time limit exceeded >>>>>>>>>>>>>>',
                  60*(op_time-P.TIME_LIMIT),'\t',rec['call'])
            P.sc.nskipped+=1
            dupe=True
            #continue

        if P.sc.contest=='13 Colonies Special Event':
            # This one has a different API - leaving it like this for now
            # but would be nice to be consistent!
            P.sc.cols13(fp,qsos)
            sys.exit(0)

        elif P.sc.contest=='Satellites Worked':
            # This one also has a different API - leaving it like this for now
            # but would be nice to be consistent!
            P.sc.satellites(fp,qsos)
            sys.exit(0)

        else:
            # This is how things should be for all contests
            # Added arg HIST2 for CQP
            line = P.sc.qso_scoring(rec,dupe,qsos,HIST,P.sc.my_mode,P.HIST2)
            
        #print(line)
        dupe=False
        for L in lines:
            if L==line:
                if line:
                    print('@@@@@@@@@@@@@@@@@@@@@@@@ Duplicate line found\n',line)
                dupe=True
        if line!=None and not dupe:
            lines.append(line)
            fp.write('%s\n' % line)

fp.write('END-OF-LOG:\n')
fp.close()
print('\nLasst call=',last_rec['call'],'\t',last_rec['band'])

print(" ")
P.sc.check_multis(qsos)
P.sc.summary()
print(" ")

# Actual stop time & average qso rate
print('Start Date/Time:',P.sc.date0)
print('End   Date/Time:',P.sc.date1)
print('\nStart time gap:\t\t%8.1f minutes\t=%8.1f hours' % (gap_min0,gap_min0/60.) )
gap_min = (P.sc.date1 - date_off).total_seconds() / 60.0
cum_gap += gap_min
print('Stop time gap:\t\t%8.1f minutes\t=%8.1f hours'  % (gap_min,gap_min/60.) )
print('Total time off:\t\t%8.1f minutes\t=%8.1f hours' % (cum_gap, cum_gap/60.) )
duration = (P.sc.date1 - P.sc.date0).total_seconds() / 60.0
print('Contest duration:\t%8.1f minutes \t=%8.1f hours' %(duration,duration/60.) )
op_time=duration-cum_gap
print('Operating time:\t\t%8.1f minutes \t=%8.1f hours' % (op_time,op_time/60.) )
ave_rate = P.sc.nqsos2/(op_time/60.)
print('Average rate:\t\t%8.1f per hour\n' % ave_rate)


# Interpolate the rate data
rate_inst=3600./np.array(dts)
times2=[]
rates2=[]
tend=times[-1]
print('tend=',tend)
t=0
dt=1./60.
idx=0
while t<tend:
    times2.append(t)
    while times5[idx]<=t:
        #r=rates[idx]
        r=rate_inst[idx]
        idx+=1
    rates2.append(r)
    t+=dt

# Smooth out the data    
if tend>3:
    N=11
    tscale=1.
    lab='Hours'
else:
    N=11
    tscale=60.
    lab='Minutes'
h=np.ones(N)/float(N)
rates5=np.array(rates2)
rates3=np.convolve(rates5,h,'same')

times=np.array(times)
time_cw=np.array(time_cw)
times2=np.array(times2)
times5=np.array(times5)

#print('rate_inst=',rate_inst,len(rate_inst))
#print('times =',times, len(times) )
#print('times2=',times2,len(times2))
#print('times5=',times5, len(times5) )
#print('h=',h)
#print('rates2=',rates2)
#print('rates3=',rates3,len(rates3))
#print('dts=',dts,len(dts))
    
# Plot qso rate vs time
if P.RATE_GRAPH:
    fig, ax = plt.subplots()
    ax.plot(tscale*times,rates,color='red',label='All Modes')
    ax.plot(tscale*time_cw,rates,color='blue',label='CW')
    #ax.plot(times2,rates2,color='green',label='Interp')
    ax.plot(tscale*times5,rate_inst,color='cyan',label='Inst')
    ax.plot(tscale*times2,rates3,color='orange',label='Smoothed')
    ax.set_xlabel('Time from Start ('+lab+')')
    ax.set_ylabel('QSO Rate (per hour)')
    #fig.suptitle('QSO RATE')
    fig.suptitle(P.sc.contest)
    #ax.set_title('Starting at '+date1)
    ax.grid(True)    
    plt.xlim(0,tend*tscale)
    plt.ylim(0,200)
    ax.legend(loc='upper left')
    plt.show()

#! /usr/bin/python3 -u
################################################################################
#
# Params.py - Rev 1.0
# Copyright (C) 2022-4 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Command line param parser for contest scorer.
#
################################################################################
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
################################################################################

import argparse
from settings import CONFIG_PARAMS
import os

from cwt import *
from scoring import *
from fd import *
from arrl_ss import *
from vhf import *
from cwopen import *
from sst import *
from mst import *
from naqp import *
from qsop import *
from wpx import *
from iaru import *
from cqp import *
from wwdigi import *
from mak import *
from rttyru import *
from cqww import *
from arrl_dx import *
from rac import *
from colonies import *
from satellites import *
from call import *
from foc import *

################################################################################

# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        # Can add required=True to anything that is required
        arg_proc = argparse.ArgumentParser()
        arg_proc.add_argument('-mak', action='store_true',help='Makrothen RTTY')
        arg_proc.add_argument('-cwss', action='store_true',help='ARRL CW Sweepstakes')
        arg_proc.add_argument('-cqwwcw', action='store_true',help='CQ WW CW')
        arg_proc.add_argument('-arrl_dx', action='store_true',help='ARRL Intl DX')
        arg_proc.add_argument('-cq160m', action='store_true',help='CQ 160m')
        arg_proc.add_argument('-cqwwrtty', action='store_true',help='CQ WW RTTY')
        arg_proc.add_argument('-rttyru', action='store_true',help='ARRL RTTY Round Up')
        arg_proc.add_argument('-ftru', action='store_true',help='FT Round Up')
        arg_proc.add_argument('-ten', action='store_true',help='ARRL 10 Meter')
        arg_proc.add_argument('-vhf', action='store_true',help='ARRL VHF')
        arg_proc.add_argument('-cqvhf', action='store_true',help='CQ WW VHF')
        arg_proc.add_argument('-vhfss', action='store_true',help='CW VHF Soc. Spring Sprint')
        arg_proc.add_argument('-fall50', action='store_true',help='SE VHF Soc. 50 MHz Fall Sprint')
        arg_proc.add_argument('-namss', action='store_true',help='NA Meteor Scatter Sprint')
        arg_proc.add_argument('-fd', action='store_true',help='ARRL Field Day')
        arg_proc.add_argument('-sprint', action='store_true',help='NS and NCJ Sprint')
        arg_proc.add_argument('-wwdigi', action='store_true',help='World Wide Digi DX')
        arg_proc.add_argument('-cwt',help='CW Ops Mini-Test',
                              nargs='*',type=int,default=None)
        arg_proc.add_argument('-cwopen',help='CW Ops CW Open',
                              nargs='*',type=int,default=None)
        arg_proc.add_argument('-mst',help='Medium  Speed Mini-Test',
                              nargs='*',type=int,default=None)
        arg_proc.add_argument('-sst', action='store_true',help='Slow Speed Mini-Test')
        arg_proc.add_argument('-foc', action='store_true',help='FOC BW')
        arg_proc.add_argument('-rac', action='store_true',help='RAC Winter Contest')
        arg_proc.add_argument('-ocdx', action='store_true',help='Oceania DX CW')
        arg_proc.add_argument('-call',help='All QSOs with a Specific Call(s)',
                              nargs='*',type=str,default=None)
        arg_proc.add_argument('-cols13', action='store_true',help='13 Colonies Special Event')
        arg_proc.add_argument('-sats', action='store_true',help='Satellites Worked')
        arg_proc.add_argument('-naqpcw', action='store_true',help='NAQP CW')
        arg_proc.add_argument('-naqprtty', action='store_true',help='NAQP RTTY')
        arg_proc.add_argument('-state', help='State QSO Party',\
                              type=str,default=None)
        arg_proc.add_argument('-cqmm', action='store_true',help='CQMM')
        arg_proc.add_argument('-wpxcw', action='store_true',help='CQ WPX CW')
        arg_proc.add_argument('-wpxrtty', action='store_true',help='CQ WPX RTTY')
        arg_proc.add_argument('-iaru', action='store_true',help='IARU HF')
        arg_proc.add_argument('-cqp', action='store_true',help='Cal QSO Party')
        arg_proc.add_argument('-nograph', action='store_true',
                              help='Dont plot rate graph')
        arg_proc.add_argument('-trap', action='store_true',
                              help='Trap errors')
        arg_proc.add_argument('-assisted', action='store_true',
                              help='Used assitance (cluster, etc.)')
        arg_proc.add_argument("-i", help="Input ADIF file",
                              type=str,default=None)
        arg_proc.add_argument("-limit", help="Time Limit (Hours)",
                              type=int,default=10000)
        arg_proc.add_argument("-o", help="Output Cabrillo file",
                              type=str,default='MY_CALL.txt')
        arg_proc.add_argument("-hist", help="History File",
                              type=str,default='')
        args = arg_proc.parse_args()

        #######################################################################################
        
        fname = args.i
        fnames=''

        self.history = ''
        self.sc=None

        self.category_band ='ALL'
        self.TIME_LIMIT    = args.limit
        self.TRAP_ERRORS   = args.trap
        self.ASSISTED      = args.assisted
        self.RATE_GRAPH    = not args.nograph

        P=CONFIG_PARAMS('.keyerrc')
        self.SETTINGS=P.SETTINGS
        self.HIST2=None

        MY_CALL   = self.SETTINGS['MY_CALL']
        OPERATOR  = self.SETTINGS['MY_OPERATOR']
        HIST_DIR  = os.path.expanduser('~/Python/data/')
        HIST_DIR2 = os.path.expanduser('~/Python/history/data/')
        self.output_file = args.o.replace('MY_CALL',MY_CALL)

        #######################################################################################

        # Contest-specific stuff
        if args.mak:
            sc = MAKROTHEN_SCORING(P)
            self.sc=sc
            
            contest=sc.contest
            MY_MODE='RTTY'
            date0=sc.date0
            date1=sc.date1
            history = sc.history
            
            #fname = 'mak_rtty_2019.adif'
            DIR_NAME = '../pyKeyer'
            fname = 'AA2IL.adif'

        elif args.rttyru:
            sc = ARRL_RTTY_RU_SCORING(P,'ARRL-RTTY')
            #self.sc=sc
            
            contest=sc.contest
            MY_MODE='MIXED'          # sc.my_mode
            date0=sc.date0
            date1=sc.date1
            history = sc.history
            
            fname1='aa2il_2022.adif'
            fnames = [DIR_NAME+'/'+fname1]

            DIR_NAME = '~/.local/share/WSJT-X - CONTEST'
            #fname2 = '2019_rtty_ru.adi'
            fname2 = 'wsjtx_log.adi'
            fnames.append( DIR_NAME+'/'+fname2 )
            output_file = sc.output_file

        elif args.ftru:

            # FT Round-up in December
            sc = ARRL_RTTY_RU_SCORING(P,'FT8-RU')
            self.sc=sc
            
            self.history = HIST_DIR+'master.csv'
            fname = 'wsjtx_log.adi'
            DIR_NAME = '~/.local/share/WSJT-X - CONTEST'
            fname = 'FTRU_2023.csv'
            fname = 'FTRU_2023.adif'
            DIR_NAME = './'
    
        elif args.ten:

            # ARRL 10m contest
            sc = ARRL_RTTY_RU_SCORING(P,'ARRL-10')
            self.sc=sc
            self.history = HIST_DIR+'master.csv'
            
            fname = 'AA2IL_2021.adif'
            fname = 'AA2IL.adif'
            DIR_NAME = '~/AA2IL'

            #DIR_NAME = '../pyKeyer'
            #fname = 'AA2IL.adif'
            output_file = sc.output_file
    
        elif args.cq160m:

            # ARRL 10m contest
            sc = ARRL_RTTY_RU_SCORING(P,'CQ-160')
            self.sc=sc
            
            fname = 'AA2IL.adif'
            DIR_NAME = '~/AA2IL'
            output_file = sc.output_file
    
        elif args.vhf or args.cqvhf or args.fall50 or args.namss or args.vhfss:

            # ARRL & CQ WW VHF Contests
            if args.vhf:
                org='ARRL'
            elif args.cqvhf:
                org='CQ'
            elif args.vhfss:
                org='CSVHF'
            elif args.fall50:
                org='SVHFS'
            elif args.namss:
                org='NAMSS'
            else:
                print('\n*** ERROR - Invalid sponser ***\n')
                sys.exit(0)
                
            sc = VHF_SCORING(P,org)
            self.sc=sc
            fname = sc.fname
            DIR_NAME = sc.DIR_NAME

            """
            # Need to merge FT8 and CW/Phone logs from RPi
            fnames=[]
            #DIR_NAME = '~/.fldigi/logs/'
            #for fname in ['AA2IL_RPi.adif','wsjtx_log_FT991a.adi','wsjtx_log_IC9700.adi']:
            DIR_NAME = '~/Python/pyKeyer/June_VHF'
            for fname in ['VHF.adif','FT8.adif']:
                f=os.path.expanduser( DIR_NAME+'/'+fname )
                fnames.append(f)
            """
            
        elif args.fd:

            # ARRL Field Day
            sc = ARRL_FD_SCORING(P)
            self.sc=sc
            
            self.history = HIST_DIR+'master.csv'
            
            # Need to merge FT8 and CW logs
            fnames=[]
            DIR_NAME = '~/logs/'
            DIR_NAME = '~/Python/pyKeyer/Field_Day'
            fnames=[]
            #for fname in ['AA2IL.adif']:
            #for fname in ['FD.csv']:
            #for fname in ['AA2IL.adif','wsjtx_log.adi']:
            for fname in ['FD.csv','wsjtx_log.adi']:
            #for fname in ['FD.csv','FTx.csv']:
                f=os.path.expanduser( DIR_NAME+'/'+fname )
                fnames.append(f)
    
        elif args.wwdigi:
            sc = WWDIGI_SCORING(P)
            self.sc=sc

            DIR_NAME = '~/.local/share/WSJT-X - CONTEST'
            #fname = '2019_rtty_ru.adi'
            fname = 'wsjtx_log.adi'

        elif args.cwss:
            sc = ARRL_SS_SCORING(P,self.TRAP_ERRORS)
            self.sc=sc
            
            fname = 'AA2IL.adif'
            DIR_NAME = '~/Python/pyKeyer'

            fname = 'SS.csv'
            DIR_NAME = '~/Python/pyKeyer/SS_2024'
            
            self.history = HIST_DIR2+'/SSCW-2024-*.txt'
            #self.history = HIST_DIR+'master.csv'
            
        elif args.naqprtty:

            # North American QSO Party RTTY
            sc = NAQP_SCORING(P,'RTTY')
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            #print('fname=',fname)
            if fname==None:
                #DIR_NAME = '~/'+MY_CALL+'/'
                #fname = MY_CALL+'.adif'
                DIR_NAME = '~/logs/'
                fname='naqp_rtty_2023.adif'
            else:
                DIR_NAME = '.'
                #DIR_NAME = '~/.fllog/'
            print('fname=',fname)
    
        elif args.naqpcw:

            # North American QSO Party CW
            sc = NAQP_SCORING(P,'CW')
            self.sc=sc

            self.history = HIST_DIR+'master.csv'

            #DIR_NAME = '../pyKeyer/NAQP/'    
            DIR_NAME = './'    
            fname = 'NAQP.csv'
            #fname = 'NAQP.adif'

        elif args.state:

            # State QSO Party
            sc = QSOP_SCORING(P,'CW',args.state)
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            #fname = MY_CALL+'.adif'
            #DIR_NAME = '~/'+MY_CALL+'/'
            DIR_NAME='./'
            
        elif args.arrl_dx:

            # ARRL Internationl DX 
            sc = ARRL_INTL_DX_SCORING(P)
            self.sc=sc

            self.history = HIST_DIR+'master.csv'

            DIR_NAME = '~/AA2IL/'
            fname = 'AA2IL.adif'
    
        elif args.cqwwcw:

            # CQ World Wide CW
            sc = CQ_WW_SCORING(P,'CW')
            self.sc=sc

            self.history = HIST_DIR+'master.csv'

            DIR_NAME = '~/AA2IL/'
            #fname = 'AA2IL_2021.adif'
            
            #DIR_NAME = '~/logs/'
            fname = 'AA2IL.adif'
    
        elif args.cqwwrtty:
            
            # CQ World Wide RTTY
            sc = CQ_WW_SCORING(P,'RTTY')
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            
            #DIR_NAME = '~/logs/'
            #fname = 'cqww_rtty_2023.adif'
            DIR_NAME = '~/AA2IL/'
            fname = 'AA2IL.adif'

        elif args.cqmm or args.wpxcw or args.wpxrtty:
            
            # CQ WPX
            if args.cqmm:
                MODE='CW'
                NAME='CQMM'
            elif args.wpxcw:
                MODE='CW'
                NAME='WPX'
            else:
                MODE='RTTY'
                NAME='WPX'
            sc = CQ_WPX_SCORING(P,MODE,NAME)
            self.sc=sc
            self.history = HIST_DIR+'master.csv'
            
            if MODE=='CW':
                DIR_NAME = '~/Python/pyKeyer/'
                fname = 'AA2IL.adif'
                #fname = 'WPX.csv'
                #DIR_NAME='./'
            else:
                DIR_NAME = '../../logs/fllog/'
                fname = 'cq_wpx_rtty_2019.adif'
                fname = 'cq_wpx_rtty_2022.adif'

        elif args.iaru:

            # IARU HF Champs
            sc = IARU_HF_SCORING(P)
            self.sc=sc
            self.history = sc.history
            fname = sc.fname
            DIR_NAME = sc.DIR_NAME

        elif args.cqp:

            # California QSO Party
            sc = CQP_SCORING(P)
            self.sc=sc
            
            self.history = HIST_DIR+'master.csv'
            self.HIST2=sc.read_hist2(args.hist)
            
            MY_CALL1 = self.SETTINGS['MY_CALL'].split('/')[0]
            MY_CALL2 = self.SETTINGS['MY_CALL'].replace('/','_')
            #DIR_NAME = '~/'+MY_CALL1+'/'
            #fname = MY_CALL2+'_2021.adif'    # Testing
            DIR_NAME = '~/'+MY_CALL1+'/'
            fname = MY_CALL2+'.adif'
            
            DIR_NAME = '../pyKeyer/CQP/'      # 2022
            fname = 'CQP.csv'
            fname = 'CQP.adif'

            DIR_NAME = '../pyKeyer/'      # 2024
            DIR_NAME = './'   
            fname = 'W6A.adif'
            
        elif args.rac or args.ocdx:

            # RAC Contests or OC DX
            if args.ocdx:
                P.TXT='OCDX'
            else:
                P.TXT='RAC'
            
            sc = RAC_SCORING(P)
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            fname = MY_CALL+'.adif'
            #fname = MY_CALL+'_2022.adif'
            DIR_NAME = '~/'+MY_CALL+'/'

            fname = 'RAC.csv'
            DIR_NAME='./'
            
        elif args.sst:

            # K1USN SST
            sc = SST_SCORING(P,'SST')
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            fname = MY_CALL+'.adif'
            DIR_NAME = '~/'+MY_CALL+'/'

        elif args.sprint:

            # NS and NCJ sprint
            sc = SST_SCORING(P,'SPRINT')
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            fname = MY_CALL+'.adif'
            DIR_NAME = '~/'+MY_CALL+'/'

        elif args.foc:

            # FOC BW
            sc = FOCBW_SCORING(P,'SPRINT')
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            fname = MY_CALL+'.adif'
            DIR_NAME = '~/'+MY_CALL+'/'

        elif args.cwt!=None:

            # CWops CWT
            print('cwt=',args.cwt)
            if len(args.cwt)>0:
                session=args.cwt[0]
            else:
                session=None
                
            sc = CWT_SCORING(self,session)
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            fname = MY_CALL+'.adif'
            DIR_NAME = '~/'+OPERATOR+'/'
            
        elif args.cwopen!=None:

            # CW Ops CW Open
            if len(args.cwopen)>0:
                session=args.cwopen[0]
            else:
                session=None
            sc = CWOPEN_SCORING(P,session)
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            if fname==None:
                fname = MY_CALL+'.adif'
                DIR_NAME = '~/'+MY_CALL+'/'
            else:
                DIR_NAME = '.'
            print('fname=',fname)
            
        elif args.mst!=None:
            print('mst=',args.mst)
            if len(args.mst)>0:
                session=args.mst[0]
            else:
                session=None
        
            sc = MST_SCORING(P,session)
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            fname = MY_CALL+'.adif'
            DIR_NAME = '~/'+MY_CALL+'/'

        elif args.cols13:

            # 13 Colonies special event
            sc=THIRTEEN_COLONIES_SES(P)
            self.sc=sc

            #contest=sc.contest
            #MY_MODE=sc.my_mode
            #date0=sc.date0
            #date1=sc.date1
            #history = ''
            
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

            # Satellites
            sc = SATCOM(P)
            self.sc=sc

            #self.history = ''
            fname = 'AA2IL.adif'
            DIR_NAME = '../pyKeyer'
            fnames = [DIR_NAME+'/'+fname]
            fname = 'vhf.adif'
            DIR_NAME = '~/logs'
            fnames.append( DIR_NAME+'/'+fname )
            
        elif args.call!=None:

            # Specific calls
            print('args.call=',args.call)
            if len(args.call)>0:
                calls=args.call
            else:
                print('ERROR - Need to specify at least one call sign')
                sys.exit(0)                

            # Specific call
            sc = SPECIFIC_CALL(P,calls)
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            fname = MY_CALL+'.adif'
            DIR_NAME = '~/'+MY_CALL+'/'
            
        else:
            print('Need to specify a single contest')
            sys.exit(0)

        print('DIR_NAME=',DIR_NAME,'\tfnames=',fnames,'\t',type(fnames))
        if type(fnames) == list:   
            self.input_files  = fnames
        else:
            self.input_files  = [DIR_NAME + '/' + fname]

        self.output_file = sc.output_file
        #sys.exit(0)

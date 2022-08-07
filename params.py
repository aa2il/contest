#! /usr/bin/python3 -u
################################################################################
#
# Params.py - Rev 1.0
# Copyright (C) 2022 by Joseph B. Attili, aa2il AT arrl DOT net
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
from wpx import *
from iaru import *
from cqp import *
from wwdigi import *
from mak import *
from rttyru import *
from cqww import *
from colonies import *
from satellites import *
from call import *

################################################################################

# User params
#DIR_NAME = '~/.fldigi/logs/'

################################################################################

# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        # Can add required=True to anything that is required
        arg_proc = argparse.ArgumentParser()
        arg_proc.add_argument('-mak', action='store_true',help='Makrothen RTTY')
        arg_proc.add_argument('-cwss', action='store_true',help='ARRL CW Sweepstakes')
        arg_proc.add_argument('-wwcw', action='store_true',help='CQ WW CW')
        arg_proc.add_argument('-wwrtty', action='store_true',help='CQ WW RTTY')
        arg_proc.add_argument('-rttyru', action='store_true',help='ARRL RTTY Round Up')
        arg_proc.add_argument('-ft8ru', action='store_true',help='FT8 Round Up')
        arg_proc.add_argument('-ten', action='store_true',help='ARRL 10 Meter')
        arg_proc.add_argument('-vhf', action='store_true',help='ARRL VHF')
        arg_proc.add_argument('-cqvhf', action='store_true',help='CQ WW VHF')
        arg_proc.add_argument('-fd', action='store_true',help='ARRL Field Day')
        arg_proc.add_argument('-wwdigi', action='store_true',help='World Wide Digi DX')
        arg_proc.add_argument('-cwt',help='CW Ops Mini-Test',
                              nargs='*',type=int,default=None)
        arg_proc.add_argument('-cwopen', action='store_true',help='CW Ops CW Open')
        arg_proc.add_argument('-mst',help='Medium  Speed Mini-Test',
                              nargs='*',type=int,default=None)
        arg_proc.add_argument('-sst', action='store_true',help='Slow Speed Mini-Test')
        arg_proc.add_argument('-call',help='All QSOs with a Specific Call(s)',
                              nargs='*',type=str,default=None)
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
        type=str,default='MY_CALL.txt')
        arg_proc.add_argument("-hist", help="History File",
                              type=str,default='')
        args = arg_proc.parse_args()

        #######################################################################################
        
        fname = args.i
        fnames=''

        self.history = ''
        self.sc=None

        self.category_band='ALL'

        P=CONFIG_PARAMS('.keyerrc')
        self.SETTINGS=P.SETTINGS
        self.HIST2=None

        MY_CALL = self.SETTINGS['MY_CALL']
        HIST_DIR = os.path.expanduser('~/'+MY_CALL+'/')
        self.output_file = args.o.replace('MY_CALL',MY_CALL)

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
    
        elif args.ten:
            contest='ARRL 10'
            MY_MODE='CW'
            date0 = datetime.datetime.strptime( "20201212 0000" , "%Y%m%d %H%M")  # Start of contest
            date1 = date0 + datetime.timedelta(hours=48)
            DIR_NAME = '../pyKeyer'
            fname = 'AA2IL.adif'
            output_file = 'AA2IL_10m_2020.LOG'
    
        elif args.vhf or args.cqvhf:

            # ARRL & CQ WW VHF Contests
            if args.vhf:
                org='ARRL'
            else:
                org='CQ'
            sc = VHF_SCORING(P,org)
            self.sc=sc

            # Need to merge FT8 and CW/Phone logs
            fnames=[]
            DIR_NAME = '~/.fldigi/logs/'
            #DIR_NAME='.'
            for fname in ['AA2IL.adif','wsjtx_log.adi']:
                #for fname in ['AA2IL_VHF_Sep2021.adif','wsjtx_VHF_Sep2021.adi']:
                f=os.path.expanduser( DIR_NAME+'/'+fname )
                fnames.append(f)

        elif args.fd:

            # ARRL Field Day
            sc = ARRL_FD_SCORING(P)
            self.sc=sc
            
            self.history = HIST_DIR+'master.csv'
            
            # Need to merge FT8 and CW logs
            fnames=[]
            DIR_NAME = '~/logs/'
            #DIR_NAME = '~/AA2IL/Contesting/Field_Day/field_day_2022/'
            fnames=[]
            #for fname in ['AA2IL.adif','ft8_contest.adi','pi2_ft8_contest.adi']:
            for fname in ['AA2IL.adif','ft8_contest.adi','rpi_fd_2022.adi']:
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
            #history = 'HIST_DIR/SSCW.txt'
            history = 'HIST_DIR/SSCW-2021-LAST-2.txt'
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
            history = 'HIST_DIR/master.csv'
            fname = 'naqp.adif'
            DIR_NAME = '~/.fllog/'
    
        elif args.naqpcw:

            # North American QSO Party CW
            sc = NAQP_SCORING(P,'CW')
            self.sc=sc

            self.history = HIST_DIR+'master.csv'
            fname = MY_CALL+'.adif'
            DIR_NAME = '~/'+MY_CALL+'/'

        elif args.wwcw:
            contest='CQ-WW-CW'
            MY_MODE='CW'
            date0 = datetime.datetime.strptime( "20201128 0000" , "%Y%m%d %H%M")  # Start of contest
            date1 = date0 + datetime.timedelta(hours=48)
            
            history = 'HIST_DIR/master.csv'
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

            # IARU HF Champs
            sc = IARU_HF_SCORING(P)
            self.sc=sc
            
            self.history = HIST_DIR+'master.csv'
            fname = MY_CALL+'.adif'
            DIR_NAME = '~/'+MY_CALL+'/'

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

            # K1USN SST
            sc = SST_SCORING(P)
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
            DIR_NAME = '~/'+MY_CALL+'/'
            
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
            sc=THIRTEEN_COLONIES(P)
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

        #print(fnames)
        #print(type(fnames))
        if type(fnames) == list:   
            self.input_files  = fnames
        else:
            self.input_files  = [DIR_NAME + '/' + fname]

        self.output_file = sc.output_file
        #sys.exit(0)

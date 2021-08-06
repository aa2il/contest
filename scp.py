#! /usr/bin/python3
############################################################################################
#
# scp.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Program to play with Super Check Partial Database
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
#pip3 install python-Levenshtein
import Levenshtein

############################################################################################
s1="Hello World"
s2="Hllo World"
print('dx=', Levenshtein.distance(s1,s2) )

call1 = input("Enter a call:\n")
if len(call1)==0:
    call1='aa2il1'
call1=call1.upper()
print('call1=',call1)

call2 = input("Enter another call:\n")
if len(call2)==0:
    call2='aa2il1/6'
call2=call2.upper()
print('call2=',call2)

print('dx=', Levenshtein.distance(call1,call2) )
print(' ')

fname='../data/MASTER.SCP'
with open(fname) as f:
    scp = f.readlines()
#print('No. SCP=',len(scp))

calls=[s.strip() for s in scp if '#' not in s]
#print('No. SCP=',len(calls))
#print(calls[0],calls[-1])

matches=[]
for c in calls:
    dx= Levenshtein.distance(call1,c) 
    if dx<=1:
        matches.append(c)

print(matches)

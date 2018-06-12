##################################
##Author:  Sushma Kalle    	 	##
##@Input:  Ladder Logic	   	 	##
##@Output: Instruction List   	##
##################################

import math
import sys
import os,errno
import numpy as np
#import extractor_refined
import re
import MySQLdb
import base64
import binascii
from collections import defaultdict

temp = "c490"
tempf = 'c290'
line = []
templ = ''
tempvals = ['c290','c490','bc90']
flag = 0

def convert(hexcode,htype):
	ret = ''
	
	if(htype == '14'):
		number = hexcode[2:4] + hexcode[0:2]
		number = int(number,16)
		number = (number - 0x8100) / 2
		if number < 2000:
			ret = "%MW" + str(number)
		else:
			ret = hexcode
	elif htype == '32':
		number = hexcode[2:4] + hexcode[0:2]
		number = int(number,16)
		number = (number - 0x8100) / 2
		if number < 2000:
			ret = "%MF" + str(number)
		else:
			ret = hexcode
	elif htype == '1a':
		number = hexcode[2:4] + hexcode[0:2]
		number = int(number,16)
		ret = str(number)
	elif htype == '29':
		lilhex = hexcode[6:8] + hexcode[4:6] + hexcode[2:4] + hexcode[0:2] 
		bit = format(int(lilhex, 16), '32b')
		if bit[0] == ' ':
			sign = 0 
		else:
			sign = bit[0]
		E = bit[1:9].replace(' ','0')
		F = bit[9:].replace(' ','0')
		number = ( math.pow((-1),int(sign)) ) * ( 1 + (int(F,2) * math.pow(2,-23))) * math.pow(2,(int(E,2) - 127))
		ret = str(round(number,7))
	elif htype == '16':
		if hexcode == 'b491':
			ret = '%IW1.0'
	if hexcode == '0c92':
		ret = '%QWE0'
	elif hexcode == '0e92':
		ret = '%QWE1'
	return ret
def parseMemWords(s):
	#7F1A05141A028102810100
	three = 0
	length = s[2:4]
	operation = s[8:10]
	first_type = s[10:12]
	second_type = s[12:14]
	first = s[14:18]
	second = s[18:22]
	operation_options = {	'04' : '+',
							'05' : '-',
							'06' : '*',
							'07' : '/',
							'1e' : ':=',
							'25' : '<',
							'26' : '<=',
							'27' : '>',
							'28' : '>=',
							'29' : '<>',
							'2a' : '='
						}
						
	if int(length,16) > 11:
		third = s[22:26]
		lhs = convert(first, '14')
		first = convert(second, first_type)
		second = convert(third, second_type)
		
		result =  lhs + ' := ' + first + "  " + operation_options[operation] + '  ' + second 
	else:
		first = convert(first,first_type)
		second = convert(second,second_type)
		result =   first + "  " + operation_options[operation] + '  ' + second 
	return result


def parseMemFloats(s):
	three = 0
	length = s[2:4]
	op = s[8:10]
	operation = int(s[8:10],16)
	first_type = s[14:16]
	second_type = s[16:18]
	op_type = {	"29" : 8,
				"32" : 4
			  }
	operation_options = {	'33' : '<' ,
							'34' : '<=',
							'35' : '>' ,
							'36' : '>=',
							'37' : '=' ,
							'38' : '<>',
							'39' : '+' ,
							'3a' : '-' ,
							'3b' : '*' ,
							'3c' : '/' ,
							'86' : ':='
					 	}
	if operation >= 51 and operation <=56:
		first = convert(s[18:22],'32')
		second = convert(s[22:22+op_type[second_type]],second_type)
		result =   first + "  " + operation_options[op] + '  ' + second
	else:
		lhs = convert(s[18:22],'32')
		first = convert(s[22:22+op_type[first_type]],first_type)
		second = convert(s[22+op_type[first_type]:22+op_type[first_type]+op_type[second_type]],second_type)
		result =  lhs + ' := ' + first + "  " + operation_options[op] + '  ' + second  
	return result

def parseEqs(st):
	length = len(st)

	operation = int(st[8:10],16)
	if operation >= 51:
		if length < 5:
			print 'error'
		elif 'c290' not in st:
			res = parseMemFloats(st)
			line.append(res)
		else:
			prev= ''
			fl_len = int(st[2:4],16) * 2
			linepart = st[0:fl_len]
			templ = parseMemFloats(linepart)
			if len(st[fl_len:]) > 5:
				parseEqs(st[fl_len:])
			
			line.append(templ)
		
	else:
		if length < 5:
			print 'error'
		elif length <= 26:
			res = parseMemWords(st)
			line.append(res)
		else:
			prev= ''
			fl_len = int(st[2:4],16) * 2
			linepart = st[0:fl_len]
			templ = parseMemWords(linepart)
			if len(st[fl_len:]) > 5:
				parseEqs(st[fl_len:])
			line.append(templ)
def parse(st):
	try:

		global line
		#print st
		parseEqs(st.strip())
		utilized = {}
		initialized = {}
		assigned = {}
		final = ''
		if len(line) > 1:
			for li in line:
				for temp in tempvals:
					if temp in li:
						if li.find(temp) < li.find("="):
							if li.find(temp,li.find(temp)+1) > li.find("="):
								if temp in utilized:
									just = utilized[temp]
									utilized[temp] = just.replace(temp,'( ' + li[li.find('=')+1:] + ' )')
								else:
									utilized[temp] = li[li.find('=')+1:]
							else:
								initialized[temp] = li[li.find('=')+1:]
						else:
							if li[:li.find('=')-2] not in tempvals:
								assigned[li[:li.find('=')-2]] = li
								final = li[:li.find('=')-2]
			try:		
				for key,value in initialized.items():
					for k,val in utilized.items():
						if key in val:
							utilized[k] = utilized[k].replace(key,'( '+ value + ' )')
				for key,value in utilized.items():
					for k,val in assigned.items():
						if key in val:
							assigned[k] = assigned[k].replace(key,  value  )
				for key,value in initialized.items():
					for k,val in assigned.items():
						if key in val:
							assigned[k] = assigned[k].replace(key,'( '+ value + ' )')
				final = '[ ' + assigned[final] + ' ]'
				line = []
			except KeyError as e:
				pass
				#print str(e) + st + "im here again"
		else:
			final = '[ ' + line[0] + ' ]'	
			line = []
		
		return final
	except AttributeError as ae1:
		pass
	
#parse(sys.argv[1]) 

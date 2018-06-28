##################################
##Author:  Sushma Kalle    	 	##
##@Input:  Ladder Logic	   	 	##
##@Output: Instruction List   	##
##################################

import pyshark
import sys
import os,errno
import numpy as np

import re
import MySQLdb
import memwords
from operator import itemgetter



start = 0
flag = 0
thisline = ''
db = MySQLdb.connect(host="localhost",  # host 
                     user="root",       # username
                     passwd="12345",    # password
                     db="modicon")   	# name of the database

cur = db.cursor()
cur.execute("select op_code,instruction,output from instructions")
rows = cur.fetchall()
cur.execute("select op_code,delimiter,category from delimiters")
delimiters = cur.fetchall()
cur.execute("select operation from operations")
operations = cur.fetchall()
cur.execute("select op_code,instruction,output from instructions where output=\'0\'")
inputs = cur.fetchall()

# Replace function for repeated occurances
def rreplace(s, old, new, occurrence):
	li = s.rsplit(old, occurrence)
	return new.join(li)

# Returns Rung end addresses
def llToRungs(ll,rows,delimiters,inputs):
	ll 		= ll[:-2]
	ends 	= []
	rungs 	= []
	end_l	= start_l	= ins_e	= ''
	cut_iter= 0
	input_addresses = []


	# To get the addresses of every end instruction
	for row in rows:
		temp = []
		if row[0] in ll and row[2] == 1:
			temp = [m.start() for m in re.finditer(row[0],ll)]
			for te in temp:
				ends.append((te,len(row[0])))

	ends = sorted(ends, key=lambda ends: ends[0])
	
	
	# The rungs with block instruction has a delimiter at the end
	for de in delimiters:
		if de[2] == 1: 	
			end_blk = [m.start() for m in re.finditer(de[0],ll)]
			end_l = de[0]	
			ins_e = de[1]
		if de[2] == 0:
			start_l = de[1]
	end_blk = end_blk[1::2]	
	
	
	# Getting the addresses of Input instructions
	for ip in inputs:
		if ip[0] in ll:
			temp = [m.start() for m in re.finditer(ip[0],ll)]
			for tem in temp:
				input_addresses.append(tem)
	
	cut = 0

	#Getting the rung end addresses from the control logic 
	for end, length in ends:
		if end+length in end_blk:
			cut = end + length + len(end_l)
		elif end+length in input_addresses:
			cut = end+length
		rung = rreplace(ll[:cut-cut_iter], end_l , "\n" +ins_e, 1)
		rungs.append(rung)
	
		ll = ll[cut-cut_iter:]
		cut_iter = cut
	rungs.append(ll)
	return rungs,start_l
		


# Decompiling Operational Block
def memOperationRung(rung,op):
	global thisline
	global flag
	length = ''
	length = rung[rung.find(op)-2:rung.find(op)]
	if rung[rung.find(op)-6:rung.find(op)-4] == '03' or flag == 1:
		flag = 1
		offset = rung.find(op)+int(length,16)*2 - 4 
		thisline = thisline + rung[rung.find(op)-4:offset]
		if rung[offset:offset+2] == '03' or not rung.find('7f1a',offset):
			return thisline
		else:
			n_op =rung.find('7f1a',offset)
			return memOperationRung(rung,rung[n_op:n_op+6])
	else:
		offset = rung.find(op)+int(length,16)*2 -4
		thisline = rung[rung.find(op)-4:offset]
		return thisline


def map(ll):
	global cur
	returnIns = ''
	result = ''
	#ll = extractor_refined.ladder_logic
	ll = ll[24:].lower().replace(":","")

	
	rungs,start_l = llToRungs(ll,rows,delimiters,inputs)
	# Decompiling one rung at a item
	for rung in rungs:
		global line
		global flag
		global thisline	 
		blk_t = 0
		if rung != '':	
			j = 0
			for op in operations:
				if op[0] in rung:
					try:
						st = memOperationRung(rung,op[0])
						flag = 0
						thisline = ''
						rep = memwords.parse(st)
						#print rep
						if rung[rung.find(op[0])-8:rung.find(op[0])-4] == '0303':
							rep = "OPER "+rep
							which = r'....'+st+'..'
						elif rung[rung.find(op[0])-8:rung.find(op[0])-4] == '03':
						 	rep = "AND "+rep
						 	which = r'..'+st+'..'
						else:
							which = r''+st
						rung = re.sub(which, rep + '\n', rung)
					except:
						pass
			for row in rows:				
				if row[0] in rung and row[2] ==1:	
					rung = rung.replace(row[0], row[1] )
				if row[0] in rung and row[2] == 0:
					rung = rung.replace(row[0],row[1]+"\n")
				if row[0] in rung and row[2] == 2:
					rung = re.sub(r''+row[0]+'..', row[1], rung)
				if row[0] in rung and row[2] == 3:
					rung = rung.replace(row[0], row[1])
			ins = rung.split("\n")
			returnIns = returnIns + "\n" + rung
			if start_l in ins[0]:
				ins[1] = "LD" + ins[1]
			else:
				ins[0] = "LD" + ins[0]
			for inst in ins: 
				result = result +  "%04d  | " % j + inst +"\n"
				j = j+1
			result = result + "---------------------------"	 + "\n"
			
	result = result + "*****************************************"
	return result


# To Test this function
#print map("aaaaaaaaaaaaaaaaaaaaaaa:7C:0C:FD:E0:2D:02")



def shadow_map():
	global cur
	returnIns = ''
	result = ''
	#ll = extractor_refined.ladder_logic
	fp = open("shadow_mem","r")
	ll = fp.read()
	

	rungs,start_l = llToRungs(ll,rows,delimiters,inputs)
	# Decompiling one rung at a item
	for rung in rungs:
		global line
		global flag
		global thisline	 
		blk_t = 0
		if rung != '':	
			j = 0
			for op in operations:
				if op[0] in rung:
					try:
						st = memOperationRung(rung,op[0])
						flag = 0
						thisline = ''
						rep = memwords.parse(st)
						#print rep
						if rung[rung.find(op[0])-8:rung.find(op[0])-4] == '0303':
							rep = "OPER "+rep
							which = r'....'+st+'..'
						elif rung[rung.find(op[0])-8:rung.find(op[0])-4] == '03':
						 	rep = "AND "+rep
						 	which = r'..'+st+'..'
						else:
							which = r''+st
						rung = re.sub(which, rep + '\n', rung)
					except:
						pass
			for row in rows:				
				if row[0] in rung and row[2] ==1:	
					rung = rung.replace(row[0], row[1] )
				if row[0] in rung and row[2] == 0:
					rung = rung.replace(row[0],row[1]+"\n")
				if row[0] in rung and row[2] == 2:
					rung = re.sub(r''+row[0]+'..', row[1], rung)
				if row[0] in rung and row[2] == 3:
					rung = rung.replace(row[0], row[1])
			ins = rung.split("\n")
			returnIns = returnIns + "\n" + rung
			if start_l in ins[0]:
				ins[1] = "LD" + ins[1]
			else:
				ins[0] = "LD" + ins[0]
			for inst in ins: 
				result = result +  "%04d  | " % j + inst +"\n"
				j = j+1
			result = result + "---------------------------"	 + "\n"
			
	return result
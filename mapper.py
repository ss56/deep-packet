import sys
import os,errno
import numpy as np
import re
import MySQLdb
import memwords
from operator import itemgetter


flag = 0
count = 0
def rreplace(s, old, new, occurrence):
	li = s.rsplit(old, occurrence)
	return new.join(li)

def llToRungs(ll,rows,delimiters):
	global count
	ll 		= ll[:-2]
	ends 	= []
	rungs 	= []
	end_l	= start_l	= ins_e	= ''
	cut_iter= 0
	
	for row in rows:
		temp = []
		if row[0] in ll and row[2] == 1:
			count = count+1
			temp = [m.start() for m in re.finditer(row[0],ll)]
			for te in temp:
				ends.append((te,len(row[0])))
	ends = sorted(ends, key=lambda ends: ends[0])
	
	
	for de in delimiters:
		if de[2] == 1: 	
			end_blk = [m.start() for m in re.finditer(de[0],ll)]
			end_l = de[0]	
			ins_e = de[1]
		if de[2] == 0:
			start_l = de[1]
	end_blk = end_blk[1::2]	
	for end, length in ends:
		if end+length in end_blk:
			cut = end + length + len(end_l)
		else:
			cut = end+length
		rung = rreplace(ll[:cut-cut_iter], end_l , "\n" +ins_e, 1)
		rungs.append(rung)
		
		ll = ll[cut-cut_iter:]
		cut_iter = cut
	return rungs,start_l
		
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
	result = ''
	global flag
	global count
	ll = ll[24:]
	#result = result +  ll
	ll = ll.replace(":" ,"")
	start = 0
	flag = 0
	db = MySQLdb.connect(host="localhost",  # host 
		                 user="root",       # username
		                 passwd="12345",    # password
		                 db="modicon")   	# name of the database

	cur = db.cursor() 

	code_list = ''
	thisline = ''

	cur.execute("select op_code,instruction,output from instructions")
	rows = cur.fetchall()
	cur.execute("select op_code,delimiter,category from delimiters")
	delimiters = cur.fetchall()
	cur.execute("select operation from operations")
	operations = cur.fetchall()
	rungs,start_l = llToRungs(ll,rows,delimiters)
	
	returnIns = ''
	for rung in rungs:
		global line
		
					 
		blk_t = 0
		if rung != '':	
			j = 0
			for op in operations:
				if op[0] in rung:
					st = memOperationRung(rung,op[0])
					flag = 0
					thisline = ''
					rep = memwords.parse(st)
					#result = result +  rep
					if rung[rung.find(op[0])-8:rung.find(op[0])-4] == '0303':
						rep = "OPER "+rep
						which = r'....'+st+'..'
					elif rung[rung.find(op[0])-8:rung.find(op[0])-4] == '03':
					 	rep = "AND "+rep
					 	which = r'..'+st+'..'
					else:
						which = r''+st
					rung = re.sub(which, rep + '\n', rung)
		
			for row in rows:				
				if row[0] in rung and row[2] ==1:
					count = count+1	
					rung = rung.replace(row[0], row[1] )
				if row[0] in rung and row[2] == 0:
					count = count+1
					rung = rung.replace(row[0],row[1]+"\n")
				if row[0] in rung and row[2] == 2:
					count = count+1
					rung = re.sub(r''+row[0]+'..', row[1], rung)
				if row[0] in rung and row[2] == 3:
					count = count+1
					rung = rung.replace(row[0], row[1])
			ins = rung.split("\n")
			returnIns = returnIns + "\n" + rung
			if start_l in ins[0]:
				ins[1] = "LD" + ins[1]
			else:
				ins[0] = "LD" + ins[0]
			for inst in ins: 
				result = result +   "%04d  | " % j + inst + "\n" 
				j = j+1
			result = result +  "---------------------------" + "\n"	

	result = result +  "*****************************************" + "\n"
	result = result +  "Opcode-count: " + `count` + "\n"
	result = result +  "Rungs: " + str(len(rungs)) + "\n"
	result = result +  "*****************************************" + "\n"
	count=0
	return result


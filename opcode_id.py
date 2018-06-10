import numpy
import MySQLdb
import numpy as np
import re
# Preparing data

op_codes = []

def match(opcodes,bytes):
	all_c = []
	ids = []
	fl = False
	for (opcode,byte) in zip(opcodes,bytes):	
		count = 0
		c = np.in1d(opcode,byte)
		for i in range(len(opcode)):
			if opcode[i] == 'xx':
				ids.append(i)				
		for Id in ids:
			c[Id] = True
		all_c.append([c])
	for c in all_c:
		if np.any(m == False for m in c):
			fl = True
	return fl	
def findOpcodes(string):
	result = ''	
	string = string[24:]	
	db = MySQLdb.connect(host="localhost", user="root", passwd="12345", db="modicon")
	cur = db.cursor()
	cur.execute("select opcode from op_codes")
	raw_ops = cur.fetchall()
	for row in raw_ops:
		op_codes.append(row[0].split(":"))
	bytes = string.split(":")
	flag=False
	try:
		for i in range(len(bytes)):
			if flag:
				i = i + length
			else:
				i = i - 1
			lhs = []
			rhs = []
			for opcode in op_codes:
				if bytes[i] == opcode[0]:
					lhs.append(opcode)
					rhs.append(bytes[i:i+len(opcode)])
					length = len(opcode)
					flag = match(lhs,rhs)
			if flag:
				result = result + bytes[i]
	except IndexError:
		pass	
	string = ''		
	return result
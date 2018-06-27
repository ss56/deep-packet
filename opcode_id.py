###########################


###########################
import numpy
import MySQLdb
import numpy as np
import re
# Preparing data
op_codes = []

def match(opcodes,bytes):
	result = ''
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
		if not False in c:	
			all_c= c
	if all_c ==[]:
		all_c = c
	result = `all_c` + '\n' + `opcode` +"\n" + `byte` + '\n'
	return 	result
def findOpcodes(string):
	result = ''
	done = []	
	string = string[24:]	
	db = MySQLdb.connect(host="localhost", user="root", passwd="12345", db="modicon")
	cur = db.cursor()
	cur.execute("select opcode from op_codes")
	raw_ops = cur.fetchall()
	for row in raw_ops:
		op_codes.append(row[0].split(":"))

	bytes = string.lower().split(":")
	flag=False
	try:
		for i in range(len(bytes)):	
			lhs = []
			rhs = []
			for opcode in op_codes:
				if bytes[i] == opcode[0]:
					lhs.append(opcode)
					rhs.append(bytes[i:i+len(opcode)])
					current_result = match(lhs,rhs)
					if not current_result in done:
						result = result + current_result
					done.append(current_result)
					
	except IndexError:
		pass	
	string = ''		
	return result

# To test this file	
#print findOpcodes("7C:0C:22:04:7C:0D:23:08:EF:CE:7E:0E:7C:1E:FD:E0:2D:7F:1A:10:0B:00:7C:0D:23:0A:CE:7E:01:00:7E:0E:7C:2E:FC:F6:72:AC:10:F2:75:AD:10:7F:1A:11:F6:70:10:11:FD:E1:2D:7F:1A:11:7F:1A:10:0B:01:7C:0D:23:08:EF:DE:7E:0E:7C:1E:FC:F6:72:AC:10:F2:75:AD:10:7F:1A:11:F6:70:18:11:FC:EA:72:01:00:7F:1A:11:02")
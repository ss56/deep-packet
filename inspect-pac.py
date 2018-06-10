import sys
import os,errno
import subprocess
import MySQLdb
import mapper
import opcode_id
from os import listdir
from os.path import isfile, join

essential = ['02','7c','2d','3d','78','7a']
folder = sys.argv[1]
onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
print onlyfiles
for fi in onlyfiles:
	print folder + "/" + fi
	result = ''
	cap1 = subprocess.check_output("tshark --disable-protocol opensafety -Y mbtcp -T fields -e modbus.data -r \"" + folder + "/" + fi + "\"", shell=True)
	cap = cap1.split('\n')

	db = MySQLdb.connect(host="localhost",  # host 
		                 user="root",       # username
		                 passwd="12345",    # password
		                 db="modicon")   	# name of the database

	cur = db.cursor() 
	cur.execute("select op_code,instruction,output from instructions")
	rows = cur.fetchall()


	for i in range(len(cap)):
#		print cap[i][3:5]
		if cap[i][3:5] == '29':
			#result = result +  "+++++++++++++ START of PACKET ++++++++++++++++"
			result = result + "packet number: "+ `i` + "\n" +cap[i] + "\n"
		
			result = result + mapper.map(cap[i]) + "\n"
			result = result + opcode_id.findOpcodes(cap[i]) + "\n"
		
				
			if "09:be:09:ff" in cap[i]:
				result = result + "metadata"	
			else:
				result = result +  "no"
			bytes = cap[i].split(':')
			my_dict_1 = {i:bytes.count(i) for i in bytes}	
			result = result +  "1-Gram" + "\n"
			result = result +  `my_dict_1` + "\n"
			done = []
			my_dict_2 = {}
			for j in range(len(bytes)-1):
				if bytes[j]+":"+bytes[j+1] not in done:
					my_dict_2[bytes[j]+":"+bytes[j+1]] = cap[i].count(bytes[j]+":"+bytes[j+1])
					done.append(bytes[j]+":"+bytes[j+1])
			result = result +  "\n 2-Gram" + "\n"
			result = result +  `my_dict_2` + "\n"
			done = []
			my_dict_3 = {}
			j=0
			for j in range(len(bytes)-2):
				if bytes[j]+":"+bytes[j+1]+":"+bytes[j+2] not in done:
					my_dict_3[bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]] = cap[i].count(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2])
					done.append(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2])
			result = result +  "\n 3-Gram" 	 + "\n"
			result = result +  `my_dict_3` + "\n"
			done = []
			my_dict_4 = {}
			j=0
			for j in range(len(bytes)-3):
				if bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3] not in done:
					my_dict_4[bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]] = cap[i].count(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3])
					done.append(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3])
			result = result +  "\n 4-Gram" + "\n" 	
			result = result +  `my_dict_4` + "\n"
			done = []
			my_dict_5 = {}
			j=0
			for j in range(len(bytes)-4):
				if bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4] not in done:
					my_dict_5[bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4]] = cap[i].count(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4])
					done.append(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4])
			result = result +  "\n 5-Gram" + "\n" 	
			result = result +  `my_dict_5` + "\n"
			done = []
			my_dict_6 = {}
			j=0
			for j in range(len(bytes)-5):
				if bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4]+":"+bytes[j+5] not in done:
					my_dict_6[bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4]+":"+bytes[j+5]] = cap[i].count(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4]+":"+bytes[j+5])
					done.append(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4]+":"+bytes[j+5])
			result = result +  "\n 6-Gram" + "\n" 	
			result = result +  `my_dict_6` + "\n"
	
			#result = result +  done
			result = result +  "+++++++++++++++ END of PACKET ++++++++++++++++++" + "\n"
		fp = open("outputs/" + fi +".txt","a")
		fp.write(result)
		fp.close()
	
		
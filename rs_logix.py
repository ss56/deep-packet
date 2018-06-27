import pccc_wp_extractor as pw
import ConfigParser
import sys

extractor = pw.wp_extractor()

class rs_logix():
	def __init__(self):
		self.opcode = ''
		self.rungs = 0
		self.decompiled = ''
		self.all_instructions = ''
		self.instruc_Settings = ConfigParser.RawConfigParser("")
	
	def opcode_identification(self, strn):
#		print strn
		self.instruc_Settings.read('instructionsConfig.ini')
		i=0
		for s in strn:
			skip = -1
			self.all_instructions = self.all_instructions + "\n Packet Number: " + `i` +'\n'
			self.all_instructions = self.all_instructions + s + '\n'
			for j in range(len(s)-3):
				find = ''.join(s[j:j+4])
				#find1 = hexcode[2:4] + hexcode[0:2]
				if j > skip:
					try:
						self.all_instructions = self.all_instructions + self.instruc_Settings.get(find,'inscode')
						size = self.instruc_Settings.getint(find,'size')
						skip = j+(size * 2) - 4
					except:
						self.all_instructions = self.all_instructions + s[j]
			self.all_instructions = self.all_instructions + '\n'
			i=i+1
						
def main():
    global extractor
   	
    extractor.extract_from_pcap(sys.argv[1])
    rs = rs_logix()
    #print extractor.wp_list
    
    rs.opcode_identification(extractor.pccc_list)
    
    print rs.all_instructions
    #extractor.print_wp()

if __name__ == '__main__':
    main()
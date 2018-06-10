# Extract payload of write request messsages of the PCCC protocol

import py
import sys
import pyshark



class wp_extractor():
    def __init__(self):
        # pccc message
        self.pccc_list = []

        # payload of write request message of the PCCC protocol
        self.wp_list = []
        
        self.all = []
        self.i = 0

    def extract_from_pcap(self, pcapfile):
        cap = pyshark.FileCapture(pcapfile)
		#cap.set_debug() 	
        #extract pccc messages and wp (write payload)
        cap.apply_on_packets(self.extract_pccc_wp)
#        print "end"
        
    def extract_pccc_wp(self, pkt):
    	
        try:
            try:
                # pccc is directly encapsulated in ENIP
                cpfdata = pkt.layers[3].cpf_data
                alternatefield = str(cpfdata.alternate_fields)
                pccc = alternatefield[28:].split(">]")[0].split(":")
                
               
            except:
                # pccc is encapsulated in CIP
                cipdata = enip_lay[5].cip_data
                pccc = cipdata.split(":")[7:]
                
            # Write request
            if pccc[4] == "aa":    
                if pccc[9] == "ff": # the size of sub-element field is 3 bytes
                    wp = pccc[12:]
                else:               # the size of sub-element field is 1 byte
                    wp = pccc[10:]           
            self.wp_list.append("".join(wp))
            self.pccc_list.append("".join(pccc))


        except:
            pass
            
    def print_pccc_msgs(self):
        for pccc in self.pccc_list:
            print pccc

    def print_wp(self):
        for wp in self.wp_list:
            print wp
        

def main():
    if len(sys.argv) < 2:
        print "Usage: python pccc_wp_extractor.py pcapfile"
        sys.exit()

    extractor = wp_extractor()
    extractor.extract_from_pcap(sys.argv[1])
    #print sys.argv[1]
    #print extractor.wp_list
    
#    decompiler for each wp element
    
#    extractor.print_pccc_msgs()
    #extractor.print_wp()

if __name__ == '__main__':
    main()

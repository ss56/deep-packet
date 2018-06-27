# Maintaining shadow memory of M221 PLC

from scapy.all import *
import sys, os
import argparse

# transaction id(2) + protocol identifier(2) + length(2) + unit identifier(1) (Not include function code byte)
MODBUS_HDR_LEN = 7

class M221_shadow_memory():
    def __init__(self):
        self.mem = bytearray('\x00') * 65536    # Memory space size = 0xffff (65536)
    
    def process_pkts(self, pcapFile):
        all_pkts = rdpcap(pcapFile)
        modbus_pkts = (pkt for pkt in all_pkts if
            TCP in pkt and (pkt[TCP].dport == 502) and len(pkt[TCP].payload) > MODBUS_HDR_LEN)

        for pkt in modbus_pkts:
            modbus = bytes(pkt[TCP].payload)
            if modbus[MODBUS_HDR_LEN] != '\x5a':    # 0x5a is the function code indicating it is M221
                continue
            m221_msg = modbus[MODBUS_HDR_LEN+1:]

            # write request:
            if m221_msg[1] == '\x29':
                addr = struct.unpack("<H", m221_msg[2:4])[0]
                addr_type = m221_msg[4:6]
                size = struct.unpack("<H", m221_msg[6:8])[0]
                data = m221_msg[8:]   

                self.mem[addr:addr+size] = data

            # Scan shadow memory
            self.scan_memory()

    def scan_memory(self):
        # Apply various detection method here
        # pass
        shadow_mapper.map()

    def print_mem(self):
        f = open("shadow_mem", "w")
        f.write(self.mem)
     

def main():
    parser = argparse.ArgumentParser(description="Shadow Memory Map of M221 PLC")
    parser.add_argument("pcapFile", help="pcap file")

    args = parser.parse_args()

    shadow_mem = M221_shadow_memory()
    shadow_mem.process_pkts(args.pcapFile)
    #shadow_mem.print_mem()

if __name__ == '__main__':
    main()

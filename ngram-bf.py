from pybloomfilter import BloomFilter
import subprocess
from os import listdir
from os.path import isfile, join

class bloomFilter():
	# Create an empty bloom filter
	def create_new_bf(self, capacity, error_rate, filename):
		self.bf = BloomFilter(capacity, error_rate, filename)

	# Open an existing bloom filter
	def open_bf(self, filename):
		self.bf = BloomFilter.open(filename)

	def add_item(self, item):
		self.bf.add(item)

	def check_membership(self, item):
		return item in self.bf
	
	def clear_all(self):
		self.bf.clear_all()

def main():
	# Create an empty bloom filter
	grams_bf = bloomFilter()
	grams_bf.create_new_bf(1000000, 0.01, "1gram.bf")
	grams_bf2 = bloomFilter()
	grams_bf2.create_new_bf(1000000, 0.01, "2gram.bf")
	grams_bf3 = bloomFilter()
	grams_bf3.create_new_bf(1000000, 0.01, "3gram.bf")
	grams_bf4 = bloomFilter()
	grams_bf4.create_new_bf(1000000, 0.01, "4gram.bf")
	grams_bf5 = bloomFilter()
	grams_bf5.create_new_bf(1000000, 0.01, "5gram.bf")
	grams_bf6 = bloomFilter()
	grams_bf6.create_new_bf(1000000, 0.01, "6gram.bf")
	grams_bf.clear_all()
	folder = "Final"
	onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
	print onlyfiles
	for fi in onlyfiles:
		print folder + "/" + fi
		cap1 = subprocess.check_output("tshark --disable-protocol opensafety -Y mbtcp -T fields -e modbus.data -r \"" + folder + "/" + fi + "\"", shell=True)
		#cap1 = cap1[cap1.find("09:be:09:ff"):cap1.find("02")]
		cap = cap1.split('\n')
		for i in range(len(cap)):
			if "09:be:09:ff" in cap[i]:
				cl = cap[i+2]
				bytes = cl[24:].split(':')
				my_dict_1 = {i:bytes.count(i) for i in bytes}	
				for key in my_dict_1.keys():
					grams_bf.add_item(key)
				done = []
				my_dict_2 = {}
				for j in range(len(bytes)-1):
					if bytes[j]+":"+bytes[j+1] not in done:
						grams_bf2.add_item(bytes[j]+":"+bytes[j+1])
						done.append(bytes[j]+":"+bytes[j+1])
				done = []
				my_dict_3 = {}
				j=0
				for j in range(len(bytes)-2):
					if bytes[j]+":"+bytes[j+1]+":"+bytes[j+2] not in done:
						grams_bf3.add_item(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2])
						done.append(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2])
				done = []
				my_dict_4 = {}
				j=0
				for j in range(len(bytes)-3):
					if bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3] not in done:
						grams_bf4.add_item(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3])
						done.append(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3])
				done = []
				my_dict_5 = {}
				j=0
				for j in range(len(bytes)-4):
					if bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4] not in done:
						grams_bf5.add_item(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4])
						done.append(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4])
				done = []
				my_dict_6 = {}
				j=0
				for j in range(len(bytes)-5):
					if bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4]+":"+bytes[j+5] not in done:
						grams_bf6.add_item(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4]+":"+bytes[j+5])
						done.append(bytes[j]+":"+bytes[j+1]+":"+bytes[j+2]+":"+bytes[j+3]+":"+bytes[j+4]+":"+bytes[j+5])
					
	# To test the membership
	'''grams_bf1 = bloomFilter()
	grams_bf1.open_bf("1gram.bf")
	
	print grams_bf1.check_membership("7c")
	
	grams_bf2 = bloomFilter()
	grams_bf2.open_bf("2gram.bf")
	
	print grams_bf2.check_membership("7c:0c")'''
	

if __name__ == '__main__':
	main()
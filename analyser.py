import ngram_bf
import pybloomfield as bf


def s_to_dict(s):
	s = string.replace("{" ,"");
	finalstring = s.replace("}" , "");

	#Splitting the string based on , we get key value pairs
	list = finalstring.split(",")

	dict ={}
	for i in list:
		#Get Key Value pairs separately to store in dictionary
		keyvalue = i.split(":")

		#Replacing the single quotes in the leading.
		m= keyvalue[0].strip('\'')
		m = m.replace("\"", "")
		dict[m] = keyvalue[1].strip('"\'')

	return dict


def map_n1(pkt_id, pkt, ngram):
	ngram_dict = s_to_dict(ngram)
	pritn ngram
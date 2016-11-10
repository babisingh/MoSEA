'''
script to create .bed files from the alternative spliced events.
input: create_bedfiles_from_suppa_events.py --ifile <input file> --event <event-type> --ext <length-extension> --ofile <output_file>
    contains columns: 
    	[1] cancer : BRCA
    	[2] event : VPS13A|23230;SE:chr9:79897190-79898271:79898387-79898463:+
    	[3] nmean : 0.631531374927508
    	[4] tmean : 0.564846366844214
    	[5] nmedian : 0.70777035404
    	[6] tmedian : 0.625395956035
    	[7] meandiff : -0.0666850080832945
    	[8] mediandiff : -0.082374398005
    	[9] wilcox : 0.0687984924239605
    	[10] wilcoxa : 0.182503207881309
					

output file: create bed files by spliting 'event' columns
	should contain columns: 
		[1] chr 
		[2] start
		[3] end
		[4] name(event_id [col : 2])
		[5] score(mediandiff [col:8])
		[6] strand


'''

import sys, getopt
import os

#get args
def main():
	
	input_file = ''
	event_type = ''
	ext_len = ''
	output_file = ''
	
	try:
		opts, args = getopt.getopt(sys.argv[1:],"h:iel:o:",["ifile=","event=","ext=","ofile="])
	except getopt.GetoptError:
		print 'create_bedfiles_from_suppa_events.py --ifile <input file> --event <event-type>\
				--ext <length-extension> --ofile <output file>'
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print 'create_bedfiles_from_suppa_events.py --ifile <inputfile> --event <event-type> --ext <extension length> --ofile <outputfile>'
			#eg.:create_bedfiles_from_suppa_events.py --ifile ~/tmp/brca_control.dpsi --event SE --cancer brca --ofile ~/tmp/brca_control.bed
			sys.exit()
		elif opt in ("--ifile"):
			input_file = arg
		elif opt in ("--event"):
			event_type = arg
		elif opt in ("--ext"):
			ext_len = int(arg)
		elif opt in ("--ofile"):
			output_file = arg
		else:
			print("please Enter correct option, use -h for help")
			sys.exit()

	filename = os.path.basename(input_file) #basename
	print("\n\nStart for se_type: {} \t file: {}".format(event_type,filename))
	print("Suppa events to Bed file conversion:")

	with open(output_file, "w"): pass
	with open(input_file) as f:
		#next(f) #skip for header
		for line in f:
			line = line.rstrip()
			len_line = len(line.split('\t'))

			if len_line > 1:
				event, mediandiff, wilcoxa = _split_line(line)
			else:
				event = line
				mediandiff = 0

			call_event_func = {"SE": fun_SE_bedfile, 
				"MX": fun_MX_bedfile,
				"RI": fun_RI_bedfile,
				"A5": fun_A5_bedfile,
				"A3": fun_A3_bedfile,
				"AF": fun_AF_bedfile,
				"AL": fun_AL_bedfile
				}

			call_event_func[event_type.upper()](input_file, output_file, ext_len, event, mediandiff)

	_print_out_msg(output_file)
	f.close()

def _split_line(row):
	row = row.split('\t')
	return row[1], row[7], row[9]

def _print_out_msg(out_file):
	print("File created: {}\n".format(out_file))


def fun_SE_bedfile(in_file, out_file, ext_len, event, mediandiff):
	'''
	ref: see Fig.2 suppa documentaion of SE e1 & s1..descriptions
	https://bitbucket.org/regulatorygenomicsupf/suppa
	Example event id: (e1-s2:e2-s3)
	CTCFL|140690;SE:chr20:56064269-56073610:56073757-56078492:-
	'''
	fo = open(out_file, "a")

	ev_all = event.split(';')
	ev_coord = ev_all[1]

	ev_all = ev_coord.split(':')

	ev_type = ev_all[0]
	ev_chr = ev_all[1]
	ev_e1_s2 = ev_all[2] #intron1_start(e1) to exon_start(s2)
	ev_e2_s3 = ev_all[3] #exon_end(e2) to intron2_end(s3)
	ev_strand = ev_all[4] 


	ev_e1_s2 = ev_e1_s2.split('-')
	#take whole intron
	#intron1_start_e1 = ev_e1_s2[0] 
	exon_start_s2 = ev_e1_s2[1]  
	ev_e2_s3 = ev_e2_s3.split('-')
	exon_end_e2 = ev_e2_s3[0]  
	#take whole intron 
	intron2_end_s3 = ev_e2_s3[1] 

	up = int(exon_start_s2) - ext_len   ##pos_start = int(exon_start_s2) -
	down = int(exon_end_e2) + ext_len

	#subtract first base to adjust 0-based position for UCSC compatible bed files
	
	if ev_strand == '+':
		exon_start_s2 = int(exon_start_s2) - 1
		exon_end_e2 = int(exon_end_e2) + 1
		var_region1 = "up"
		var_region2 = "down"
	else:
		#up = int(up) - 1
		exon_end_e2 = int(exon_end_e2) + 1
		exon_start_s2 = int(exon_start_s2) - 1
		var_region1 = "down"
		var_region2 = "up"


	event_1 = event + ";" + var_region1
	event_E = event + ";E" 
	event_2 = event + ";" + var_region2

	fo.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(ev_chr, up,
		exon_start_s2, event_1, mediandiff, ev_strand))
	fo.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(ev_chr, exon_start_s2,
		exon_end_e2, event_E, mediandiff, ev_strand))
	fo.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(ev_chr, exon_end_e2,
		down, event_2, mediandiff, ev_strand))



	       		
def fun_MX_bedfile(in_file, out_file, len_ext, event, mediandiff):
	'''
	ref: see Fig.2 suppa documentaion of MX e1 & s1..descriptions
	#https://bitbucket.org/regulatorygenomicsupf/suppa
	#Example event id: (e1-s2:e2-s4:e1-s3:e3-s4)
	#SMPD4|55627;MX:chr2:130922018-130925031:130925163-130934127:130922018-130932487:130932573-130934127:-
	#A2BP1|54715;MX:chr16:7703949-7714931:7714970-7726776:7703949-7721559:7721601-7726776:+
	'''
	fo = open(out_file, "a")

	ev_all = event.split(';')	
	ev_coord = ev_all[1]

	ev_all = ev_coord.split(':')
	ev_type = ev_all[0]
	ev_chr = ev_all[1]
	ev_strand = ev_all[6]

	ev_e1_s2 = ev_all[2]
	ev_e2_s4 = ev_all[3]
	ev_e1_s3 = ev_all[4]
	ev_e3_s4 = ev_all[5]

			   
	ev_e1_s2 = ev_e1_s2.split('-') 
	e1 = int(ev_e1_s2[0])
	s2 = int(ev_e1_s2[1])
			  
	ev_e2_s4 = ev_e2_s4.split('-')
	e2 = int(ev_e2_s4[0])
	s4 = int(ev_e2_s4[1])
			  
	ev_e1_s3 = ev_e1_s3.split('-')
	e1 = int(ev_e1_s3[0])
	s3 = int(ev_e1_s3[1])
			  
	ev_e3_s4 = ev_e3_s4.split('-')
	e3 = int(ev_e3_s4[0])
	s4 = int(ev_e3_s4[1])


	#event_mx1 = event + ";MX1"
	#event_mx2 = event + ";MX2"
	if(ev_strand == '+'):
		s2a = int(s2) - 1 
		e2a = e2 + 1
		V1 = ("{}\t{}".format(s2 - len_ext, s2a)) 			#(int(s2) - len_ext) + "\t" + s2a
		V2 = ("{}\t{}".format(s2, e2)) 						#s2a + "\t" + e2
		V3 = ("{}\t{}".format(e2a, e2 + len_ext))  			#e2 + "\t" + (int(e2)+ len_ext)

		s3a = int(s3) - 1
		e3a = e3 + 1
		V4 = ("{}\t{}".format(s3a - len_ext, s3a))
		V5 = ("{}\t{}".format(s3a, e3))
		V6 = ("{}\t{}".format(e3a, e3 + len_ext))

	elif(ev_strand == '-'):
		s3a = int(s3) + 1
		e3a = int(e3) + 1
		V1 = ("{}\t{}".format(e3a, e3 + len_ext))
		V2 = ("{}\t{}".format(s3, e3))
		V3 = ("{}\t{}".format(s3a - len_ext, s3))

		s2a = int(s2) - 1
		e2a = e2 + 1
		V4 = ("{}\t{}".format(e2a, e2 + len_ext))
		V5 = ("{}\t{}".format(s2, e2))
		V6 = ("{}\t{}".format(s2 - len_ext, s2a))
	
	else:
		print("No strand information in file, for event: {}".format(event))
		sys.exit()

	#if the intron-length between two center exons (e2 and s3) is > 200
	if(int(s3) - int(e2) >= 200):	
		fo.write("{}\t{}\t{};V1\t{}\t{}\n".format(ev_chr,V1,event,mediandiff,ev_strand)) 
		fo.write("{}\t{}\t{};V2\t{}\t{}\n".format(ev_chr,V2,event,mediandiff,ev_strand))
		fo.write("{}\t{}\t{};V3\t{}\t{}\n".format(ev_chr,V3,event,mediandiff,ev_strand))
		fo.write("{}\t{}\t{};V4\t{}\t{}\n".format(ev_chr,V4,event,mediandiff,ev_strand))
		fo.write("{}\t{}\t{};V5\t{}\t{}\n".format(ev_chr,V5,event,mediandiff,ev_strand))
		fo.write("{}\t{}\t{};V6\t{}\t{}\n".format(ev_chr,V6,event,mediandiff,ev_strand)) 

	fo.close()



def fun_RI_bedfile(in_file, out_file, len_ext, event, mediandiff):
	'''
	##ref: see Fig.2 suppa documentaion of RI e1 & s1..descriptions
	#https://bitbucket.org/regulatorygenomicsupf/suppa
	#Example event id: 
	#TIAL1|7073;RI:chr10:121336123:121336262-121336592:121336715:-
	'''
	fo = open(out_file, "a")
	
	ev_all = event.split(';')	
	ev_coord = ev_all[1]

	ev_all = ev_coord.split(':')
	ev_type = ev_all[0]
	ev_chr = ev_all[1]
	s1 = int(ev_all[2])
	e1_s2 = ev_all[3]
	e2 = int(ev_all[4])
	ev_strand = ev_all[5]

	e1_s2 = e1_s2.split('-') 
	e1 = int(e1_s2[0])
	s2 = int(e1_s2[1])

	if(ev_strand == '+'):	
		V1 = ("{}\t{}".format(e1 - len_ext, e1)) 	#(int(e1) - len_ext) + "\t" + e1 #up exon
		V2 = ("{}\t{}".format(e1, s2)) 			 #e1 + "\t" + s2 				  #intron
		V3 = ("{}\t{}".format(s2, s2 + len_ext)) 	#s2 + "\t" + (int(s2) + len_ext) #down

	elif(ev_strand == '-'):
		s2 = int(s2) - 1 #for 0-based correction
		V1 = ("{}\t{}".format(s2, s2 + len_ext)) 	#s2 + "\t" + (int(s2) + len_ext)   #up exon
		V2 = ("{}\t{}".format(e1, s2)) 			 #e1 + "\t" + s2 				    #intron
		V3 = ("{}\t{}".format(e1 - len_ext, e1)) 	#(int(e1) - len_ext) + "\t" + e1   #down

	else:
		print("No strand information in file, for event: {}".format(event))
		sys.exit()

	if( (s2 - e1) >=10 and (s2 - e1) <= 1000):
		fo.write("{}\t{}\t{};V1\t{}\t{}\n".format(ev_chr, V1, event,
			mediandiff, ev_strand)) 
		fo.write("{}\t{}\t{};V2\t{}\t{}\n".format(ev_chr, V2, event,
			mediandiff, ev_strand)) 
		fo.write("{}\t{}\t{};V3\t{}\t{}\n".format(ev_chr, V3, event,
			mediandiff, ev_strand)) 

	else:
		return

	fo.close()


def fun_A5_bedfile(in_file, out_file, len_ext, event, mediandiff):
	'''
	##ref: see Fig.2 suppa documentaion of A5 e1,e2 & s3..descriptions
	#https://bitbucket.org/regulatorygenomicsupf/suppa
	#Example event id: (e2-s3:e1-s3)
	#CUL7|9820;A5:chr6:43020534-43021360:43020534-43021449:-
	'''
	fo = open(out_file, "a")

	ev_all = event.split(';')	
	ev_coord = ev_all[1]

	ev_all = ev_coord.split(':')
	ev_type = ev_all[0]
	ev_chr = ev_all[1]
	ev_strand = ev_all[4]

	if(ev_strand=="-"):
		s3_e1 = ev_all[2]
		s3_e2 = ev_all[3]
		s3_e1 = s3_e1.split('-')
		s3 = int(s3_e1[0])
		e1 = int(s3_e1[1])

		s3_e2 = s3_e2.split('-')
		e2 = int(s3_e2[1]) - 1 #correct for 0-base

		V1 = ("{}\t{}".format(e2 - len_ext, e2)) #(e2 - len_ext) + "\t" + e2
		V2 = ("{}\t{}".format(e2, e2 + len_ext)) #e2 + "\t" + (e2 + len_ext)

	elif(ev_strand=="+"):
		e2_s3 = ev_all[2]
		e1_s3 = ev_all[3]
		e2_s3 = e2_s3.split('-')
		e2 = int(e2_s3[0])
		s3 = int(e2_s3[1])

		e1_s3 = e1_s3.split('-')
		e1 = int(e1_s3[0])

		V1 = ("{}\t{}".format(e1 - len_ext, e1))  #(e1 - len_ext) + "\t" + e1
		V2 = ("{}\t{}".format(e1, e1 + len_ext))  #e1 + "\t" + (e1 + len_ext)

	else:
		print("No strand information in file, for event: {}".format(event))
		sys.exit()

	fo.write("{}\t{}\t{};V1\t{}\t{}\n".format(ev_chr, V1, event,
		mediandiff, ev_strand)) 
	fo.write("{}\t{}\t{};V2\t{}\t{}\n".format(ev_chr, V2, event,
		mediandiff, ev_strand)) 

	fo.close()



def fun_A3_bedfile(in_file, out_file, len_ext, event, mediandiff):
	'''
	##ref: see Fig.2 suppa documentaion of A3 e1 & s1..descriptions
	#https://bitbucket.org/regulatorygenomicsupf/suppa
	#Example event id: (e1-s2:e1-s3)
	#ABCG2|9429;A3:chr4:89016761-89018605:89016751-89018605:-
	-ve strand: (s2-e1:s3-e1)
	'''
	fo = open(out_file, "a")

	ev_all = event.split(';')	
	ev_coord = ev_all[1]

	ev_all = ev_coord.split(':')
	ev_type = ev_all[0]
	ev_chr = ev_all[1]
	ev_strand = ev_all[4]

	if ev_strand == '-':
		#eg.ABCG2|9429;A3:chr4:89016761-89018605:89016751-89018605:-   
		ev_s2_e1 = ev_all[2]
		ev_s2_e1 = ev_s2_e1.split('-')
		s2 = int(ev_s2_e1[0])	
		e1 = int(ev_s2_e1[1])	

		ev_s3_e1 = ev_all[3]
		ev_s3_e1 = ev_s3_e1.split('-')
		s3 = int(ev_s3_e1[0])

		#s3a = s3 - 1
		V1 = ("{}\t{}".format(s3, (s3 + len_ext)))
		V2 = ("{}\t{}".format((s3 - len_ext), s3)) 

	elif ev_strand == '+' :  
		#eg. A2BP1|54715;A3:chr16:7568391-7629779:7568391-7629782:+ 
		ev_e1_s2 = ev_all[2]
		ev_e1_s2 = ev_e1_s2.split('-')
		e1 = ev_e1_s2[0] 
		s2 = int(ev_e1_s2[1]) 

		ev_e1_s3 = ev_all[3]
		ev_e1_s3 = ev_e1_s3.split('-')
		s3 = int(ev_e1_s3[1]) 

		V1 = ("{}\t{}".format((s3 - len_ext), s3))
		V2 = ("{}\t{}".format(s3,(s3 + len_ext)))

	else:
		print("No strand information in file, for event: {}".format(event))
		sys.exit()

	fo.write("{}\t{}\t{};V1\t{}\t{}\n".format(ev_chr, V1, event,
		mediandiff, ev_strand)) 
	fo.write("{}\t{}\t{};V2\t{}\t{}\n".format(ev_chr, V2, event,
		mediandiff, ev_strand)) 


	fo.close()


def fun_AF_bedfile(in_file, out_file, len_ext, event, mediandiff):
	'''
	##ref: see Fig.2 suppa documentaion of A3 e1 & s1..descriptions
	#https://bitbucket.org/regulatorygenomicsupf/suppa
	ABAT|18;AF:chr16:8768444:8768568-8829556:8814573:8814791-8829556:+
	#Example event id: (s1:e1-s3:s2:e2-s3)
	AAA1|404744;AF:chr7:34768428-34797686:34797884:34768428-34800724:34800803:-
	-ve strand: (s3-e2:s2:s3-e1:s1)

	[==V1==]----V2---|--------------------------------[===] AF (+strand)
						[==V3==]----V4-----|----------[===] AF
	'''
	fo = open(out_file, "a")

	ev_all = event.split(';')	
	ev_coord = ev_all[1]

	ev_all = ev_coord.split(':')
	ev_type = ev_all[0]
	ev_chr = ev_all[1]
	ev_strand = ev_all[6]

	if ev_strand == '-':
		#eg.AF:chr7:34768428-34797686:34797884:34768428-34800724:34800803:-
		#(s3-e2:s2:s3-e1:s1)

		ev_s3_e2 = ev_all[2]
		s2 = int(ev_all[3])
		ev_s3_e1 = ev_all[4]
		s1 = int(ev_all[5])

		s3, e2 = ev_s3_e2.split('-')
		s31 = int(s3)
		e2 = int(e2)

		s3, e1 = ev_s3_e1.split('-')
		s32 = int(s3)
		e1 = int(e1)

		if s31 != s32:
			print("Wrong event id. please correct the event: {}".format(event))
			sys.exit()
		
		if (e1 - s2) > 10:
			V1 = ("{}\t{}".format(e1, s1))
			V2 = ("{}\t{}".format((e1 - len_ext), e1-1)) 
			V3 = ("{}\t{}".format(e2-1, s2)) 
			V4 = ("{}\t{}".format(e2 -len_ext, e2-1)) 
		else:
			return

	elif ev_strand == '+' :  
		#eg. A2BP1|54715;A3:chr16:7568391-7629779:7568391-7629782:+ 
		#(s1:e1-s3:s2:e2-s3)

		s1 = int(ev_all[2])
		ev_e1_s3 = ev_all[3]
		s2 = int(ev_all[4])
		ev_e2_s3 = ev_all[5]

		e1, s3 = ev_e1_s3.split('-')
		e1 = int(e1)
		s31 = int(s3)
		e2, s3 = ev_e2_s3.split('-')
		e2 = int(e2)
		s32 = int(s3)

		if s31 != s32:
			print("Wrong event id. please correct the event: {}".format(event))
			sys.exit()

		if (s2 - e1) > 10:
			V1 = ("{}\t{}".format(s1, e1))
			V2 = ("{}\t{}".format(e1 + 1, (e1 + len_ext)))
			V3 = ("{}\t{}".format(s2, e2))
			V4 = ("{}\t{}".format(e1+1, (e1 + len_ext)))
		else:
			return

	else:
		print("No strand information in file, for event: {}".format(event))
		sys.exit()

	fo.write("{}\t{}\t{};V1\t{}\t{}\n".format(ev_chr, V1, event,
		mediandiff, ev_strand)) 
	fo.write("{}\t{}\t{};V2\t{}\t{}\n".format(ev_chr, V2, event,
		mediandiff, ev_strand)) 
	fo.write("{}\t{}\t{};V3\t{}\t{}\n".format(ev_chr, V3, event,
		mediandiff, ev_strand)) 
	fo.write("{}\t{}\t{};V4\t{}\t{}\n".format(ev_chr, V4, event,
		mediandiff, ev_strand)) 

	fo.close()

def fun_AL_bedfile(in_file, out_file, len_ext, event, mediandiff):
	'''
	##ref: see Fig.2 suppa documentaion of A3 e1 & s1..descriptions
	#https://bitbucket.org/regulatorygenomicsupf/suppa
	ABCB5|340273;AL:chr7:20698299-20698689:20700016:20698299-20706382:20707187:+
	#Example event id: (e1-s3:e3:e1-s2:e2)
	ABCA11P|79963:ZNF721|170960;AL:chr4:419224:420762-466364:433781:438221-466364:-
	-ve strand: (e3:s3-e1:e2:s2-e1)

	[===]---------------------------|------V2----[==V1==] AL (+ve strand)
	[===]--------|-----V4-----[==V3==]

	[==V1==]----V2---|--------------------------------[===] AL (-strand)
						[==V3==]----V4-----|----------[===] AL
	'''
	fo = open(out_file, "a")

	ev_all = event.split(';')	
	ev_coord = ev_all[1]

	ev_all = ev_coord.split(':')
	ev_type = ev_all[0]
	ev_chr = ev_all[1]
	ev_strand = ev_all[6]

	if ev_strand == '-':
		#eg.AL:chr4:419224:420762-466364:433781:438221-466364:-
		#(e3:s3-e1:e2:s2-e1)

		e3 = int(ev_all[2])
		ev_s3_e1 = ev_all[3]
		e2 = int(ev_all[4])
		ev_s2_e1 = ev_all[5]

		s3, e1 = ev_s3_e1.split('-')
		s3 = int(s3)
		e11 = int(e1)

		s2, e1 = ev_s2_e1.split('-')
		s2 = int(s2)
		e12 = int(e1)

		if e11 != e12:
			print("Wrong event id. please correct the event: {}".format(event))
			sys.exit()
		
		if (e2 - s3) > 10:
			V1 = ("{}\t{}".format(e3, s3))
			V2 = ("{}\t{}".format(s3+1, (s3 + len_ext))) 
			V3 = ("{}\t{}".format(e2, s2)) 
			V4 = ("{}\t{}".format(s2+1, s2 + len_ext)) 
		else:
			return

	elif ev_strand == '+' :  
		#eg. AL:chr7:20698299-20698689:20700016:20698299-20706382:20707187:+
		#(e1-s3:e3:e1-s2:e2)

		ev_e1_s3 = ev_all[2]
		e3 = int(ev_all[3])
		ev_e1_s2 = ev_all[4]
		e2 = int(ev_all[5])

		e1, s3 = ev_e1_s3.split('-')
		e11 = int(e1)
		s3 = int(s3)
		e1, s2 = ev_e1_s2.split('-')
		e12 = int(e1)
		s2 = int(s2)

		if e11 != e12:
			print("Wrong event id. please correct the event: {}".format(event))
			sys.exit()

		if (e2 - s3) > 10:
			V1 = ("{}\t{}".format(s3, e3))
			V2 = ("{}\t{}".format(s3- len_ext, s3-1))
			V3 = ("{}\t{}".format(s2, e2))
			V4 = ("{}\t{}".format(s2 - len_ext, s2-1))
		else:
			return

	else:
		print("No strand information in file, for event: {}".format(event))
		sys.exit()

	fo.write("{}\t{}\t{};V1\t{}\t{}\n".format(ev_chr, V1, event,
		mediandiff, ev_strand)) 
	fo.write("{}\t{}\t{};V2\t{}\t{}\n".format(ev_chr, V2, event,
		mediandiff, ev_strand)) 
	fo.write("{}\t{}\t{};V3\t{}\t{}\n".format(ev_chr, V3, event,
		mediandiff, ev_strand)) 
	fo.write("{}\t{}\t{};V4\t{}\t{}\n".format(ev_chr, V4, event,
		mediandiff, ev_strand)) 

	fo.close()


if __name__ == "__main__":
    main()



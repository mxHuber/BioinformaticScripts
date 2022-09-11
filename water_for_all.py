import os
import sys
import time
from os.path import exists

# get starting time of program 
program_start_time = time.time()

# checks if everything is as it should be
if not len(sys.argv) == 4:
	print("Bad input. Command is: python get_het_vcf.py [GAP_OPEN_PENALTY] [GAP_EXTEND_PENALTY] [TXT WITH NAMES]")
	exit()

base_path = "/vol/storage/pipeline/"
gap_open_penalty = sys.argv[1]
gap_extend_penalty = sys.argv[2]

names_txt = open(sys.argv[3])
lines = names_txt.readlines()
names_txt.close()

names = []

# get all the names
for i in range(len(lines)):
	# name and remove newline character
	if (i % 4 == 0):
		names.append(lines[i][:-1])

print("Found " + str(len(names)) + " species names")

for i in range(len(names)):
	if not os.path.exists(base_path + names[i] + "/mito/"):
		print("No mito folder found for " + names[i])
		continue

	if os.path.exists(base_path + names[i] + "/mito/waterO" + gap_open_penalty + "E" + gap_extend_penalty + ".water"):
		print("The file waterO" + gap_open_penalty + "E" + gap_extend_penalty + ".water already exists for " + names[i])
		continue

	current_path = base_path + names[i] + "/mito/"
	asequence = current_path + "doubled.fasta "
	bsequence = current_path + "sequence.fasta "
	gap_open = "-gapopen " + gap_open_penalty + " "
	gap_extend = "-gapextend " + gap_extend_penalty + " "
	out_file = "-outfile " + current_path +"waterO" + gap_open_penalty + "E" + gap_extend_penalty + ".water"
	os.system("water " + asequence + bsequence + gap_open + gap_extend + out_file)

print("Finished! It took " + str((time.time() - program_start_time) / 60) + " minutes to run.")
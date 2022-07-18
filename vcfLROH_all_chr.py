import os
import sys
import time
from prettytable import PrettyTable

# example
# python /vol/storage/ba/scripts/vcfLROH_all_chr.py /vol/storage/prmd/secondTry/output.vcf /vol/storage/prmd/secondTry/refGenome/GCA_000738735.6_ASM73873v6_genomic.fna.fai 

# get starting time of program
program_start_time = time.time()

if not len(sys.argv) == 3:
	print("Please provide the path to the .vcf file and the path to the .fai index file")
	exit()

# .vcf file path
file_path = sys.argv[1]
# index file path
index_path = sys.argv[2]
# sys.argv[0] is the command itself

# first, go over index file of reference genome and extract chromosome names and number of base pairs
print("Extracting chromosome names...\n")
index_data = open(index_path)
index_lines = index_data.readlines()
index_data.close()
chr_names = []
base_pairs = []

# split lines to get chromosome names and number of base pairs, for all chromosomes
for i in range(len(index_lines)):
	splitted = index_lines[i].split("\t")
	chr_names.append(splitted[0])
	base_pairs.append(splitted[1])
	
# print(chr_names)

print("\nCreating LROH files...\n")
for i in range(len(chr_names)):
	if int(base_pairs[i]) > 1000000:
		os.system("vcftools --vcf " + file_path + " --out /vol/storage/ba/scripts/chromosome_outputs/" + chr_names[i] + " --LROH --chr " + chr_names[i])
	else:
		print("Chromosome " + chr_names[i] + " is smaller than one megabase, these don't interest me in my use case")

run_time = time.time() - program_start_time
print("\nFinished! It took " + str(run_time) + " seconds to complete")

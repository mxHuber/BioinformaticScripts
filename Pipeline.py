import os
import sys
import subprocess
import wget
import time
from prettytable import PrettyTable

# Author: Maximilian Leo Huber
#
# This pipeline creates a .vcf file and runs GetOrganelle for all given species in a .txt file.
# It also creates quality control files using fastqc for the trimmed and untrimmed files.
#
# Tools required:
# fastq-dump
# fastqc
# trimmomatic
# samtools
# GetOrganelle
#
# example command:
# python Pipeline.py names_and_links.txt
#
# To use this pipeline, simply provide a .txt file with the below specified format 
# and edit the base_path variable to your working directory
#
# The .txt must have the following format:
# [SPECIES_NAME]
# [READ_DOWNLOAD_LINK]
# [REFERENCE_GENOME_DOWNLOAD_LINK]
# --- EMPTY LINE ---
#
# So four lines for every species you want to run this pipeline on, in that specific order
#
# Example:
# ---------------------------------------------------------------------------------------------------------------------------------
# Fregetta_grallaria
# https://sra-pub-run-odp.s3.amazonaws.com/sra/SRR9946910/SRR9946910
# https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/013/399/335/GCA_013399335.1_ASM1339933v1/GCA_013399335.1_ASM1339933v1_genomic.fna.gz
# 
# Oceanites_oceanicus
# https://sra-downloadb.be-md.ncbi.nlm.nih.gov/sos5/sra-pub-zq-11/SRR009/9994/SRR9994311/SRR9994311.lite.1
# https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/013/396/615/GCA_013396615.1_ASM1339661v1/GCA_013396615.1_ASM1339661v1_genomic.fna.gz
#
# ---------------------------------------------------------------------------------------------------------------------------------

# get starting time of program
program_start_time = time.time()

# check for correct number of arguments
if not len(sys.argv) == 2:
	print("Bad Inputs. Command is: python Pipeline.py [FILE]")
	exit()

# edit this to your working directory
base_path = "/vol/storage/pipeline/"

# data_file = open("names_and_links")
data_file = open(sys.argv[1])

# the format is: name, read download link, reference genome download link, new line
lines = data_file.readlines()

data_file.close()

number_of_lines = len(lines)

names = []
readDownloadLinks = []
refGenomeDownloadLinks = []

# get all the names and corresponding download links
for i in range(number_of_lines):
	# name and remove newline character
	if (i % 4 == 0):
		names.append(lines[i][:-1])
	# read download link and remove newline character
	elif (i % 4 == 1):
		readDownloadLinks.append(lines[i][:-1])
	# reference genome download link and remove newline character
	elif (i % 4 == 2):
		refGenomeDownloadLinks.append(lines[i][:-1])
	# (i % 4 == 3) is a new line character, must be skipped

number_of_genomes = len(names)
print("The data file contains " + str(number_of_genomes) + " animal species")

runtime_per_animal = []

# Create .vcf file for all genome/read pairs
for i in range(number_of_genomes):
	# get time at the beginning of this loop
	for_loop_start_time = time.time()
	loop_time = -1

	current_path = base_path + names[i] + "/"

	print("Now working on " + current_path + "\n")

	# check if folder and .vcf already exists. If not, create folder and/or .vcf
	if os.path.exists(current_path + "output.vcf.gz"):
		print("\n.vcf file already exists, skipping species\n")
		runtime_per_animal.append(loop_time)
		continue
	elif not os.path.exists(current_path):
		os.makedirs(current_path)
	else:
		print("Folder " + current_path + " already exists" )

	#
	#	Downloads
	#

	# download read. If read already exists, don't redownload it
	cut_read_download_link = readDownloadLinks[i].split('/')
	current_read_name = cut_read_download_link[len(cut_read_download_link) - 1]
	current_read = "PLACEHOLDER_PATH_READ"

	if os.path.exists(current_path + current_read_name):
		print("Read file found, no need to download it again\n")
		current_read = current_path + current_read_name
	else:
		print("Downloading read file...")
		current_read = wget.download(readDownloadLinks[i], out=current_path)

	# download reference genome. If reference genome already exists, don't redownload it
	cut_refGenome_download_link = refGenomeDownloadLinks[i].split('/')
	current_refGenome_name = cut_refGenome_download_link[len(cut_refGenome_download_link) - 1]
	current_refGenome = "PLACEHOLDER_PATH_REFERENCE_GENOME"	

	if os.path.exists(current_path + current_refGenome_name):
		print("\nReferenceGenome found, no need to download it again\n")
		current_refGenome = current_path + current_refGenome_name
	else:
		print("\nDownloading reference genome...")
		current_refGenome = wget.download(refGenomeDownloadLinks[i], out=current_path)

	# wget saves the file with a weird '//' which makes the rest of the script not work
	current_read = current_read.replace("//",'/')
	current_refGenome = current_refGenome.replace("//",'/')

	if(not os.path.exists(current_read)):
		runtime_per_animal.append(loop_time)
		print("File: " + current_read + " not found. Skipping genome")
		continue

	if(not os.path.exists(current_refGenome)):
		runtime_per_animal.append(loop_time)
		print("File: " + current_refGenome + " not found. Skipping genome")
		continue

	#
	#	preparing reads by converting them to fastq and trimming them
	#

	# convert read file to fastq format
	print("\nConverting read file to fastq format...")
	os.system("/vol/storage/ncbi_sra_tools/sratoolkit.3.0.0-ubuntu64/bin/fasterq-dump  --split-files " + current_read + " --outdir " + current_path)
	print("\nGzipping .fastq file...")
	os.system("gzip " + current_read + "_1.fastq")
	os.system("gzip " + current_read + "_2.fastq")

	if not os.path.exists(current_read + "_1.fastq.gz"):
		runtime_per_animal.append(loop_time)
		print("fastq-dump didn't work. Therefore the neccesary file " + current_read + ".fastq is missing. Skipping genome")
		continue

	# cut adapters and trim low-quality reads
	print("\nTrimming adapters and low-quality reads...\n")
	os.system("java -jar /vol/storage/Trimmomatic-0.39/trimmomatic-0.39.jar PE -threads 8 " + current_read + "_1.fastq.gz " + current_read + "_2.fastq.gz " + current_read + "_paired_1.fastq.gz " + current_read + "_unpaired_1.fastq.gz " + current_read + "_paired_2.fastq.gz " + current_read + "_unpaired_2.fastq.gz " + "SLIDINGWINDOW:4:20 MINLEN:25 ILLUMINACLIP:/vol/storage/Trimmomatic-0.39/adapters/TruSeq3-PE.fa:2:30:10:2:keepBothReads")
	
	#
	#	fastqc quality control
	#

	# create quality control files of reads before they got trimmed
	print("\nCreating fastqc reports for untrimmed files...")
	os.system("fastqc -t 18 -f fastq " + current_read + "_1.fastq.gz " + current_read + "_2.fastq.gz")

	# create quality control files of reads after trimming with trimmomatic
	print("\nCreating fastqc reports for trimmed files...")
	os.system("fastqc -t 18 -f fastq " + current_read + "_paired_1.fastq.gz" + current_read + "_paired_2.fastq.gz")

	#
	#	getOrganelle
	#

	if not os.path.exists(current_path + "getOrganelle_" + names[i]):
		getOrganelle = "/vol/storage/GetOrganelle-1.7.6.1/get_organelle_from_reads.py"
		first = current_read + "_paired_1.fastq.gz"
		second = current_read + "_paired_2.fastq.gz"
		folderName = current_path + "getOrganelle_" + names[i]
		spades = "/vol/storage/SPAdes-3.15.4-Linux/bin/"
		os.system(getOrganelle + " -1 " + first + " -2 " + second + " -o " + folderName + " -F animal_mt -R 10 --memory-save --out-per-round --which-spades " + spades)
	else:
		print("GetOrganelle folder already exists")
	
	#
	#	read mapping
	#

	# burrows wheeler alignment
	print("\nBurrows Wheeler Alignment...")
	os.system("bwa index -p " + current_path + "referenceIndex " + current_refGenome)

	# convert file into bam
	print("\nConverting to bam format")
	os.system("bwa mem -t 18 " + current_path + "referenceIndex " + current_read + "_paired_1.fastq.gz " + current_read + "_paired_2.fastq.gz " + "| samtools sort -@ 18 -o " + current_path + "bwa.sorted.bam")

	# create index of read
	print("\nIndexing read...")
	os.system("samtools index " + current_path + "bwa.sorted.bam")

	# unzip reference for samtools
	print("\nUnzipping reference genome...")
	os.system("gunzip " + current_refGenome)

	# String with the name of the unzipped reference genome file
	current_unzipped_refGenome = current_refGenome[:-3]

	# index reference
	print("\nIndexing reference genome...")
	os.system("samtools faidx " + current_unzipped_refGenome)

	# create .vcf
	print("\nCreating .vcf file...")
	os.system("samtools mpileup -C50 -uf " + current_unzipped_refGenome + " " + current_path + "bwa.sorted.bam | bcftools call -c -o " + current_path + "output.vcf")

	# zip .vcf, because they are like 110 GB big (i only have 2 TB, i need space)
	print("\nZipping .vcf file...")
	os.system("bgzip " + current_path + "output.vcf")

	# delete files that aren't needed anymore
	print("\nDeleting files that aren't needed anymore...\n")
	os.system("rm " + current_read)
	os.system("rm " + current_refGenome)
	os.system("rm " + current_read + "_1.fastq.gz")
	os.system("rm " + current_read + "_2.fastq.gz")
	os.system("rm " + current_read + "_paired_1.fastq.gz")
	os.system("rm " + current_read + "_paired_2.fastq.gz")
	os.system("rm " + current_read + "_unpaired_1.fastq.gz")
	os.system("rm " + current_read + "_unpaired_2.fastq.gz")
	os.system("rm " + current_path + "bwa.sorted.bam")
	os.system("rm " + current_path + "bwa.sorted.bam.bai")
	os.system("rm " + current_unzipped_refGenome)
	os.system("rm " + current_unzipped_refGenome + ".fai")
	os.system("rm " + current_path + "referenceIndex.amb")	
	os.system("rm " + current_path + "referenceIndex.ann")
	os.system("rm " + current_path + "referenceIndex.bwt")
	os.system("rm " + current_path + "referenceIndex.pac")
	os.system("rm " + current_path + "referenceIndex.sa")

	# calculate runtime of current loop and save it in the corresponding list
	for_loop_end_time = time.time()
	loop_time = for_loop_end_time - for_loop_start_time
	runtime_per_animal.append(loop_time)

program_end_time = time.time()
final_time = program_end_time - program_start_time

print("Program finished! It took " + str(final_time) + " seconds to finish")

time_table = PrettyTable()
# time_table.field_names["Name", "Time"]

for t in range(number_of_genomes):
	time_table.add_row([names[t], str((runtime_per_animal[t] / 60) / 60) + " hours"])

print(time_table)


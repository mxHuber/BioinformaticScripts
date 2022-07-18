import os
import sys
import time

# example command:
# python /vol/storage/ba/scripts/psmc_for_vcf.py /vol/storage/pipeline/Fregetta_grallaria/output.vcf -o /vol/storage/pipeline/Fregetta_grallaria/psmc/ -n Fregetta_grallaria

# get starting time of program
program_start_time = time.time()

if not len(sys.argv) == 6:
	print("Bad Inputs. Command is: python psmc_for_vcf.py [VCF_FILE] -o [OUTPUT_DIRECTORY] -n [NAME_FOR_FILES]")
	exit()

# path of .vcf
file_path = sys.argv[1]
# output directory
output_dir = sys.argv[3]
# name for files
file_name = sys.argv[5]
# sys.argv[0] is the command itself

# check if folder exists and if not, create it
if not os.path.exists(output_dir):
	os.makedirs(output_dir)

# make consensus file
print("Creating consensus file...")
os.system("vcfutils.pl vcf2fq -d 10 -D 100 " + file_path + " > " + output_dir + "consensus.fq")

# psmc commands
print("Now using command fq2psmcfa")
first_command = "/vol/storage/psmc-0.6.5/utils/fq2psmcfa -q20 consensus.fq > " + output_dir + file_name + ".psmcfa"
os.system(first_command)

print("Now using command psmc")
parameter = "4+25*2+4+6"
second_command = "/vol/storage/psmc-0.6.5/psmc -N25 -t15 -r5 -p " + parameter + " -o " + output_dir + file_name + ".psmc " + output_dir + file_name + ".psmcfa"
os.system(second_command)

print("Now using command psmc2history-pl")
third_command = "/vol/storage/psmc-0.6.5/utils/psmc2history.pl " + output_dir + file_name + ".psmc | /vol/storage/psmc-0.6.5/utils/history2ms.pl > " + output_dir + file_name + "_ms-cmd.sh"
os.system(third_command)

run_time = time.time() - program_start_time
print("\nFinished! It took " + str(run_time / 3600) + " hours to complete")
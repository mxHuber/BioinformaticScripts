import matplotlib.pyplot as plt
import seaborn as sns
import time
import sys
import os

# get starting time of program 
program_start_time = time.time()

# checks if everything is as it should be
if not len(sys.argv) == 6:
	print("Bad input. Command is: python plot_het.py [FILE_PATH] -o [OUTPUT_PATH] -n [NAME_FOR_FILE]")
	exit()

# .vcf file path
file_path = sys.argv[1]
output_path = sys.argv[3]
file_name = sys.argv[5]
# sys.argv[0] is the command itself

data_file = open(file_path, 'r')
data = data_file.read()
data_file.close()

data = data.split("\n")
data = data[15:]

relevant = []

# go over all lines and find biggest chromosomes/assemblies
for i in range(len(data) - 1):
	current = data[i].split("\t")
	
	current_size = int(current[3])

	if current_size < 1000000:
		continue

	relevant.append((i, current_size))

relevant.sort(key=lambda tup: tup[1], reverse=True)

# x axis names for plot
x_val = []

# gather percentage of measure of heterozygosity
y_val = []

# if there are less than 30, plot as much as possible, else, plot 30
range_num = 30
if len(relevant) < 30:
	range_num = len(relevant)

for i in range(range_num):
	current = data[relevant[i][0]].split("\t")
	current_zero_one = current[1]
	current_one_two = current[2]
	current_all = current[3]
	x_val.append(str(relevant[i][0] + 1))
	y_val.append((int(current_zero_one) + int(current_one_two))/int(current_all))

y_val.sort(reverse=True)

# set seaborn default theme
sns.set_theme()

# plot stuff
plot = plt.figure(figsize=(10, 8))
subPlot = plot.add_subplot(111)
subPlot.bar(x_val, y_val)
subPlot.set_xlabel("Chromosomes")
subPlot.set_ylabel("Measure of heterozygosity in %")

plot.savefig(output_path + file_name + ".png")

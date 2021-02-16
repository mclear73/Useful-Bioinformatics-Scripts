## Useful Linux Commands and Analysis Pipeline ##

### Downloading Fastq files ###
- For downloading via ftp or http:
	- Note: there are http and ftp-user/pass options
	
			wget --user=USER --password=PASS <URL>
- For decompressing .tar file:

		tar -xvf <filename.tar>
- For decompressing .tar.gz or .gz files:

		gzip -d <filenam.tar.gz>

### For assessing the quality of fastq files ###
- This method uses [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) to run the analytics followed by [MultiQC](https://multiqc.info/docs/) for compilation and visualization of the data.
- The data is most likely in fastq.gz format. In order to process these compress files, we will add the zcat command to FastQC.
- This command is written as a loop to analyze all fastq.gz files in a directory, if you wish to analyze specific files or different file types, make sure to edit the fastq.gz portion of the loop
	- Note: my specific instance of FastQC is located in the ~/ptmp/FastQC directory. In this loop, I have specified an output directory. It is highly recommended that you organize the FastQC output files in a single directory as the following MultiQC command will compile all of the FastQC files in a single directory. If you plan to use the same directory tree as me, run `mkdir FastQC_Output` in the directory where your fastq.gz files are sitting.
	- Note: `-t 8` specifies 8 threads to be run. Make sure that you have the processing power to run that many threads and have allocated enough memory (250mb per thread)

			for f in $(ls *fastq.gz)
			do
			zcat ${f} | ~/ptmp/FastQC/fastqc -t 8 -o FastQC_Output ${f}
			done
- Once all of the files have been run through FastQc, use MultiQC to compile the data and visualize the outputs:
	-Note: This assumes you have placed your output files into a directory labeled "FastQC_Output". The following will collect all of the FastQC output files in the current directory

			cd FastQC_Output
			multiqc .
- MultiQC will output many files but the most useful one will be titled "multiqc_report.html". Download the file and open it in a web browser. 
		


		
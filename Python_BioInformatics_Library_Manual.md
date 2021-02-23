## Python Bioinformatics Library Manual ##

### batch_iterator() ###
    batch_iterator(iterator, batch_size)
- Meant to  be used by Bio.SeqIO to parse fasta files into smaller files based on a specified number of entries
- This function was taken directly from biopython documentation

### combineIPC2output() ###
    combineIPC2output()
- This function will compile all IPC2 output *.csv files in the current working directory
- As of February 16, 2021, it will also automatically parse *N. crassa*, *A. nidulans*, and *C. reinhardtii* protein names for addition to a full annotation
- This function will output a single excel file titled 'IPC2 Output.xlsx' where a parsed 'IPC2_forAnnot' sheet containing the parsed protein names (limited functionality) and a 'IPC2_FULL' sheet containing all of the compiled IPC2 .csv files

### compileChlamAnnot() ###
    compileChlamAnnot(outputFile, trans, geneName, description, definition, 
	annotation, protFasta, signalP, Delaux, IPC2, PlantTFDB)
- This function will compile all of the *C. reinhardtii* annotation information present in the [AnnotationFiles](https://github.com/mclear73/Useful-Bioinformatics-Scripts/tree/main/AnnotationFiles) directory
- For example usage see the [ExampleUsage](https://github.com/mclear73/Useful-Bioinformatics-Scripts/tree/main/ExampleUsage) Directory
- This is not meant to be a reusable function to be used with other annotated plant genomes. It is specifically meant for a single compilation of *C. reinhardtti* annotations

### compileMycocosum() ###
    compileMycocosum(outputFile, pep, trans="None", KOG="None", KEGG="None", 
	GO="None", InterPro="None", SignalP="None", IPC2="None",CAZy="None", FTFDB="None")
- This function is meant to compile fungal annotation data compiled from JGI Mycocosm.
- This funciton is meant to be re-used on other fungi as long as data is downloaded from the same sources. See [AnnotationFiles](https://github.com/mclear73/Useful-Bioinformatics-Scripts/tree/main/AnnotationFiles) directory for example files
- You do not have to include all of these files for the compilation to work, however you must specify outputFile and include a peptide fasta file for the function to run and compile any information. 
- For usage example see [ExampleUsage](https://github.com/mclear73/Useful-Bioinformatics-Scripts/tree/main/ExampleUsage) Directory

### queryIPC2() ###
    queryIPC2(executablePath)
- This function uses selenium to query the IPC2 webpage.
- I wrote this function because fasta queries must be short (~50 peptide sequences) and it can take a long time to run a whole proteome
- You must download the [chromedriver executable](https://sites.google.com/a/chromium.org/chromedriver/) to use this function. See instructions in link
	- This process can be kind of confusing use [these instructions](https://sites.google.com/a/chromium.org/chromedriver/downloads/version-selection) to determine which driver you need to download based on your version of chrome
	- Make sure that you note where you save the chromedriver.exe file as it is needed to run the function
- This function must be run from the directory containing only the "*.fasta" files that you want to query IPC2 with
- The .csv outputs from IPC2 will be deposited in your Downloads directory as if you manually entered in the fasta sequences on the webpage
	- executablePath: string that contains the PATH + filename of your chromedriver.exe Ex:  
		`'C:/Users/mclea/OneDrive/Desktop/chromedriver.exe'`

### split_fasta() ###
    split_fasta(File, outputPrefix, length)
- This function takes a protein fasta file and outputs smaller fasta files so that they can be loaded into web-based analysis tools such as SignalP and IPC2. 50 peptide sequences is recommended for IPC2, but any length can be applied for other purposes
	- File: string that includes PATH + file name of protein fasta file (note: for IPC2 asterisks are acceptable) Ex:  
		`'G:MyDrive/proteins.fasta'`
	- outputPrefix: string that will be added to be appended to the beginning of all of the output file names. I use the prefix to indicate the organism I am parsing EX:  
		`'Creinhardtii'`
	- length: integer specifying the number of fasta sequences included in each file. (50 recommended for IPC2) Ex:  
		`50`
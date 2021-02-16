# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 13:46:09 2020

@author: mclea
"""

##General function used by split_fasta##
#############################################################################
def batch_iterator(iterator, batch_size):
    """Returns lists of length batch_size.

    This can be used on any iterator, for example to batch up
    SeqRecord objects from Bio.SeqIO.parse(...), or to batch
    Alignment objects from Bio.AlignIO.parse(...), or simply
    lines from a file handle.

    This is a generator function, and it returns lists of the
    entries from the supplied iterator.  Each list will have
    batch_size entries, although the final list may be shorter.
    """
    entry = True  # Make sure we loop once
    while entry:
        batch = []
        while len(batch) < batch_size:
            try:
                entry = next(iterator)
            except StopIteration:
                entry = None
            if entry is None:
                # End of file
                break
            batch.append(entry)
        if batch:
            yield batch

##Split protein FASTA for input into isoelectric point calculator##
#This function requires the full path and filename of the protein fasta
#File that you wish to divide
#This function is necessary because IPC2 has a file size limit
#It will deposit .csv files in your downloads folder as if you had manually
#used IPC2
#############################################################################
def split_fasta(File, outputPrefix, length):
      from Bio import SeqIO
      import os
      direct = os.getcwd()
      record_iter = SeqIO.parse(open(File), "fasta")

      for i , batch in enumerate(batch_iterator(record_iter, length)):
            filename = direct + "\\" + outputPrefix +"ISO_%i.fasta" % (i + 1)
            with open(filename, "w") as handle:
                  count = SeqIO.write(batch, handle, "fasta")
            print("Wrote %i records to %s" % (count, filename))
            
##Selenium for isoelectric point##
#############################################################################
#This function will run IPC2 on all of the protein fasta files in a directory
#You must run this function within the directory containing the "*.fasta"
#output files from split_fasta()
#peptide sequences. You must also provide the path for the selenium chrome 
#driver on your computer. For more information, see Python Library Manual
#and selenium docs
#Note: my executable path is 'C:/Users/mclea/OneDrive/Desktop/chromedriver.exe'
def queryIPC2(executablePath):
      from selenium import webdriver
      import os
      import time      
      for filename in os.listdir(os.getcwd()):
            if filename.endswith(".fasta"):
                  try:
                        driver = webdriver.Chrome(executable_path=executablePath)
                        my_file = open(filename)
                        file_contents = my_file.read()                       
                        driver.get("http://ipc2.mimuw.edu.pl/index.html")
                        element = driver.find_element_by_name('protein')
                        element.send_keys(file_contents)
                        my_file.close()
                        driver.find_element_by_name('protein').submit()
                        driver.get("http://ipc2.mimuw.edu.pl/result.csv")
                        time.sleep(3)
                        driver.close()
                  except Exception as e:
                        print("something went wrong: ")
                        print(e)
      driver.quit()

##Compile IPC2 Files##
#############################################################################
#This function compiles all of the .csv files generated by queryIPC2()
#This function also parses specific transcript names
#Run this function in the directory where all of your IPC2 output files are
#stored. 
#NOTE: all "*.csv" files in the directory must be IPC2 output files
#The output is a single .xlsx file with two sheets. One sheet contains
#parsed protein names and the other sheet is the full, unparsed list
#of all combined IPC2 outputs in the directory
def combineIPC2output():
      import os
      import glob
      import pandas as pd
      #need to parse the header column in the new dataframe       
      path = os.getcwd()
      all_files = glob.glob(os.path.join(path, "*.csv"))
      
      df_from_each_file = (pd.read_csv(f) for f in all_files)
      concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
      
      concatenated_df = concatenated_df[['header', 'molecular_weight', 'IPC2_protein', 'IPC2_peptide']].drop_duplicates()
      
      #Split dataframe by organism this is necessary because we need to parse the headers
      #Differently
      if concatenated_df[concatenated_df['header'].str.contains('Neucr')]:
            neurDF = concatenated_df[concatenated_df['header'].str.contains('Neucr')]
            #Parse the header column
            nParse = neurDF["header"].str.split("|", expand = True).drop(columns=[0,1,2]).rename(columns={3:'header'})
            nParse['match'] = neurDF['header']
            nParse = nParse.merge(neurDF, how='left', left_on='match', right_on='header').drop(columns=['match', 'header_y'])
      else:
            nParse = pd.DataFrame()
            
      if concatenated_df[concatenated_df['header'].str.contains('Aspnid')]:
            aspDF = concatenated_df[concatenated_df['header'].str.contains('Aspnid')]
            #Parse the header column
            aParse = aspDF["header"].str.split("|", expand = True).drop(columns=[0,1,2]).rename(columns={3:'header'})
            aParse['match'] = aspDF['header']
            aParse = aParse.merge(aspDF, how='left', left_on='match', right_on='header').drop(columns=['match', 'header_y'])
      else:
            aParse = pd.DataFrame()
            
      if concatenated_df[concatenated_df['header'].str.contains('Cre')]:
            chlamDF = concatenated_df[concatenated_df['header'].str.contains('Cre')]
            #Parse the header column
            cParse = chlamDF["header"].str.split(" ", expand = True).drop(columns=[1,2,3,4,5]).rename(columns={0:'header'})
            cParse['match'] = chlamDF['header']
            cParse = cParse.merge(chlamDF, how='left', left_on='match', right_on='header').drop(columns=['match', 'header_y'])
      else:
            cParse = pd.DataFrame()
      
      #Concatenate modified dataframes
      fixedDF = pd.concat([nParse, aParse, cParse])
      
      #Export file containing the modified dataframes and original concatenated DF
      #Export Excel File
      writer = pd.ExcelWriter('IPC2 Output.xlsx')
      fixedDF.to_excel(writer,'IPC2_forAnnot', index=False)
      concatenated_df.to_excel(writer,'IPC2_FULL', index=False)
      writer.save()
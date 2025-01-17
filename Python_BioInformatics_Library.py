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
def split_fasta(File, outputPrefix, length=50):
      from Bio import SeqIO
      import os
      direct = os.getcwd()
      record_iter = SeqIO.parse(open(File), "fasta")

      for i , batch in enumerate(batch_iterator(record_iter, length)):
            filename = direct + "\\" + outputPrefix +"ISO_%i.fasta" % (i + 1)
            with open(filename, "w") as handle:
                  count = SeqIO.write(batch, handle, "fasta")
            print("Wrote %i records to %s" % (count, filename))

#Add column that designates if protein may be a small secreted protein based
# off of SingalP output and peptide length
def getSSP(DF, signalPname):
      secreteList = []
      for a , b in zip(DF['AA Length'], DF[signalPname]):
            if a <= 400 and b == 'SP(Sec/SPI)':
                  secreteList.append('SSP')
            elif a > 400 and b == 'SP(Sec/SPI)':
                  secreteList.append('Secreted')
            else:
                  secreteList.append('Not Exciting')
      DF['Secreted'] = secreteList
      newDF = DF
      return newDF            
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
      
#Compiles all annotations files available from mycocosum and outputs it to a single
#.xlsx file denoted by "outputFile"
#Note: outputFile and pep must be used!!!
def compileMycocosum(outputFile, pep, trans="None", KOG="None", KEGG="None", 
                     GO="None", InterPro="None", SignalP="None", IPC2="None",
                     CAZy="None", FTFDB="None", Secretome="None"):
      import pandas as pd
      from Bio import SeqIO
      
      #Extract protein ID and gene names from protein FASTA file
      record = list(SeqIO.parse(pep, "fasta"))
      rec = [rec.id for rec in record]
      aa = [rec.seq for rec in record]
      aspDF = pd.DataFrame(rec)
      aspDF = aspDF[0].str.split("|", expand = True).rename(columns={0:'Source', 1:'Genome', 2:'Protein ID', 3:'Protein Name'})
      aspDF['Protein ID'] = aspDF['Protein ID'].astype(str)
      #Add amino acid sequence
      aspDF['AA Seq'] = aa
      aspDF['AA Length'] = aspDF['AA Seq'].str.len()


      if KOG != "None":
            aspKOG = pd.read_csv(KOG, sep = '\t')
            aspKOG['proteinId'] = aspKOG['proteinId'].astype(str)
            aspKOG = aspKOG.drop(columns='#transcriptId')
            #Add KOG data
            aspDF = aspDF.merge(aspKOG, how='left', left_on='Protein ID', right_on='proteinId').drop(columns= ['proteinId'])
                                 
      if KEGG != "None":
            aspKEGG = pd.read_csv(KEGG, sep = '\t')
            aspKEGG['#proteinId'] = aspKEGG['#proteinId'].astype(str)
            #Add KEGG data
            aspDF = aspDF.merge(aspKEGG, how='left', left_on='Protein ID', right_on='#proteinId').drop(columns= ['#proteinId'])
                   
      if GO != "None":
            aspGO = pd.read_csv(GO, sep = '\t')
            aspGO['#proteinId'] = aspGO['#proteinId'].astype(str)
            #Add GO data
            aspDF = aspDF.merge(aspGO, how='left', left_on='Protein ID', right_on='#proteinId').drop(columns= ['#proteinId'])
                  
      if InterPro != "None":
            aspInterPro = pd.read_csv(InterPro, sep = '\t')
            aspInterPro['#proteinId'] = aspInterPro['#proteinId'].astype(str)
            #Add InterPro data
            aspDF = aspDF.merge(aspInterPro, how='left', left_on='Protein ID', right_on='#proteinId').drop(columns= ['#proteinId'])
                        
      if SignalP != "None":
            aspSignalP = pd.read_csv(SignalP)
            aspSignalP['Protein'] = aspSignalP['Protein'].astype(str)
            #Add signalP data
            aspDF = aspDF.merge(aspSignalP, how='left', left_on='Protein Name', right_on='Protein').drop(columns= ['Protein'])
                 
      if trans != "None":
            #Extract transcript IDs and gene names from transcript FASTA file
            record = list(SeqIO.parse(trans, "fasta"))
            rec = [rec.id for rec in record]
            aspTrans = pd.DataFrame(rec)
            aspTrans = aspTrans[0].str.split("|", expand = True).rename(columns={0:'Source', 1:'Genome', 2:'Transcript ID', 3:'Protein Name'})
            aspTrans['Transcript ID'] = aspTrans['Transcript ID'].astype(str)
            aspDF = aspDF.merge(aspTrans, how='left', left_on='Protein Name', right_on='Protein Name').drop(columns = ['Source_y','Genome_y'])
            
      if FTFDB != "None":
            aspTFDB = pd.read_csv(FTFDB)
            aspTFDB[' Locus Name'] = aspTFDB[' Locus Name'].astype(str)
            aspTFDB = aspTFDB.drop(columns=' Species Name')
            #Add Fungal TFDB data
            aspDF = aspDF.merge(aspTFDB, how='left', left_on='Protein Name', right_on=' Locus Name').drop(columns=[' Locus Name'])
     
      
      #Add IPC2 data
      if IPC2 != "None":
            ipc2 = pd.ExcelFile(IPC2)
            ipc2DF = pd.read_excel(ipc2, 'IPC2_forAnnot')
            aspDF = aspDF.merge(ipc2DF, how='left', left_on='Protein Name', right_on='header_x').drop(columns= ['header_x'])
            
      if CAZy != "None":
            caz = pd.ExcelFile(CAZy)
            cazDF = pd.read_excel(caz, 'Sheet1')
            if aspDF['Protein Name'].str.contains('NCU').any():
                  aspDF['Gene Name'] = aspDF['Protein Name'].str[:-2]
                  aspDF = aspDF.merge(cazDF, how='left', left_on='Gene Name', right_on='Gene').drop(columns= ['Gene'])                  
            
            else:            
                  aspDF = aspDF.merge(cazDF, how='left', left_on='Protein Name', right_on='Gene').drop(columns= ['Gene'])
                  
      if Secretome != "None":
            print("You included a secretomeDB file. It may take a while to compile.")
            record = list(SeqIO.parse(Secretome, "fasta"))
            rec = [rec.id for rec in record]
            aa = [rec.seq for rec in record]
            secDF = pd.DataFrame(rec)
            secDF = secDF[0].str.split("|", expand = True).rename(columns={0:'Source', 
                         1:'ref#', 2:'ref', 3:'NCBI Name', 
                         4:'SecretomeDB Description'})
            secDF['SecretomeDB Description'] = secDF['SecretomeDB Description'].astype(str)
            secDF['AA Seq'] = aa
            aspDF = aspDF.merge(secDF[['AA Seq', 'SecretomeDB Description']], 
                                how='left', left_on='AA Seq', 
                                right_on='AA Seq', indicator=True)
            tempDF = aspDF.drop_duplicates(subset=['Protein Name'])
            length = len(tempDF[tempDF['_merge'] == 'both'])
            aspDF = aspDF.drop(columns=['_merge'])
            print("You matched ",length, "peptides of ",len(aa), "present in the secretomeDB.")               
            
      #Determine secreted and SSP based of signalP data and peptide length
      if SignalP != 'None':
            getSSP(aspDF, 'Prediction')
            
      #Add Lipid binding  
#      gpsLipid = pd.read_csv(gpsLipid, sep='\t')
#      names = gpsLipid["ID"].str.split("|", expand = True).drop(columns=[0,1,2]).rename(columns={3:'ID'})
#      names['match'] = gpsLipid['ID']
#      newgpsLipid = names.merge(gpsLipid, how='left', left_on='match', right_on='ID').drop(columns=['match', 'ID_y'])
#      aspDF = aspDF.merge(newgpsLipid, how='left', left_on='Protein Name', right_on='ID_x').drop(columns=['ID_x'])    

      #Output the final annotation file          
      filename =  outputFile + '.xlsx'                    
      writer = pd.ExcelWriter(filename)
      aspDF.to_excel(writer,'FULL', index=False)
      writer.save()
      
#Compiles all of the annotation data for Chlamydomonas reinhardtii
#This function is specific to C. reinhardtii and is not meant to be adapted
#to a different organisms
#This function will also plot the amino acid length distribution and
#Output some basic statistics about the predict protein length distribution
def compileChlamAnnot(outputFile, trans, geneName, description, definition, annotation, protFasta,
                      signalP, Delaux, IPC2, PlantTFDB):
      import pandas as pd
      from Bio import SeqIO
      from scipy import stats
      import numpy as np
      import matplotlib.pyplot as plt
      #Import relevant files
      chlamName = pd.read_csv(trans, skiprows=[0], delim_whitespace=True)
      chlamGeneName = pd.read_csv(geneName, sep='\t', 
                                  names=['Transcript ID', 'Gene Name', 'Alt. Gene Name'])
      chlamDescription = pd.read_csv(description, sep='\t', 
                                  names=['Transcript ID', 'Description'])     
      chlamDefline = pd.read_csv(definition, sep='\t', 
                                  names=['Transcript ID', 'defLine/pdef', 'Details'])      
      chlamAnnotation = pd.read_csv(annotation, sep='\t')      
      CHLAMrecord = list(SeqIO.parse(protFasta, "fasta"))      
#      predXLS = pd.ExcelFile(predAlgo)
      delaux = pd.ExcelFile(Delaux)
      
      #Add Gene Name
      chlamName = chlamName.merge(chlamGeneName, how='left', left_on= '#5.5', right_on='Transcript ID').drop(columns=['Transcript ID'])
                                  
      #Add Gene Description
      chlamName = chlamName.merge(chlamDescription, how='left', left_on= '#5.5', right_on='Transcript ID').drop(columns=['Transcript ID'])
                                 
      #Add defline/pdef
      chlamName = chlamName.merge(chlamDefline, how='left', left_on= '#5.5', right_on='Transcript ID').drop(columns=['Transcript ID'])
                                  

      
      #Add annotation
      chlamName = chlamName.merge(chlamAnnotation, how='left', left_on= '#5.5', right_on='transcriptName').drop(columns=['transcriptName'])
      CHLAMrec = [rec.id for rec in CHLAMrecord]
      CHLAMaa = [rec.seq for rec in CHLAMrecord]
      CHLAMDFpep = pd.DataFrame(CHLAMrec)
      CHLAMDFpep['AA Seq'] = CHLAMaa
      CHLAMDFpep['AA Length'] = CHLAMDFpep['AA Seq'].str.len()      
      CHLAMDFpep = CHLAMDFpep[(np.abs(stats.zscore(CHLAMDFpep['AA Length'])) < 3)]
      proteinTotal = len(CHLAMDFpep)
      avgProtLength = CHLAMDFpep['AA Length'].mean()
      f= open("Creinhardtii.txt", "w")
      print("Total Predicted Proteins = " + str(proteinTotal), file=f)
      print("Average Protein Length = " + str(avgProtLength), file=f)
      f.close()
      CHLAMDFpep.boxplot(column=['AA Length'])
      plt.savefig("Creinhardtii_AALength.pdf")
      chlamName = chlamName.merge(CHLAMDFpep, how='left', left_on='#5.5', right_on=0)
      chlamName =chlamName.drop(columns=[0])
      
      #Add PredAlgo, removed because PredAlgo appears to be drepecated
#      predDF = pd.read_excel(predXLS, 'Sheet1')   
#      chlamName = chlamName.merge(predDF, how='left', left_on='3.1', right_on='full ID (most v3)')
#      chlamName = chlamName.drop(columns=['full ID (most v3)'])

      #Add Delaux annotation for CSSP  
      delauxGenes = pd.read_excel(delaux, 'Sheet1')
      chlamName = chlamName.merge(delauxGenes, how='left', left_on='#5.5', right_on='#5.5') 
                                  
      #Add SignalP
      sigP = pd.read_csv(signalP)
      chlamName = chlamName.merge(sigP, how='left', left_on='#5.5', right_on='# ID')

      #Add IPC2                                  
      ipc2 = pd.ExcelFile(IPC2)
      ipc2DF = pd.read_excel(ipc2, 'IPC2_forAnnot')
      chlamName = chlamName.merge(ipc2DF, how='left', left_on='#5.5', right_on='header_x').drop(columns= ['header_x'])
                                  
      #Add Plant TFDB                                  
      TFDF = pd.read_csv(PlantTFDB)
      chlamName = chlamName.merge(TFDF, how='left', left_on='#5.5', right_on='TF_ID').drop(columns= ['TF_ID'])
                                  
      #Determine secreted and SSP based of signalP data and peptide length
      getSSP(chlamName, 'Prediction')
                       
      #Generate the output file, 'Creinhardtii_Annotation.xlsx'
      writer = pd.ExcelWriter(outputFile)
      chlamName.to_excel(writer,'FULL', index=False)
      writer.save()

#This function takes a .csv file of gene names (or any other shared identifier)
#And will make a venn diagram for up to 6 comparisons and create a union
#output file that includes the genes that are shared in all of the categories
#included in the comparison
#Note: Column headings are automatically category labels
#If more than 6 columns are included, only the first 6 columns will be 
#compared
def makeVenn(csvFilePath):
      import pandas as pd
      from venn import venn
      DF = pd.read_csv(csvFilePath)
      catList = list(DF.columns.values)
      if len(catList) == 2:
            set1 = set()
            set2 = set()
            for i in DF.iloc[:,0]:
                  set1.add(i)
            for i in DF.iloc[:,1]:
                  set2.add(i)
            unionDict = dict([(catList[0], set1), (catList[1],set2)])
            union = set1.intersection(set2)
      elif len(catList) == 3:
            set1 = set()
            set2 = set()
            set3 = set()
            for i in DF.iloc[:,0]:
                  set1.add(i)
            for i in DF.iloc[:,1]:
                  set2.add(i)
            for i in DF.iloc[:,2]:
                  set3.add(i)
            unionDict = dict([(catList[0], set1), (catList[1],set2), 
                              (catList[2],set3)])
            union = set1.intersection(set2, set3)
      elif len(catList) == 4:
            set1 = set()
            set2 = set()
            set3 = set()
            set4 = set()
            for i in DF.iloc[:,0]:
                  set1.add(i)
            for i in DF.iloc[:,1]:
                  set2.add(i)
            for i in DF.iloc[:,2]:
                  set3.add(i)
            for i in DF.iloc[:,3]:
                  set4.add(i)
            unionDict = dict([(catList[0], set1), (catList[1], set2), 
                             (catList[2], set3), (catList[3], set4)])
            union = set1.intersection(set2, set3, set4)
      elif len(catList) == 5:
            set1 = set()
            set2 = set()
            set3 = set()
            set4 = set()
            set5 = set()
            for i in DF.iloc[:,0]:
                  set1.add(i)
            for i in DF.iloc[:,1]:
                  set2.add(i)
            for i in DF.iloc[:,2]:
                  set3.add(i)
            for i in DF.iloc[:,3]:
                  set4.add(i)
            for i in DF.iloc[:,4]:
                  set5.add(i)
            unionDict = dict([(catList[0], set1), (catList[1], set2), 
                             (catList[2], set3), (catList[3], set4), 
                             (catList[4], set5)])
            union = set1.intersection(set2, set3, set4, set5)
      elif len(catList) == 6:
            set1 = set()
            set2 = set()
            set3 = set()
            set4 = set()
            set5 = set()
            set6 = set()
            for i in DF.iloc[:,0]:
                  set1.add(i)
            for i in DF.iloc[:,1]:
                  set2.add(i)
            for i in DF.iloc[:,2]:
                  set3.add(i)
            for i in DF.iloc[:,3]:
                  set4.add(i)
            for i in DF.iloc[:,4]:
                  set5.add(i)
            for i in DF.iloc[:,5]:
                  set6.add(i)
            unionDict = dict([(catList[0], set1), (catList[1], set2), 
                             (catList[2], set3), (catList[3], set4), 
                             (catList[4], set5), (catList[5], set6)])
            union = set1.intersection(set2, set3, set4, set5, set6)
      if len(catList) >=2:
            unionDF = pd.DataFrame(union)
            figure = venn(unionDict)
            writer = pd.ExcelWriter('Venn Output.xlsx')
            unionDF.to_excel(writer,'Union', index=False)
            writer.save()
            return figure, unionDF
            if len(catList) > 6:
                  print("More than 6 columns were included in dataset. Only the first 6 columns are included in this analysis.")
      elif len(catList) == 1:
            print("Only one column is included. There is nothing to compare.")

#This function will extract keywords provided in the form of a dataframe column
#From an annotation dataframe
#The geneIdentifier value should be the column in the annotation file that will 
#be used to match with the differential expression data
###NOTE: This is supposed to be used as part fo the extractFromCSV() function
###It is not recommended to use this function outside of the extractFromCSV() function           
def KeywordExtract(annotationDF, DFColumn, geneIdentifier):
      import pandas as pd
      DFColumn = DFColumn.dropna()
      DFColumn = DFColumn.astype(str)      
      listString = '|'.join(DFColumn)     
      DF = annotationDF[annotationDF.apply(lambda row: row.astype(str).str.contains(listString,
                                            case=False).any(), axis=1)]
      DF = DF.drop_duplicates(subset=[geneIdentifier])
#      geneList = pd.DataFrame()
#      geneList[geneIdentifier] = DF[geneIdentifier]
      return DF

#This function will extract key genes of interest based on a string match. This 
#Can be used to extract groups of genes of interest from an annotation file
#This function requires 1) an annotation file in .csv format. 2) A .csv file with
#column headings being the gene group names of interest and the values underneath the column
#the extraction keywords. 3) A geneIdentifier value that specifies the column name
#to be used to match with differential expression data downstream. 4) Full output
#file name as .xlsx. and 5) [optional] specify whether SYM pathway are desired to be extracted
def extractFromCSV(annotationCSV, genesCSV, geneIdentifier, outputFile, delaux='None'):
      import pandas as pd
      AnnotDF = pd.read_csv(annotationCSV)
      genesDF = pd.read_csv(genesCSV)
      cols = list(genesDF)
      writer = pd.ExcelWriter('Genes of Interest.xlsx')
      for i in cols:
            temp = KeywordExtract(AnnotDF, genesDF[i], geneIdentifier)
            temp.to_excel(writer, i, index=False)
      ssps = AnnotDF[AnnotDF['Secreted'] == 'SSP'].drop_duplicates(subset=[geneIdentifier])
      secreted = AnnotDF[AnnotDF['Secreted'] == 'Secreted'].drop_duplicates(subset=[geneIdentifier])
      if delaux != 'None':
            SYM = AnnotDF.dropna(subset=['Delaux et al. 2015']).drop_duplicates(subset=[geneIdentifier])
            SYM.to_excel(writer, 'SYM', index=False)            
      ssps.to_excel(writer, 'SSPs', index=False)
      secreted.to_excel(writer, 'Secrted', index=False)
      writer.save()
      

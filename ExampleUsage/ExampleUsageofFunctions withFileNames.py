# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 17:39:29 2021

@author: mclea
"""
import Python_BioInformatics_Library as PBL

#Compiles C. reinhardtii data. Outputs file called 'Creinhardtii_Annotation.xlsx' 
PBL.compileChlamAnnot(outputFile='AnnotationFiles/Creinhardtii_Annotation.xlsx', 
                     trans='AnnotationFiles/ChlamydomonasTranscriptNameConversionBetweenReleases.Mch12b.txt', 
                     geneName='AnnotationFiles/Creinhardtii_281_v5.6.geneName.txt', 
                     description='AnnotationFiles/Creinhardtii_281_v5.6.description.txt', 
                     definition='AnnotationFiles/Creinhardtii_281_v5.6.defline.txt', 
                     annotation='AnnotationFiles/Creinhardtii_281_v5.6.annotation_info.txt', 
                     protFasta='AnnotationFiles/Creinhardtii_281_v5.5.proteinNOaserisk.FA',
                     signalP='AnnotationFiles/Crein_SignalP.csv',
                     Delaux='AnnotationFiles/DelauxChlamAnnot.xlsx',
                     IPC2='AnnotationFiles/IPC2 Output.xlsx',
                     PlantTFDB= 'AnnotationFiles/PlantTFDB_Chlamy.csv')


#Compiles A. nidulans data. Outputs file called 'Aspergillus_Annotation.xlsx' 
PBL.compileMycocosum(outputFile= 'AnnotationFiles/Aspergillus_Annotation', trans='AnnotationFiles/Aspnid1_GeneCatalog_transcripts_20110130.nt.fasta',
                        pep= 'AnnotationFiles/Aspnid1_GeneCatalog_proteins_20110130.aa.fasta', 
                        KOG= 'AnnotationFiles/Aspnid1_GeneCatalog_proteins_20110130_KOG.tab',
                        KEGG= 'AnnotationFiles/Aspnid1_GeneCatalog_proteins_20110130_KEGG.tab',
                        GO= 'AnnotationFiles/Aspnid1_GeneCatalog_proteins_20110130_GO.tab',
                        InterPro= 'AnnotationFiles/Aspnid1_GeneCatalog_proteins_20110130_IPR.tab',
                        SignalP='AnnotationFiles/Anidulans_SignalP.csv',
                        IPC2='AnnotationFiles/IPC2 Output.xlsx',
                        CAZy= 'AnnotationFiles/Asp_CAZymes.xlsx',
                        FTFDB='AnnotationFiles/FTFD_TF_List_Phylym_Ascomycota.csv',
                        Secretome= 'AnnotationFiles/fungSecrete_Anidulans.fasta')

#Compiles N. crassa data. Outputs file called 'Neurospora_Annotation.xlsx'      
PBL.compileMycocosum(outputFile= 'AnnotationFiles/Neurospora_Annotation', trans='AnnotationFiles/Neucr2_GeneCatalog_transcripts_20130412.nt.fasta',
                        pep= 'AnnotationFiles/Neucr2_GeneCatalog_proteins_20130412.aa.fasta', 
                        KOG= 'AnnotationFiles/Neucr2_GeneCatalog_proteins_20130412_KOG.tab',
                        KEGG= 'AnnotationFiles/Neucr2_GeneCatalog_proteins_20130412_KEGG.tab',
                        GO= 'AnnotationFiles/Neucr2_GeneCatalog_proteins_20130412_GO.tab',
                        InterPro= 'AnnotationFiles/Neucr2_GeneCatalog_proteins_20130412_IPR.tab',
                        SignalP='AnnotationFiles/Ncrassa_SignalP.csv',
                        IPC2='AnnotationFiles/IPC2 Output.xlsx',
                        CAZy='AnnotationFiles/Neur_CAZymes.xlsx',
                        FTFDB='AnnotationFiles/FTFD_TF_List_Phylym_Ascomycota.csv',
                        Secretome= 'AnnotationFiles/fungSecrete_Ncrassa.fasta')

#Example venn diagram from .csv comparison
PBL.makeVenn('ExampleUsage/vennInput.csv')  

#Example gene Extraction with SYM pathway extraction
PBL.extractFromCSV(annotationCSV='G:/Shared drives/Hom Lab - Franken Lichens/Data Analysis/Annotation Files and Compilation Code/Test/Creinhardtii_Annotation.xlsx', 
               genesCSV='AnnotationFiles/geneExtract_CHLAM.csv', 
               geneIdentifier='locusName', 
               outputFile='CHLAM_Genes of Interest.xlsx', 
               delaux='yes')         
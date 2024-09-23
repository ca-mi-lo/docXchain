#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import argparse

import numpy as np
import cv2
import datetime
import time
import pytz
import json

import pandas as pd

from modules.file_loading import load_document, load_whole_pdf
from modules.formula_recognition import FormulaRecognition
from pipelines.general_text_reading import GeneralTextReading
from pipelines.table_parsing import TableParsing

from pipelines.document_structurization import DocumentStructurization
from utilities.visualization import *

import os
from pathlib import Path
import logging
import pandas as pd
from langchain_core.documents import Document

def check_species_processed(root_path, 
                            processed_list=['Leptonycteris yerbabuenae_all', 'Leptonycteris nivalis_all', 'Melipona beecheii_all','test species_A','test species_B']):
    species_subfolders = os.listdir(root_path)
    pending_process_species = list(set(species_subfolders)-set(processed_list))
    return pending_process_species 

def check_file_processed(file_path):
    print("comming soon")

def get_list_paths(root_path, 
               input_subfolder_sufix="_bibliografía", 
               output_subfolder = "output"
               ):

    path_dics = []
    
    try: 
        pending_process_species = check_species_processed(root_path)
    except:
        pending_process_species = os.listdir(root_path)

    for species_folder in pending_process_species:
        species_folder_path = Path(root_path,species_folder)
        file_name_list = os.listdir(Path(root_path,species_folder,species_folder+'_bibliografía'))
        for file_name in file_name_list:
            path_dics.append(
                dict(
                    file_input_path = Path(species_folder_path,str(species_folder_path.name)+input_subfolder_sufix,file_name),
                    folder_output_path = Path(species_folder_path,output_subfolder),
                    species_folder = species_folder,
                    file_name = file_name
                )
            )
    return path_dics

def whole_pdf_conversion_example(image_list):

    # configure
    configs = dict()
    
    layout_analysis_configs = dict()
    layout_analysis_configs['from_modelscope_flag'] = False
    layout_analysis_configs['model_path'] = '/home/DocXLayout_231012.pth'  # note that: currently the layout analysis model is NOT from modelscope
    configs['layout_analysis_configs'] = layout_analysis_configs
    
    text_detection_configs = dict()
    text_detection_configs['from_modelscope_flag'] = True
    text_detection_configs['model_path'] = 'damo/cv_resnet18_ocr-detection-line-level_damo'
    configs['text_detection_configs'] = text_detection_configs

    text_recognition_configs = dict()
    text_recognition_configs['from_modelscope_flag'] = True
    text_recognition_configs['model_path'] = 'damo/cv_convnextTiny_ocr-recognition-document_damo'  # alternatives: 'damo/cv_convnextTiny_ocr-recognition-scene_damo', 'damo/cv_convnextTiny_ocr-recognition-general_damo', 'damo/cv_convnextTiny_ocr-recognition-handwritten_damo' 
    configs['text_recognition_configs'] = text_recognition_configs

    formula_recognition_configs = dict()
    formula_recognition_configs['from_modelscope_flag'] = False
    formula_recognition_configs['image_resizer_path'] = '/home/LaTeX-OCR_image_resizer.onnx'
    formula_recognition_configs['encoder_path'] = '/home/LaTeX-OCR_encoder.onnx'
    formula_recognition_configs['decoder_path'] = '/home/LaTeX-OCR_decoder.onnx'
    formula_recognition_configs['tokenizer_json'] = '/home/LaTeX-OCR_tokenizer.json'
    configs['formula_recognition_configs'] = formula_recognition_configs

    # initialize
    document_structurizer = DocumentStructurization(configs)

    # run
    final_result = []
    page_index = 0
    for image in image_list:
        result = document_structurizer(image)

        page_info = {'page': page_index, 'information': result}
        final_result.append(page_info)

        page_index = page_index + 1

    if True:
        print (final_result)

    # release
    document_structurizer.release()

    return final_result

def loop_OCR(root_path, max_files = 100): 
    '''
    Expected folder Structure :

    root_folder/
        species A/
            species A_bibiliografía/
                file_A1.pdf
                file_A2.pdf
            output/
                Doc_A1
                Doc_A2
    
    Note: The subfolders under root_folde define the species-name. 
    '''
    list_paths = get_list_paths(root_path)
    final_results = []

    for file_path_dict in list_paths[0:max_files]:
        pdf_path = file_path_dict.get('file_input_path')
        output_folder = file_path_dict.get('folder_output_path')
        if not os.path.exists(output_folder):
            print("Creating output folder in : {output_folder.parent.name}")
            os.mkdir(output_folder)

        image_list = load_whole_pdf(str(pdf_path))

        try:
            final_result = whole_pdf_conversion_example(image_list)
            
            
        
        except:
            final_result = {'error_species':str(file_path_dict.get('species_folder')), 
                            'error_file': str(file_path_dict.get('file_input_path'))
                            }
            logging.error("Custom_error_msg", exc_info=True)
        
        final_results.append(final_result)
    
    return final_results

def res_to_df_chunks(final_result: list, filter_criteria = ['plain text']) -> Document:
    # 1. to DataFrame and "Explode" for relevant columns
    # 2. Select type of objects, default 'plain text' category
    # 3. Group text into region-polygon-chunks

    
    try: 
        df = pd.DataFrame(final_result)
        cols = ['information','text_list']

        for col in cols:
            #print(col)
            df = df.explode(col).reset_index(drop=True)
            df = df.drop(columns=[col]).join(df[col].apply(pd.Series), rsuffix=f".{col}")

        df['content'] = df['content'].apply(lambda x: x[0] if isinstance(x,list) else '')
        df['region_poly'] = df['region_poly'].apply(lambda x: tuple(x)) # lists are mutable 
        df['content_type'] = df ['content'].apply(lambda x: type(x).__name__)
        
        # 2
        df = df[df.category_name.apply(lambda x: x in filter_criteria)]

        # 3
        aggr_level = ['page', 'region_poly']
        grouped_df = df.groupby(aggr_level)
        # Concatenate the content of the 'content' column with spaces
        df_agg = df.groupby(aggr_level)['content'].apply(lambda x: ' '.join(x)).reset_index()
    
    except:
        return (final_result)

        
    return df_agg

def df_to_doc(df_agg, file_path_dict):
    """Converts a Pandas DataFrame to a list of LangChain Documents with enhanced data handling.

    Args:
        df_agg (pandas.DataFrame): The DataFrame containing the data to be converted.
        file_path_dict (dict): A dictionary containing file paths for various purposes.

    Returns:
        list: A list of LangChain Document objects with page_content and metadata.
    """

    documents = [
        Document(
            page_content=row.get("content"),
            metadata={
                "page": row.get("page"),  # Use get() for potential missing values
                "file_name": file_path_dict.get("file_name"),
                "region_poly": row.get("region_poly"),
                "input_file": str(file_path_dict.get("file_input_path")),
                "species_folder": file_path_dict.get("species_folder"),
                "output_folder": str(Path(file_path_dict.get("folder_output_path"))),  # Convert Path to string for JSON
                "output_file": str(Path(file_path_dict.get("folder_output_path"), file_path_dict.get("file_name").split(".")[0] + ".json"))  # Use get() and string conversion
            }
        )
        for _, row in df_agg.iterrows()
    ]

    return documents

def df_to_dict(df_agg, file_path_dict):
    documents = [ 
        dict(
            page_content=row.get("content"),
            metadata={
                "page": row.get("page"),
                "file_name": file_path_dict.get("file_name"),
                "region_poly": row.get("region_poly"),
                "input_file": str(file_path_dict.get("file_input_path")),
                "species_folder": file_path_dict.get("species_folder"),
                "output_folder": str(Path(file_path_dict.get("folder_output_path"))),
                "output_file": str(Path(file_path_dict.get("folder_output_path"), file_path_dict.get("file_name").split(".")[0] + ".json"))
            }
        )
        for _, row in df_agg.iterrows()
    ]

    return documents

def write_to_json(dfs:list,list_paths, mode = 'override'):
     for res, path_dic in  zip(dfs,list_paths):
          output_folder = path_dic.get('folder_output_path')
          output_file_path = Path(output_folder,
                                   path_dic.get('file_name').split(".")[0]+".json")
               
          if mode == "skip" and os.path.exists(output_file_path):
                continue  # Skip existing file
          
          # if it is a DataFrame, result finished correctly
          if isinstance(res, pd.DataFrame):
               list_of_dicts = df_to_dict(res,path_dic)
               if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
               
               with open (output_file_path,"w") as fp:
                    json.dump(list_of_dicts,fp, indent=2)
          else:
               with open ('./log_errors',"a") as fp:
                              try:
                                   json.dump(res,fp)
                              except:
                                   print("TypeError: Object of type PosixPath is not JSON serializable")

# main routine
def main():
    """
    Description:
     Step 1. check_species_processed: Evaluates at species level if it should be processed
     Step 2. get_list_paths: From the remaining pending species, get paths of files to process
     Step 3. Invoke the OCR model for the previous list in a loop
     Step 4. Transform data into df and aggregate text into polygons (res_to_df_chunks)
     Step 5. Router_output:  If the OCR process finished correctly, generate the (document + path-metadata) in each output folder
     Pending:
     - Logs & Traces
     - Unify output in just one place 
    """

    # parse parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("root_path", help = "specify the path of the folder containing the pdf files", type = str)
    args = parser.parse_args()

    # start
    tz = pytz.timezone('America/Mexico_City')
    now = datetime.datetime.now(tz)
    print (now.strftime("%Y-%m-%d %H:%M:%S"))
    print ("Started!")
    print ('Whole PDF conversion task, only PDF files are supported!')

    # Load whole pdf, no options (for now)
    # image_list & final result are processed together

    final_results = loop_OCR(args.root_path, max_files = 100)

    dfs = [res_to_df_chunks(df) for df in final_results]
    path_list = get_list_paths(args.root_path)
    write_to_json(dfs,path_list)

    # finish
    now = datetime.datetime.now(tz)
    print (now.strftime("%Y-%m-%d %H:%M:%S"))
    print ("Finished!")

    return

if __name__ == "__main__":
    # execute only if run as a script
    # python docXchain.py /home/camilo/Documents/00-Conabio/by_species
    # python3 docXchain.py /home/camilo/Documents/by_species
    main()


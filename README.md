# DocXChain: A Powerful Open-Source Toolchain for Document Parsing and Beyond

## Introduction

Extracting text from a PDF file can be challenging, especially when dealing with scanned documents or images. OCR (Optical Character Recognition) technology is designed to overcome these challenges. It can convert images into text, recognizing individual characters and assembling them into words.

One of the key challenges in text processing is accurately identifying paragraph breaks. While this might seem straightforwar at plain sight, it becomes more complex in formatted documents and specific editorial design context. A line break could indicate the end of a title, subtitle, footer, column break, or even a text bubble. OCR tools are adept at handling these complexities, allowing them to accurately identify and extract meaningful text units.

Another advantage of OCR is its ability to classify different types of text. This means it can distinguish between titles, footers, and main content. By filtering out irrelevant text, OCR helps ensure that only the most pertinent information is processed.

Our current but not single use-case for OCR-extracted text is feeding it into an LLM (Large Language Model) API. By accurately identifying sentence boundaries, OCR can improve the performance of the LLM, as it helps the model to better understand the context and meaning of the text.


## Installation

* Install basic requirements (Python version >= 3.7):

- `pip install -r requirements.txt` . Pinned version of requirements are included in `requirements.txt`. The pinned version were compiled using `pip-tools` on `requirements.in`.
  
- Install tensorflow<=2.12: `pip install tensorflow<=2.12`.

- `pip install torch -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html`

- Install modelscope with cv: `pip install modelscope[cv] -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html`. 


- * Create missing file (if necesary only):
```sh
touch /home/<USERNAME>/.cache/modelscope/hub/._____temp/damo/cv_resnet18_ocr-detection-line-level_damo/.ipynb_checkpoints/configuration-checkpoint.json
```

* Install ImageMagick (needed to load PDFs):
```bash
apt-get update
apt-get install libmagickwand-dev
pip install Wand
sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml  # run this command if the following message occurs: "wand.exceptions.PolicyError: attempt to perform an operation not allowed by the security policy `PDF'"
```

* Download the layout analysis model (a homebrewed model provided by us):
```bash
wget -c -t 100 -P /home/ https://github.com/AlibabaResearch/AdvancedLiterateMachinery/releases/download/v1.2.0-docX-release/DocXLayout_231012.pth
``` 

* Download the formula recognition models (from [RapidLatexOCR](https://github.com/RapidAI/RapidLatexOCR)):
```bash
wget -c -t 100 -P /home/ https://github.com/AlibabaResearch/AdvancedLiterateMachinery/releases/download/v1.6.0-LaTeX-OCR-models/LaTeX-OCR_image_resizer.onnx
wget -c -t 100 -P /home/ https://github.com/AlibabaResearch/AdvancedLiterateMachinery/releases/download/v1.6.0-LaTeX-OCR-models/LaTeX-OCR_encoder.onnx
wget -c -t 100 -P /home/ https://github.com/AlibabaResearch/AdvancedLiterateMachinery/releases/download/v1.6.0-LaTeX-OCR-models/LaTeX-OCR_decoder.onnx
wget -c -t 100 -P /home/ https://github.com/AlibabaResearch/AdvancedLiterateMachinery/releases/download/v1.6.0-LaTeX-OCR-models/LaTeX-OCR_tokenizer.json
```

## How to use it

The program takes a unique parameter, a root-path, to search for pdf's in it. In the first level below the root folder, there are more folders expected.Theses other folders, "species-folders", are very important, since their name will impact the data structure. 
The species folders contain "_bibliografía" subfolders. The actual PDF files should be stored in these subfolders before execution.  See "Expected folder Structure" for a diagram.

###  Expected folder Structure

```python

root_folder/
    species A/
        species A_bibiliografía/
            file_A1.pdf
            file_A2.pdf
        output/
            file_A1.json
            file_A2.json

Note: The subfolders under root_folder defines the species-name. 
```

### Expected Output
In each species-folder an "output" folder will be created. If the process runs successfully, for every pdf found in the "Species X_bibligrafía" folders, a "Species X.json" will be created respectively.

Here an example of an element of the the json file. Each element has the main information "page_content" and it's "metadata".

``` json
{
  "page_content": "Carlos Enrique Ruano lraheta**, Miguel Angel Hernandez Martinez\u2019, Luis Alonso Alas Romero\n...",
  "metadata": {
    "page": 0,
    "file_name": "Ruano-Iraheta et al., 2015.pdf",
    "region_poly": [102, 344, 1117, 344, 1117, 392, 102, 392],
    "input_file": "/home/<USERNAME>/Documents/datasets/by_species/Melipona beecheii/Melipona beecheii_bibliografía/Ruano-Iraheta et al., 2015.pdf",
    "species_folder": "Melipona beecheii",
    "output_folder": "/home/<USERNAME>/Documents/datasets/by_species/Melipona beecheii/output",
    "output_file": "/home/<USERNAME>/Documents/datasets/by_species/Melipona beecheii/output/Ruano-Iraheta et al.json"
  }
}
```
#### Glossary

* **page_content** (string): The extracted text content of the current page within the processed document.  
* *metadata*:
* * **page** (integer): The zero-based page number within the input document that this entry corresponds to (starting from 0).  
* * **file_name** (string): The original filename of the input document from which this data was extracted.  
* * **region_poly** (list of integers): A list of eight integers representing a polygon that defines the bounding box around the extracted text content on the page. Used as aggregation granularity for the page_content.  
* * **input_file** (string): The full path to the original input document that was processed.  
* * **species_folder** (string): The folder name within the output directory that corresponds to the species the document is related to (e.g., "Melipona beecheii").  
* * **output_folder** (string): The full path to the output directory where the processed data is stored.  
* * **output_file** (string): The full path to the current JSON output file itself. This provides a reference point within the overall output structure.  


## Run the code (DocXchain.py)

The original examle.py file was modified to accept a single parameter, the 'root_folder' which is expected to contain pdf files (images and text based) to convert them into json files.
```bash
python docXchain.py <root_folder>
```

### What the code does
    Step 1. check_species_processed: Evaluates at species level if it should be processed
    Step 2. get_list_paths: From the remaining pending species (See "Expected folder Structure), get paths of files to process
    Step 3. Invoke the OCR model for the previous list in a loop
    Step 4. Transform data into df and aggregate text into polygons
    Step 5. Router_output:  If the OCR process finished correctly, generate the (document + path-metadata) in each output folder


### Defaults

Not programed as an arguments. If needed, change parameters in **docXChain.py**

- max_files = 100. The minimum length of texts to process helps to avoid short and maybe not relevant chunks of text. 
- Default: 'plain text'. The OCR detects and differenciates kinds of text-polygons: 'plain text','header',footer', etc.
- check_species_processed = List of species-folders to skip to avoid reprecess

## *License*
DocXChain is released under the terms of the [Apache License, Version 2.0](LICENSE).

### Original Repository

This repository is an apdaptation of [DocXchain](https://github.com/AlibabaResearch/AdvancedLiterateMachinery).
The original repository has a wider scope, allowing for more specific tasks like focusing on particular document sections or converting formulas and tables to LaTeX. It can also handle images, while our version is specifically designed for PDF files.

```
@article{DocXChain2023,
  title={{DocXChain: A Powerful Open-Source Toolchain for Document Parsing and Beyond}},
  author={Cong Yao},
  journal={ArXiv},
  year={2023}
  url={https://arxiv.org/abs/2310.12430}
}
```


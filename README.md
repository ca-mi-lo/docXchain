# DocXChain: A Powerful Open-Source Toolchain for Document Parsing and Beyond

## Updated notes on installation

- Pinned version of requirements are included in `requirements.txt`. The pinned 
  version were compiled using `pip-tools` on `requirements.in`.
- Install modelscope with cv: `pip install modelscope[cv] -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html`. 
  This instruction also install torch, if there is an error about torch install 
  before 
  ```
  pip install torch -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
  ```
- Install tensorflow<=2.12: `pip install tensorflow<=2.12`.
- Create missing file:
```sh
touch /home/<USERNAME>/.cache/modelscope/hub/._____temp/damo/cv_resnet18_ocr-detection-line-level_damo/.ipynb_checkpoints/configuration-checkpoint.json
```

## Docker image

A docker image can be created using `docker/Dockerfile`:
```
docker build -t docx:1 -f docker/Dockerfile .
```

## Introduction

<font color=#FFA500 size=3> ***"Make Every Unstructured Document Literally Accessible to Machines"*** </font>

Extracting text from a PDF file can be challenging, especially when dealing with scanned documents or images. OCR (Optical Character Recognition) technology is designed to overcome these challenges. It can convert images into text, recognizing individual characters and assembling them into words.

One of the key challenges in OCR is accurately identifying paragraph breaks. While this might seem straightforward for plain text, it becomes more complex in formatted documents and specific editorial desing context. A line break could indicate the end of a title, subtitle, footer, column break, or even a text bubble. OCR tools are adept at handling these complexities, allowing them to accurately identify and extract meaningful text units.

Another advantage of OCR is its ability to classify different types of text. This means it can distinguish between titles, footers, and main content. By filtering out irrelevant text, OCR helps ensure that only the most pertinent information is processed.

Our current but not single use case for OCR-extracted text is feeding it into an LLM (Large Language Model) API. By accurately identifying sentence boundaries, OCR can improve the performance of the LLM, as it helps the model to better understand the context and meaning of the text.


## Repositorio Original

Este repositorio es una adaptación de este otro: [DocXchain](https://github.com/AlibabaResearch/AdvancedLiterateMachinery).
El alcance el repocitorio original es más aplio, ya que puede enfocarse en determinadoas partes del documentos o enfocarse en detectar fórmulas y tablas para traducirlas a código latex, por ejemplo, así como procesar imágenes, mientras que nostros suponemos que se tratan siempre de achivos en formato pdf.


## Installation

* Install basic requirements (Python version >= 3.7):

```
pip install -r requirements.txt
```

* **[Important]** Install ModelScope as well as related frameworks and libraries (such as PyTorch and TensorFlow). Please refer to the [GitHub homepage of ModelScope](https://github.com/modelscope/modelscope) for more details regarding the installation instructions.

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

## Run the code (DocXchain.py)


The original examle.py file was modified to accept a single parameter, the 'root_folder' which is expected to contain pdf files (images and text based) to convert them into json files.
```bash
python docXchain.py <root_folder>
```

### What the code does
    Step 1. check_species_processed: Evaluates at species level if it should be processed
    Step 2. get_list_paths: From the remaining pending species (See "Expected folder Structure), get paths of files to process
    Step 3. Invoke the OCR model for the previous list in a loop
    Step 4. Transform data into df and aggregate text into polygons (res_to_df_chunks)
    Step 5. Router_output:  If the OCR process finished correctly, generate the (document + path-metadata) in each output folder


 
###  Expected folder Structure

```python

root_folder/
    species A/
        species A_bibiliografía/
            file_A1.pdf
            file_A2.pdf
        output/
            Doc_A1
            Doc_A2

Note: The subfolders under root_folder defines the species-name.
```

## Inference

One can perform inference using the `example.py` script. It can be run as follows:
```bash
python example.py general_text_reading <document_file_path> <output_file_path>  # task: general text reading (dump supports both image and JSON file)
python example.py table_parsing <document_file_path> <output_file_path>  # task: table parsing  (dump supports both image and JSON file)
python example.py formula_recognition  <document_file_path> <output_file_path>  # task: formula recognition (dump supports only JSON file)
python example.py document_structurization <document_file_path> <output_file_path>  # task: document structurization  (dump supports both image and JSON file)
python example.py whole_pdf_conversion <document_file_path> <output_file_path>  # task: whole PDF conversion, i.e., converting all pages of a PDF file into an organized JSON structure (dump supports only JSON file)
``` 
```sh
python example.py whole_pdf_conversion /papers/Hensley_Wilkins.pdf output/test2.json
``

## Citation

If you find our work beneficial, please cite:

```
@article{DocXChain2023,
  title={{DocXChain: A Powerful Open-Source Toolchain for Document Parsing and Beyond}},
  author={Cong Yao},
  journal={ArXiv},
  year={2023}
  url={https://arxiv.org/abs/2310.12430}
}
```

## *License*

DocXChain is released under the terms of the [Apache License, Version 2.0](LICENSE).

```
DocXChain is a toolchain for document parsing and the code and models herein created by the authors from Alibaba can only be used for research purpose.
Copyright (C) 1999-2023 Alibaba Group Holding Ltd. 

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

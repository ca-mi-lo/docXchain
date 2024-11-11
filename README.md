# DocXChain: A Powerful Open-Source Toolchain for Document Parsing and Beyond

## Introduction

Extracting text from a PDF file can be challenging, especially when dealing with scanned documents or images. OCR (Optical Character Recognition) technology is designed to overcome these challenges. It can convert images into text, recognizing individual characters and assembling them into words.

One of the key challenges in OCR is accurately identifying paragraph breaks. While this might seem straightforward for plain text, it becomes more complex in formatted documents and specific editorial desing context. A line break could indicate the end of a title, subtitle, footer, column break, or even a text bubble. OCR tools are adept at handling these complexities, allowing them to accurately identify and extract meaningful text units.

Another advantage of OCR is its ability to classify different types of text. This means it can distinguish between titles, footers, and main content. By filtering out irrelevant text, OCR helps ensure that only the most pertinent information is processed.

Our current but not single use-case for OCR-extracted text is feeding it into an LLM (Large Language Model) API. By accurately identifying sentence boundaries, OCR can improve the performance of the LLM, as it helps the model to better understand the context and meaning of the text.


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

### Updated notes on installation

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

### Docker image

A docker image can be created using `docker/Dockerfile`:
```
docker build -t docx:1 -f docker/Dockerfile .
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
    Step 4. Transform data into df and aggregate text into polygons
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


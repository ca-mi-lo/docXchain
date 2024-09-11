FROM python:3.10-bookworm

ENV PYTHON_ENV=/docx/.venv
ARG UID=1000
ARG GID=1000

RUN apt-get update && apt-get install -y libmagickwand-dev \
  && rm -rf /var/lib/apt/lists/* \
  && sed -i '/disable ghostscript format types/,+6d' /etc/ImageMagick-6/policy.xml

WORKDIR /docx
RUN groupadd -g ${GID} conabio_ds
RUN useradd -u ${UID} -g ${GID} -d /docx conabio_ds

RUN chown -R ${UID}:${GID} /docx
USER conabio_ds

RUN python -m venv $PYTHON_ENV
ENV PATH="$PYTHON_ENV/bin:$PATH"
COPY ./requirements.txt ./ 
RUN pip install -r requirements.txt
RUN pip install torch -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
RUN pip install modelscope[cv] -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
RUN pip install "tensorflow<=2.12"
RUN pip install Wand
RUN mkdir models \
  && wget -c -t 100 -P models/ https://github.com/AlibabaResearch/AdvancedLiterateMachinery/releases/download/v1.2.0-docX-release/DocXLayout_231012.pth \
  && wget -c -t 100 -P models/ https://github.com/AlibabaResearch/AdvancedLiterateMachinery/releases/download/v1.6.0-LaTeX-OCR-models/LaTeX-OCR_image_resizer.onnx \ 
  && wget -c -t 100 -P models/ https://github.com/AlibabaResearch/AdvancedLiterateMachinery/releases/download/v1.6.0-LaTeX-OCR-models/LaTeX-OCR_encoder.onnx \ 
  && wget -c -t 100 -P models/ https://github.com/AlibabaResearch/AdvancedLiterateMachinery/releases/download/v1.6.0-LaTeX-OCR-models/LaTeX-OCR_decoder.onnx \ 
  && wget -c -t 100 -P models/ https://github.com/AlibabaResearch/AdvancedLiterateMachinery/releases/download/v1.6.0-LaTeX-OCR-models/LaTeX-OCR_tokenizer.json
RUN mkdir -p /docx/.cache/modelscope/hub/._____temp/damo/cv_resnet18_ocr-detection-line-level_damo/.ipynb_checkpoints/ \
  && touch .cache/modelscope/hub/._____temp/damo/cv_resnet18_ocr-detection-line-level_damo/.ipynb_checkpoints/configuration-checkpoint.json

COPY . .

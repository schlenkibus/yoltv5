FROM yolov5-30xx:latest

#https://askubuntu.com/questions/909277/avoiding-user-interaction-with-tzdata-when-installing-certbot-in-a-docker-contai
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

RUN apt update
RUN /opt/conda/bin/python -m pip install --upgrade pip
RUN conda install -c conda-forge gdal osmnx=0.12 scikit-image statsmodels
RUN pip install torchsummary utm numba jinja2==2.10 rasterio

COPY yoltv5 /yoltv5
COPY configs /configs
COPY use-cases /use-cases

RUN pip install -r /yoltv5/yolov5/requirements.txt
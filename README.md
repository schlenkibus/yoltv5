# YOLTv5 #

![Alt text](/results/__examples/header.jpg?raw=true "")
 
 YOLTv5 rapidly detects objects in arbitrarily large aerial or satellite images that far exceed the ~600×600 pixel size typically ingested by deep learning object detection frameworks. 
  
 YOLTv5 builds upon [YOLT]( https://github.com/avanetten/yolt) and [SIMRDWN]( https://github.com/avanetten/simrdwn), and updates these frameworks to use the [YOLOv5](https://github.com/ultralytics/yolov5) version of the [YOLO](https://pjreddie.com/darknet/yolo/) object detection family.  This repository has generally similar performance to the [Darknet](https://pjreddie.com/darknet/)-based [YOLTv4](https://github.com/avanetten/yoltv4) repository.  For those users who prefer a [PyTorch](https://pytorch.org) backend, however, we provide YOLTv5.  
 
 Below, we provide examples of how to use this repository with the open-source [SpaceNet](https://spacenet.ai) dataset. 
 
____
## Running YOLTv5

docker build . -t yoltv5
nvidia-docker run --ipc=host --gpus=all -p 5000:5000 $hostOutDir:/out $hostDataDir:/data -it yoltv5

idea is to run the docker container with and persistent shared volume called /data and /out
data is meant as a base layer of models and test-data
out is an archive of artefacts the training and interference produced

___

### 0. Installation (Preliminary)

YOLTv5 is built to execute on a GPU-enabled machine. 

	cd yoltv5/yolov5
	pip install -r requirements.txt 

	# update with geo packages
	conda install -c conda-forge gdal
	conda install -c conda-forge osmnx=0.12 
	conda install  -c conda-forge scikit-image
	conda install  -c conda-forge statsmodels
	pip install torchsummary
	pip install utm
	pip install numba
	pip install jinja2==2.10

___

### 1. Train

Training preparation is accomplished via [prep_train.py](https://github.com/avanetten/yoltv5/blob/main/yoltv5/prep_train.py).  To train a model, run:

	cd /yoltv5
    python yolov5/train.py --img 640 --batch 16 --epochs 100 --data yoltv5_train_vehicles_8cat.yaml --weights yolov5l.pt

___

### 2. Test

Simply edit [yoltv5_test_vehicles_8cat.yaml](https://github.com/avanetten/yoltv5/blob/main/configs/yoltv5_test_vehicles_8cat.yaml) to point to the appropriate locations, then run the _test.sh_ script:

	cd yoltv5
	./test.sh ../configs/yoltv5_test_vehicles_8cat.yaml


Outputs will look something like the figure below (cars=green, trucks=red, buses=blue):

![Alt text](/results/__examples/khartoum_example0.jpg?raw=true "")

python inference-on-model.py -i /data/test-tif/Max_20200722_Trans_transparent_mosaic_group1.tif -o /out/zitest -y /configs/yoltv5_test_flowers_base_tif.yaml -m /data/BEST-YOLT.pt
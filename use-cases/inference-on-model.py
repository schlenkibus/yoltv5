#usage: modelpath, outputpath, inputfile

#!/usr/bin/python

from genericpath import exists
import shutil, time
import sys, getopt, yaml
from time import time
import os
import subprocess
from distutils.dir_util import copy_tree


def touch(fname):
    try:
        os.utime(fname, None)
    except OSError:
        open(fname, 'a').close()

def main(argv):
    inDirectory = ''
    outputdir = ''
    modelfile = ''
    base_yaml = ''
    test_application_path = ''
    base_yolt_path = ''
    num_plots = 4

    #parse arguments to this script
    try:
        opts, args = getopt.getopt(argv,"hi:o:m:b:t:y:p:",["input=","output=","model=","baseyaml=","test_application_path=","yolt_path=","plots="])
    except getopt.GetoptError:
        print(f"inference-on-model.py -i <inputfile> -o <outputdir> -m <model> -b <base_yaml_path> -t <test_application_path> -y <yolt_path> -p <plots>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(f"inference-on-model.py -i <inputfile> -o <outputdir> -m <model> -b <base_yaml_path> -t <test_application_path> -y <yolt_path> -p <plot_all>")
            sys.exit()
        elif opt in ("-i", "--input"):
            inDirectory = arg
        elif opt in ("-o", "--output"):
            outputdir = arg
        elif opt in ("-m", "--model"):
            modelfile = arg
        elif opt in ("-b", "--baseyaml"):
            base_yaml = arg
        elif opt in ("-t", "--test_application_path"):
            test_application_path = arg
        elif opt in ("-y", "--yolt_path"):
            base_yolt_path = arg
        elif opt in ("-p", "--plots"):
            num_plots = int(arg)

    print(f"Input file/dir is {inDirectory}")
    print(f"Model file is {modelfile}")
    print(f"Output directory is {outputdir}")
    print(f"Baseyaml file is {base_yaml}")
    print(f"Test application path is {test_application_path}")
    print(f"Number of plots is {num_plots}")

    timestamp = str(int(time()))
    data_root = outputdir
    test_run_dir = f"{outputdir}/{timestamp}"
    test_im_dir = f"{test_run_dir}/input"
    outdir_slice_root = f"{test_run_dir}/yoltv5"
    outdir_slice_ims = f"{test_run_dir}/images_slice"
    outdir_slice_txt = f"{test_run_dir}/txt"
    outpath_test_txt = f"{test_run_dir}/test.txt"
    inference_yaml = f"{test_run_dir}/inference.yaml"
    pred_out_dir = f"{test_run_dir}/prediction"
    yolov5_outdirectory = f"{test_run_dir}/yolov5-detection"
    outname_infer = timestamp

    #validate files exist
    if not os.path.exists(base_yaml):
        print(f"Yaml File: {base_yaml} does not exists")
        sys.exit(3)

    isdirectory = False
    fileType = None

    jpgTypes = ['jpg', 'jpeg', 'JPG', 'JPEG']
    pngTypes = ['png', 'PNG']

    if os.path.isdir(inDirectory):
        isdirectory = True
        #check if all files have the same extension
        fileTypes = set()
        
        #rename all jpg variants to one literal extension
        for file in os.listdir(inDirectory):
            if file.endswith(tuple(jpgTypes)):
                os.rename(f"{inDirectory}/{file}", f"{inDirectory}/{file.split('.')[0]}.jpg")
            if file.endswith(tuple(pngTypes)):
                os.rename(f"{inDirectory}/{file}", f"{inDirectory}/{file.split('.')[0]}.png")

        #collect all file extensions
        for root, dirs, files in os.walk(inDirectory):
            for file in files:
                fileTypes.add(file.split(".")[-1])

        if len(fileTypes) > 1:
            raise Exception("Directory contains files of different types")

        if len(fileTypes) == 0:
            raise Exception("Directory contains no files")

        fileType = fileTypes.pop()
    

    if not os.path.exists(inDirectory) and not isdirectory:
        print(f"Inputfile: {inDirectory} does not exists")
        sys.exit(3)

    if not isdirectory:
        fileType = inDirectory.split(".")[-1]

    if os.path.exists(outdir_slice_ims):
        print(f"Slice_directory: {outdir_slice_ims} exists")
        sys.exit(3)

    if os.path.exists(outdir_slice_txt):
        print(f"Txt_directory: {outdir_slice_txt} exists")
        sys.exit(3)

    if os.path.exists(outpath_test_txt):
        print(f"Txt with slices: {outpath_test_txt} exists")
        sys.exit(3)

    #prepare output directory
    os.makedirs(outputdir, exist_ok=True)
    os.makedirs(test_im_dir, exist_ok=True)
    os.makedirs(outdir_slice_root, exist_ok=True)
    os.makedirs(pred_out_dir, exist_ok=True)

    #copy input file or files to slice input
    if isdirectory:
        copy_tree(inDirectory, test_im_dir)
    else:
        shutil.copy2(inDirectory, test_im_dir)

    #read base yaml
    try:
        with open(base_yaml, 'r') as base_file:
            data = yaml.safe_load(base_file)
            #replace arguments of interest
            data['data_root'] = data_root
            data['test_im_dir'] = test_im_dir
            data['outdir_slice_root'] = outdir_slice_root
            data['outdir_slice_ims'] = outdir_slice_ims
            data['outdir_slice_txt'] = outdir_slice_txt
            data['outpath_test_txt'] = outpath_test_txt
            data['weights_file'] = modelfile
            data['outname_infer'] = outname_infer
            data['yolov5_outdirectory'] = yolov5_outdirectory
            data['yoltv5_path'] = base_yolt_path
            data['n_plots'] = num_plots

            if isdirectory or fileType != None:
                fileType = f".{fileType}"
                data['im_ext'] = fileType
                data['out_ext'] = fileType
                data['chip_ext'] = fileType

            with open(inference_yaml, 'w') as out_file:
                #save yaml to output dir
                outputs = yaml.dump(data, out_file)
            print(f"Saved config yaml to {inference_yaml}.")

    except yaml.YAMLError as exception:
        print("interference-on-model.py:154 " + exception)
        sys.exit(4)

    print("Running inference!")
    startTime = time()
    ret = os.system(f"python {test_application_path} {inference_yaml}")
    endTime = time()
    print(f"Done running inference! Time taken: {endTime - startTime} seconds. Exit Code: {ret}")

if __name__ == "__main__":
    main(sys.argv[1:])
#usage: modelpath, outputpath, inputfile

#!/usr/bin/python

import shutil
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
    inputfile = ''
    outputdir = ''
    modelfile = ''
    base_yaml = ''

    #parse arguments to this script
    try:
        opts, args = getopt.getopt(argv,"hi:o:m:y:",["input=","output=","model=","baseyaml="])
    except getopt.GetoptError:
        print(f"inference-on-model.py -i <inputfile> -o <outputdir> -m <model> -y <base_yaml_path>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(f"inference-on-model.py -i <inputfile> -o <outputdir> -m <model>")
            sys.exit()
        elif opt in ("-i", "--input"):
            inputfile = arg
        elif opt in ("-o", "--output"):
            outputdir = arg
        elif opt in ("-m", "--model"):
            modelfile = arg
        elif opt in ("-y", "--baseyaml"):
            base_yaml = arg

    print(f"Input file is {inputfile}")
    print(f"Model file is {modelfile}")
    print(f"Output directory is {outputdir}")
    print(f"Baseyaml file is {base_yaml}")


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

    if os.path.isdir(inputfile):
        isdirectory = True

    if not os.path.exists(inputfile) and not isdirectory:
        print(f"Inputfile: {inputfile} does not exists")
        sys.exit(3)

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
        copy_tree(inputfile, test_im_dir)
    else:
        shutil.copy2(inputfile, test_im_dir)

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

            with open(inference_yaml, 'w') as out_file:
                #save yaml to output dir
                outputs = yaml.dump(data, out_file)
            print(f"Saved config yaml to {inference_yaml}.")

    except yaml.YAMLError as exception:
        print(exception)
        sys.exit(4)

    print("Running inference!")
    #continue to start the approrpiate script from yoltv5 with the generated yaml file
    ret = os.system(f"python /yoltv5/test.py {inference_yaml}")
    #app = subprocess.run(["python", "/yoltv5/test.py", inference_yaml], shell=True)
    #print("out:" + str(app.stdout))
    #print("err:" + str(app.stderr))
    print(f"Done running inference! Exit Code: {ret}")

if __name__ == "__main__":
    main(sys.argv[1:])
#usage: modelpath, outputpath, inputfile

#!/usr/bin/python

import shutil
import sys, getopt, yaml

import os

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
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
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


    data_root = outputdir
    test_img_dir = f"{outputdir}/input"
    outdir_slice_root = f"{outputdir}/yoltv5"
    outdir_slice_ims = f"{outputdir}/images_slice"
    outdir_slice_txt = f"{outputdir}/txt"
    outpath_test_txt = f"{outputdir}/test.txt"

    #validate files exist
    if not os.path.exists(base_yaml):
        print(f"Yaml File: {base_yaml} does not exists")
        sys.exit(3)

    if not os.path.exists(inputfile):
        print(f"Inputfile: {inputfile} does not exists")
        sys.exit(3)

    #prepare output directory
    os.mkdir(outputdir, exists_okay=True)
    os.mkdir(test_img_dir, exists_okay=True)
    os.mkdir(outdir_slice_root, exists_okay=True)
    os.mkdir(outdir_slice_ims, exists_okay=True)
    os.mkdir(outdir_slice_txt, exists_okay=True)
    
    #touch files needed -> test.txt
    touch(outpath_test_txt)

    #copy input file to slice input
    shutil.copy2(inputfile, test_img_dir)


    #read base yaml
    try:
        with open(base_yaml, 'r') as base_file:
            data = yaml.safe_load(base_file)
            #replace arguments of interest
            data['data_root'] = data_root
            data['test_img_dir'] = test_img_dir
            data['outdir_slice_root'] = outdir_slice_root
            data['outdir_slice_ims'] = outdir_slice_ims
            data['outdir_slice_txt'] = outdir_slice_txt
            data['outpath_test_txt'] = outpath_test_txt

            with open(f"{outputdir}/inference.yaml", 'w') as file:
                #save yaml to output dir
                outputs = yaml.dump(data, file)
                print(outputs)

    except yaml.YAMLError as exception:
        print(exception)
        sys.exit(4)

    #continue to start the approrpiate script from yoltv5 with the generated yaml file

if __name__ == "__main__":
    main(sys.argv[1:])
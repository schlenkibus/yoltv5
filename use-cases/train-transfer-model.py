#input: model, yaml -> relative to /data/

#-o /out/train -y /configs/yoltv5_train_flowers_base.yaml -m /data/BEST-YOLT.pt

import getopt
import subprocess
import sys


def main(argv):
    outputdir = ''
    modelfile = ''
    base_yaml = ''
    wandb_key = ''

    #parse arguments to this script
    try:
        opts, args = getopt.getopt(argv,"ho:m:y:w:",["output=","model=","baseyaml=","wandbkey="])
    except getopt.GetoptError:
        print(f"train-transfer-model.py -o <outputdir> -m <model> -y <base_yaml_path> -w <wandb_api_key>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(f"train-transfer-model.py -o <outputdir> -m <model> -y <base_yaml_path> -w <wandb_api_key>")
            sys.exit()
        elif opt in ("-o", "--output"):
            outputdir = arg
        elif opt in ("-m", "--model"):
            modelfile = arg
        elif opt in ("-y", "--baseyaml"):
            base_yaml = arg
        elif opt in ("-w", "--wandbkey"):
            wandb_key = arg

    print(f"Model file is {modelfile}")
    print(f"Output directory is {outputdir}")
    print(f"Baseyaml file is {base_yaml}")
    print(f"Wandb key is {wandb_key}")
    app = subprocess.run(["python", "/yoltv5/train.py", base_yaml], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("out:" + str(app.stdout))
    print("err:" + str(app.stderr))
    print("Done running inference!")
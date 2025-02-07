#import flask
from flask import Flask, render_template, request, redirect, url_for, send_file
import sys
import getopt
import uuid
import os
import shutil
import zipfile

class ApplicationState:
    def __init__(self, workDirPath, modelPath, resultPath):
        self.workDirPath = workDirPath
        self.modelPath = modelPath
        self.resultPath = resultPath
        self.inInterference = False

        if not os.path.isfile(self.modelPath):
            raise Exception("Model path does not exist")
        
        if not os.path.isdir(self.workDirPath):
            os.makedirs(self.workDirPath)

        if not os.path.isdir(self.resultPath):
            os.makedirs(self.resultPath)

    def processUploadedFileOrZip(self, zipFileOrFile, generatePlots, loggerFN):
        loggerFN(f"processUploadedFileOrZip: {zipFileOrFile}")

        if zipFileOrFile.endswith(".zip"):
            loggerFN("Zip file")
            zipFile = zipFileOrFile
        else:
            imageFile = zipFileOrFile
            zipFile = None

        if self.inInterference:
            return "process running already"

        #create tmp directory to unzip to
        tmpDir = f"{self.workDirPath}/{str(uuid.uuid4())}"
        os.makedirs(tmpDir)
        loggerFN(f"tmpDir: {tmpDir} exits: {os.path.isdir(tmpDir)}")

        if zipFile is not None:
            with zipfile.ZipFile(zipFile, 'r') as zip_ref:
                zip_ref.extractall(tmpDir)
        else:
            shutil.copy(imageFile, tmpDir)


        self.inInterference = True
        ret = os.system(f"python3 /use-cases/inference-on-model.py -i {tmpDir} -o {self.resultPath} -m {self.modelPath} -b /configs/yoltv5_test_flowers_base.yaml -y / -t /yoltv5/test.py")

        #delete tmp directory
        shutil.rmtree(tmpDir)

        timestamp = 0
        for root, dirs, files in os.walk(self.resultPath):
            try:
                timestamp = max(timestamp, int(root.split("/")[-1]))
            except:
                pass
        resultPath = f"{self.resultPath}/{timestamp}"

        #path to geojson directory: resultPath/yolov5detection/results/<timestamp>/geojsons_geo_0p2
        #create zip with geo-jsons
        geoJsonPath = f"{resultPath}/yolov5-detection/results/{timestamp}/geojsons_geo_0p2"
        plotsPath = f"{resultPath}/yolov5-detection/results/{timestamp}/pred_plots_0p2"
        plotInfix = ""
        if generatePlots:
            plotInfix = "and-plots-"
        outZipPath = f"{self.resultPath}/geojsons-{plotInfix}{zipFileOrFile}-{timestamp}.zip"
        print(geoJsonPath)
        with zipfile.ZipFile(outZipPath, 'w') as zip_ref:
            for root, dirs, files in os.walk(geoJsonPath):
                for file in files:
                    print(f"root: {root}, file: {file}")
                    zip_ref.write(f"{root}/{file}", f"json/{file}")
            
            if generatePlots:
                for root, dirs, files in os.walk(plotsPath):
                    for file in files:
                        print(f"root: {root}, file: {file}")
                        zip_ref.write(f"{root}/{file}", f"plots/{file}")

        #check if zip was written
        if not os.path.isfile(outZipPath):
            return "could not create zip file at " + outZipPath

        self.inInterference = False
        return outZipPath

def main(args):
    #parse arguments
    modelPath = ""
    resultPath = ""
    workDirPath = ""

    try:
        opts, args = getopt.getopt(args, "m:r:w:", ["model=", "result=", "workdir="])
    except getopt.GetoptError:
        print("app.py -m <modelPath> -r <resultPath> -w <workDirPath>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-m":
            modelPath = arg
        elif opt == "-r":
            resultPath = arg
        elif opt == "-w":
            workDirPath = arg

    app.app_ctx_globals_class.state = ApplicationState(workDirPath, modelPath, resultPath)
    app.run(host='0.0.0.0', debug=True)

app = Flask(__name__)

#add default route
@app.route('/')
def index():
    return send_file('/use-cases/index.html')

@app.route('/ls/<id>')
def ls(id):
    path = f"/out/results/{id}/inference.yaml"
    return send_file(path)

#upload route
@app.route('/uploader', methods=['POST'])
def upload():
    if request.method == 'POST':
        app.logger.info(f"upload: {request.form}")

        generatePlots = request.form.get('download_plots') == "download_plots"

        f = request.files['file']
        
        f.save(f.filename)
        res = app.app_ctx_globals_class.state.processUploadedFileOrZip(f.filename, generatePlots, lambda x: app.logger.info(f"LOG: {x}"))

        if os.path.isfile(res):
            return send_file(res)
        else:
            return res

if __name__ == "__main__":
    main(sys.argv[1:])

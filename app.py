import os
import subprocess
import sys
import logging
import shutil
from flask import Flask, jsonify, render_template, request
from werkzeug import secure_filename
import re
from datetime import datetime

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['TEMP_FOLDER'] = '/tmp'
app.config['OCR_OUTPUT_FILE'] = 'ocr'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'jpeg', 'gif', 'tif', 'tiff'])

# import our OCR function
from ocr_core import ocr_core
UPLOAD_FOLDER = '/static/uploads/'
#  our extract data function
def getrawdate(ocr_dump_text):
    
    ocr_dump_text=ocr_dump_text.upper()
    extracted_date=""
    try:                                                            
        match = re.search(r'(\d{1,4}([.\-\\/])\d{1,2}([.\-\\/])\d{1,4})',ocr_dump_text)
        extracted_date=match.group(1)
    except:
        extracted_date=ocr_dump_text    
        try:
            match = re.search(r'(\d{1,4}([.\-\\/])\D{1,3}([.\-\\/])\d{1,4})',ocr_dump_text)
            extracted_date=match.group(1)
        except:
            extracted_date=ocr_dump_text  
    extracted_date=extracted_date.replace("/","-")
    extracted_date=extracted_date.replace("\\","-")
    return extracted_date

def getdate(extracted_date):       #Its hard to recognize DD/MM/YY or MM/DD/YY in some cases so it will assume dd/mm/yy unless values are outside expected range 
    try:
        my_date= datetime.strptime(extracted_date, "%d-%m-%Y")       
    except:
        
        try:
            my_date= datetime.strptime(extracted_date, "%d-%m-%y")       
        except:
            
            try:
                my_date= datetime.strptime(extracted_date, "%m-%d-%Y")       
            except:
                
                try:
                    my_date= datetime.strptime(extracted_date, "%m-%d-%y")       
                except:
                    
                    try:
                        my_date= datetime.strptime(extracted_date, "%d-%b-%Y")       
                    except:
                        
                        try:
                            my_date= datetime.strptime(extracted_date, "%d-%b-%y")       
                        except:
                            my_date="null"
            
    
    return my_date

@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/upload', methods = ['GET','POST'])
def upload_page():
    if request.method == 'POST':
        # check if there is a file in the request
        if 'file' not in request.files:
            return render_template('upload.html', msg='No file selected')
        file = request.files['file']
        # if no file is selected
        if file.filename == '':
            return render_template('upload.html', msg='No file selected')

        if file and allowed_file(file.filename):

            # call the OCR function on it
            ocr_dump_text = ocr_core(file)
            extracted_date=getrawdate(ocr_dump_text)
            extracted_text=getdate(extracted_date).date()
            # extract the text and display it
            return render_template('upload.html',
                                   msg='Successfully processed',
                                   extracted_text=extracted_text,
                                   img_src=UPLOAD_FOLDER + file.filename)
    elif request.method == 'GET':
        return render_template('upload.html')

if __name__ == '__main__':
  app.run(debug=True)

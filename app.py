import os
from flask import Flask, render_template, request
import re
from datetime import datetime

# import our OCR function
from ocr_core import ocr_core

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

# define a folder to store and later serve the images
UPLOAD_FOLDER = '/static/uploads/'

# allow files of a specific type
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)

# function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# route and function to handle the home page
@app.route('/')
def home_page():
    return render_template('index.html')

# route and function to handle the upload page
@app.route('/upload', methods=['GET', 'POST'])
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
    app.run()
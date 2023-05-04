import tensorflow
from keras.models import load_model
import numpy as np
from keras.utils import load_img
import os
from keras.utils import img_to_array
from googletrans import Translator
from flask import Flask, render_template, jsonify, request


#works with this yellow warning
from tensorflow.keras.applications.resnet50 import preprocess_input

app = Flask(__name__, template_folder='template')


def translate_func(r,lang):
    
    # create an instance of the Translator class
    translator = Translator(service_urls=['translate.google.co.in'])

    # English text to be translated
    english_text =r

    try:
        # translate the text to Kannada
        kannada_translation = translator.translate(text=english_text, dest=lang)

        # print the translated text
        #print("English Text: ", english_text)
        return kannada_translation.text.encode('utf-8').decode('utf-8')
        
    
    except Exception as e:
        print("Translation Error:", e)


from pymongo import MongoClient
client = MongoClient("mongodb://mfrt:YfkCgmLy4CtkIycY9HrCNueXrB6gEFJEyWHt8mUTewrGCymuYp2kPQzE8XclUW4VupkhYCdosOCCACDbnH27Zw==@mfrt.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@mfrt@&serverSelectionTimeoutMS=60000")
db = client["remedies"]
collection = db["collection1"]
        
        
        
model = load_model('RESNET50_PLANT_DISEASE(96%).h5',compile=False)


@app.route('/')
def index_view():
    return render_template('index.html')

@app.route('/ind',methods=['GET','POST'])
def ind():
    return render_template('ind.html')


#Allow files with extension png, jpg and jpeg
ALLOWED_EXT = set(['JPG' ,'jpg', 'jpeg' , 'png'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT
           
# Function to load and prepare the image in right shape
def read_image(filename):
    img = load_img(filename, target_size=(224,224))
    i = img_to_array(img)
    im = preprocess_input(i)
    img = np.expand_dims(im, axis=0)
    return img


@app.route('/translate', methods=['POST'])
def translate():
    text = request.form['text']
    lang = request.form['lang']
    result = translate_func(text,lang)
    #print(result)
    return jsonify({'result': result})


@app.route('/predict',methods=['GET','POST'])
def predict():
    
      ref={0: 'Apple___Apple_scab',
      1: 'Apple___Black_rot',
      2: 'Apple___Cedar_apple_rust',
      3: 'Apple___healthy',
      #4: 'Blueberry___healthy',
      4: 'Cherry_(including_sour)___Powdery_mildew',
      5: 'Cherry_(including_sour)___healthy',
      6: 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
      7: 'Corn_(maize)___Common_rust_',
      8: 'Corn_(maize)___Northern_Leaf_Blight',
      9: 'Corn_(maize)___healthy',
      10: 'Grape___Black_rot',
      11: 'Grape___Esca_(Black_Measles)',
      12: 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
      13: 'Grape___healthy',
      #15: 'Orange___Haunglongbing_(Citrus_greening)',
      14: 'Peach___Bacterial_spot',
      15: 'Peach___healthy',
      16: 'Pepper,_bell___Bacterial_spot',
      17: 'Pepper,_bell___healthy',
      18: 'Potato___Early_blight',
      19: 'Potato___Late_blight',
      20: 'Potato___healthy',
      #23: 'Raspberry___healthy',
      #24: 'Soybean___healthy',
      #25: 'Squash___Powdery_mildew',
      21: 'Strawberry___Leaf_scorch',
      22: 'Strawberry___healthy',
      23: 'Tomato___Bacterial_spot',
      24: 'Tomato___Early_blight',
      25: 'Tomato___Late_blight',
      26: 'Tomato___Leaf_Mold',
      27: 'Tomato___Septoria_leaf_spot',
      28: 'Tomato___Spider_mites Two-spotted_spider_mite',
      29: 'Tomato___Target_Spot',
      30: 'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
      31: 'Tomato___Tomato_mosaic_virus',
      32: 'Tomato___healthy'}
      
     
      
     
      if request.method == 'POST':
          file = request.files['file']
          print(allowed_file(file.filename))
          
          if file and allowed_file(file.filename):
                filename = file.filename
                file_path = os.path.join('static/testimages', filename)
                file.save(file_path)
                img= read_image(file_path)
                class_prediction=model.predict(img) 
                morelikelylabel=max(class_prediction[0])
                classes_x=np.argmax(class_prediction,axis=1)
                d=ref[int(classes_x)]
                document = collection.find_one({"_id": d})
                remedy=document['r']
               
                
                disease_name=""
                d_english=""
                
                
                if "healthy" not in d:
                    s=remedy['r0']
                    for i in s.split(" "):
                        if i!='is' and i!='are':
                            disease_name=disease_name+" "+i
                        else:
                            break
                    d_english=disease_name
                  
                    
                else:

                    disease=d.split("_")[0]
                    if disease=="Corn":
                        disease="Maize"
                    if disease=="Pepper,":
                        disease="Pepper Bell"
                        
                    disease_name=disease+" Healthy"
                    d_english=disease_name 
                    
                
            
                      
                return render_template('predict.html', d=d_english,prob=round(morelikelylabel*100,2), remedy=remedy,user_image = file_path)
              
       
          else:
            return "Unable to read the file. Please check file extension"
        
      return render_template('predict.html')




if __name__ == '__main__':
    app.run(debug=True,use_reloader=False, port=8000)
import onnxruntime as ort 
import os
# from utils.image_preprocessing import preprocessing
import numpy as np

model_path="models/ensemble_model_final.onnx"

def load_disease_model():
    try:
        if os.path.exists(model_path):
            ort_sess=ort.InferenceSession(model_path)
            print(ort_sess)
            return ort_sess
    except Exception as e:
        print(f"Error loading model:{e}")
        return None
load_disease_model()


def disease_preduction():
    if model is None:
        return
    image=np.array(preprocessing)
    try:
        preduction=model.run(None,{image})[0]
        preducted_index=np.argmax(preduction)
        confidence=np.max(preduction)*100
        return preduction,confidence,preducted_index
    except Exception as e:
        print(f"Error during prdiction :{e}")
        return None

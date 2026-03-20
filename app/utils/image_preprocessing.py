from PIL import Image
import numpy as np

image="0b8dabb7-5f1b-4fdc-b3fa-30b289707b90___JR_FrgE.S 3047.JPG"
def preprocessing(img_path):
    with Image.open(img_path) as img:
        resized_image=img.resize((224,224),Image.Resampling.LANCZOS)
        converting_arry=np.array(resized_image)/255.0
        return np.expand_dims(converting_arry,axis=0)
array=preprocessing(image)
print(array)
   
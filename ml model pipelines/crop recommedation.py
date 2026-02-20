# importing all the dependency
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

MODEL_FILE="models/crop recommedation.pkl" # path for saveing an model

if  not os.path.exists(MODEL_FILE): # if model file doesn't exist
    df=pd.read_csv("datasets/Crop_recommendation.csv") # calling an dataset
    X=df.drop(["label"],axis=1) # seting features
    Y=df["label"] # seting labels
    # spliting traing data as 80% and test data 20%
    x_train ,x_test ,y_train , y_test = train_test_split(X,Y,test_size=0.2,random_state=42) 
    
    #train the model on data
    model=RandomForestClassifier(n_estimators=300, max_depth=None,min_samples_split=2,min_samples_leaf=1,random_state=42,n_jobs=-1)
    model.fit(x_train,y_train)

    joblib.dump(model,MODEL_FILE) # save the trained model in file

    print("model trained and saved")
else:
    model=joblib.load(MODEL_FILE) # loading a model in file exists
    print("model is loaded")
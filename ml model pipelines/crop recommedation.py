
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

MODEL_FILE="models/crop recommedation.pkl"

if  not os.path.exists(MODEL_FILE):
    df=pd.read_csv("datasets/Crop_recommendation.csv")
    X=df.drop(["label"],axis=1)
    Y=df["label"]
    
    from sklearn.model_selection import train_test_split
    x_train ,x_test ,y_train , y_test = train_test_split(X,Y,test_size=0.2,random_state=42)
     
    model=RandomForestClassifier(n_estimators=300, max_depth=None,min_samples_split=2,min_samples_leaf=1,random_state=42,n_jobs=-1)
    model.fit(x_train,y_train)

    joblib.dump(model,MODEL_FILE)

    print("model trained and saved")
else:
    model=joblib.load(MODEL_FILE)
    print("model is loaded")
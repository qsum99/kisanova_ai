from  sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.preprocessing import OneHotEncoder,StandardScaler
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import joblib

df=pd.read_csv("datasets/crop_yield.csv")
print("dataset loaded....")

df_clean=df.drop(["Crop_Year","Area","Production","Fertilizer","Pesticide"],axis=1)

x=df_clean.drop("Yield",axis=1)
y=df_clean["Yield"]

cat_features = ['Crop', 'Season', 'State']
num_features = ['Annual_Rainfall']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features)
    ])

pipline=Pipeline([
    ('preprocessor',preprocessor),
    ('model',RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1))
])

x_train , x_test, y_train, y_test= train_test_split(x,y,test_size=0.2,random_state=42)
param_grid = {
    'model__n_estimators': [100, 200],          
    'model__max_depth': [10, 15, 20, None],     
    'model__min_samples_split': [2, 5, 10]  }

grid_search = GridSearchCV(
    estimator=pipline, 
    param_grid=param_grid, 
    cv=5,                 # 5-Fold Cross Validation
    scoring='r2',         # Optimize for the R2 score
    n_jobs=-1,            # Use all CPU cores
    verbose=1             # Show progress
)

grid_search.fit(x_train,y_train)

best_pipeline = grid_search.best_estimator_

y_pred = best_pipeline.predict(x_test)

accuracy=r2_score(y_test,y_pred)
print(accuracy)

joblib.dump(best_pipeline,'yield_model.pkl')

print("model saved as yield_model.pkl'")
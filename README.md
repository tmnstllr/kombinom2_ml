# kombinom2_ml
This repo provides insights into the code I have written during my Bachelor Dissertation.
The title of the Dissertation is:

`Developing a Machine Learning Model for the Prediction of Travel Movements as Simulation Inputs through Intelligent Clustering of Geographical Areas`

## Abstract
Combined transport concepts for passengers and goods focus on providing mobility in rural areas where public transport can barely meet the demand. Mobility demand is based on real data and predicted in a simulation. This work aims to generate additional data and provide machine learning models to predict mobility behaviour more accurately. For this purpose, geographical clustering criteria are defined and implemented, the database is enriched with other real data, and recursive feature elimination is used to extract the most informative features. The ML models are trained in Python using the Scikit-learn API and LightGBM. The hyperparameters are optimised using Bayesian search, and models with different feature sets are evaluated. The best model is tested for integration into the simulation environment.

## Supervised ML Model 
### Approach
- Train/Val/Test split of 0.65/0.2/0.15
- 5-fold CV for training dataset
- Comparison between different Encoders/Transformers/Scalers for categorical and numerical values
- Comparison of XGBoost and LightGBM, opted for LightGBM for faster training 
- Bayesian Search for hyperparameter tuning
- Recursive Feature Elimination (RFE) for feature selection
- Evaluation metrics: RSME (minimised during hyperparameter tuning) and R-squared
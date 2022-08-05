"""
The model.py module is part of the analytics package.  It is for laying out the framework for the
machine learning models used for predictions on the app.

Classes:
    Model
"""


import pandas as pd
import matplotlib.pyplot as plt

# from sklearn import preprocessing
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score



class Model:
    """
    The Model class is for building a model, training it, and using it to make predictions.
    
    Attributes:
        model: The model that is trained and used for predictions.
        data: The dataframe used to train the model.
        features: A list of columns used by the model to make predictions.
        target: The value the model aims to predict.
        type: The type of problem the model is for.  The accepted values are 'Regression' and 'Classification'.
        name: The name of the model, represented as a string.
        predicted_target: A list of predicted target values from the test dataset.
        observed_target: A list of actual target values from the test dataset.
        residuals: A list of residual values for the predicted target values of the test dataset.
    """
    
    def __init__(self, model, data, features, target, model_type, model_name):
        """The constructor method for this class takes in several arguments, including a model, a dataframe, 
        a list of features and a target, and saves them as attributes."""
        
        self.model = model
        self.data = data
        self.features = features
        self.target = target
        self.type = model_type
        self.name = model_name
        self.predicted_target = None
        self.observed_target = None
        self.residuals = None
    
    def build_model(self, compare_df, test_size=.2):
        """This method splits the dataframe into training and test sets, trains the model on the training data, 
        makes predictions on the test set, and saves metrics in the compare_df dataframe that is passed in."""
        
        # Split dataset into training and test sets, based on the test_size parameter.
        features_train, features_test, target_train, target_test = train_test_split(
            self.data[self.features], self.data[self.target], test_size=test_size)
        
        # Fit the model to the training data and save the metric as a variables.
        self.model = self.model.fit(features_train, target_train)
        training_score = self.model.score(features_train, target_train)
        
        # Make predictions on the test set and save the metrics as variables.
        self.predicted_target = self.model.predict(features_test)
        self.observed_target = target_test
        self.residuals = self.observed_target - self.predicted_target
        
        if self.type == "Regression":
            test_r2 = r2_score(y_true=self.observed_target, y_pred=self.predicted_target)
            mse = mean_squared_error(y_true=self.observed_target, y_pred=self.predicted_target)
            rmse = mse**.5
            metrics = [training_score, test_r2, rmse, 0]
        elif self.type == "Classification":
            accuracy = accuracy_score(y_true=self.observed_target, y_pred=self.predicted_target)
            precision = precision_score(y_true=self.observed_target, y_pred=self.predicted_target)
            recall = recall_score(y_true=self.observed_target, y_pred=self.predicted_target)
            metrics = [training_score, accuracy, precision, recall]
        
        # Add the metrics to the compare_df (given as an argument).
        compare_df.loc[self.name] = metrics
        
        return self.model
    
    def cross_validate(self, cv, compare_df, scoring="neg_mean_squared_error"):
        """This method runs cross validation on the dataset."""
        
        neg_mse = cross_val_score(self.model, self.data[self.features], self.data[self.target], 
                                  cv=cv, scoring=scoring)
        avg_mse = sum(neg_mse) / len(neg_mse) * -1.0
        avg_rmse = avg_mse**.5
        compare_df.loc[self.name, "Cross Validation Score"] = avg_rmse
    
    def get_coefficients(self, test_size=.2):
        """This method gets the coefficients of the model and displays them as a series."""
        
        features_train, features_test, target_train, target_test = train_test_split(
            self.data[self.features], self.data[self.target], test_size=test_size)
        self.model = self.model.fit(features_train, target_train)
        coefficients = pd.Series(self.model.coef_, index=features_train.columns).sort_values(ascending=False)
        return coefficients
    
    def plot_observed_vs_fitted(self):
        """This method creates a line graph for the predicted values and the observed values to visualize how well 
        the model predicts the target variable."""
        
        plt.plot(self.predicted_target, c='g')
        plt.plot(self.observed_target, c='b')
        plt.title("Observed vs Fitted Graph")
    
    def predict(self, data):
        """This method makes predictions on the given dataset."""
        
        predictions = self.model.predict(data)
        return predictions
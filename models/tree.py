"""
A simple SVC model, for reference please see
https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html

I am only using five pickle parameters as feaures, in principle
more features can be used and one can also generate features on the
go using the data passed in to the Model. 
"""

import numpy as np
from sklearn.tree import DecisionTreeClassifier
import cPickle as pickle

from mlpipe import Model


class DecisionTreeModel(Model):

    name = "DecisionTree"

    def __init__(self, random_state=0):
        self.model = DecisionTreeClassifier(random_state=random_state)

    def train(self, data, labels, metadata):
        corrLive = metadata['corrLive']
        rmsLive = metadata['rmsLive']
        kurtLive = metadata['kurtLive']
        skewLive = metadata['skewLive']
        normLive = metadata['normLive']
        features = np.hstack([corrLive, rmsLive, kurtLive, skewLive, normLive])
        self.model.fit(features, labels)

    def validate(self, data, labels, metadata):
        corrLive = metadata['corrLive']
        rmsLive = metadata['rmsLive']
        kurtLive = metadata['kurtLive']
        skewLive = metadata['skewLive']
        normLive = metadata['normLive']
        features = np.hstack([corrLive, rmsLive, kurtLive, skewLive, normLive])
        prediction = self.model.predict(features)
        return prediction
    
    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.model, f, protocol=pickle.HIGHEST_PROTOCOL)

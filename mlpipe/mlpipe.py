# -*- coding: utf-8 -*-

"""Main module."""
from __future__ import print_function
import os
import torch
from torch.utils.data import DataLoader
from sklearn import metrics
from data import Dataset, truncate_collate

from report import Report


class MLPipe(object):
    def __init__(self):
        self._epochs = 1
        self._models = dict()
        self.collate_fn = truncate_collate
        self._param_keys = None
        self._report = Report()

    def set_epochs(self, epochs):
        self._epochs = epochs

    def add_model(self, model):
        self._models[model.name] = model
        
    def set_dataset(self, src):
        if os.path.isfile(src):
            self._train_set = Dataset(src=src, label='train')
            self._test_set = Dataset(src=src, label='test')

            # retrieve parameter keys
            self._param_keys = self._train_set.param_keys

        else:
            raise IOError("Dataset provided is not found!")

    def run(self):
        use_cuda = torch.cuda.is_available()
        device = torch.device("cuda:0" if use_cuda else "cpu")

        # specify parameters used for DataLoader
        loader_params = {
            'batch_size': 32,
            'shuffle': True,
            'num_workers': 1,
            'collate_fn': self.collate_fn
        }

        train_loader = DataLoader(self._train_set, **loader_params)
        test_loader = DataLoader(self._test_set, **loader_params)

        # setup all models
        for name in self._models.keys():
            model = self._models[name]
            model.setup(device)

        # train all models
        for epoch in range(self._epochs):
            for i, (batch, params, labels) in enumerate(train_loader):
                for name in self._models.keys():
                    model = self._models[name]
                    metadata = {
                        'batch_id': i,
                        'device': device
                    }
                    for idx, k in enumerate(self._param_keys):
                        metadata[k] = params[:, idx]

                    output = model.train(batch, labels, metadata)

                    # if there is an output that's not none
                    if len(output) > 0:
                        self._report.add_record(name, epoch, i, output, labels)

                    if i % 100 == 0:
                        self._report.print_batch_report(epoch, i)
                        
                        
        # test all models
        for i, (batch, params, labels) in enumerate(test_loader):
            for name in self._models.keys():
                model = self._models[name]
                metadata = {
                    'batch_id': i,
                    'device': device
                }
                for idx, k in enumerate(self._param_keys):
                    metadata[k] = params[:, idx]

                predictions = model.test(batch, labels, metadata)

        # clean up the memory
        for name in self._models.keys():
            model = self._models[name]
            model.cleanup()

    def report_performance(self, epoch, batch_num, predict, truth):
        
        
class Model(object):

    name = ""

    def __init__(self):
        pass

    def setup(self, device):
        pass

    def train(self, batch, labels, metadata):
        raise RuntimeError("This method needs to be overridden!")

    def test(self, batch, labels, metadata):
        raise RuntimeError("This method needs to be overridden!")

    def cleanup(self):
        pass

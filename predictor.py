#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 17:36:21 2019

@author: shiry10
"""

import pickle
import numpy as np

import keras
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation, Flatten





class predictor:
    def __init__(self):
        self.data = None
        self.model = None
    
    def readdata(self, data_name = 'draft_win.txt'):
        f = open(data_name,'rb') 
        self.data = pickle.load(f) 
        f.close()
        np.random.shuffle(self.data)
        N = len(self.data)
        print(N)
        self.x_train = self.data[:int(0.7*N), :-1] / 130
        self.x_test = self.data[int(0.7*N):, :-1] / 130
        self.y_train = self.data[:int(0.7*N), -1]
        self.y_test = self.data[int(0.7*N):, -1]
        
    def build(self):
        self.model = Sequential()
        self.model.add(Dense(64, activation='relu', input_shape=self.x_train.shape[1:]))
        self.model.add(Dense(128, activation='relu'))
        self.model.add(Dense(32, activation='relu'))
        self.model.add(Dense(16, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
        opt = keras.optimizers.rmsprop(lr=0.001, decay=1e-7)
        self.model.compile(optimizer=opt,
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        
    def train(self, batch_size = 64, epochs = 100):
        self.model.fit(self.x_train, self.y_train, epochs=epochs, batch_size=batch_size)
        
    def save(self):
        self.model.save('predictor.h5')
        
    def evaluate(self):
        eva = self.model.evaluate(self.x_test, self.y_test)
        print(eva)
        
    def do_all(self):
        self.readdata()
        self.build()
        self.train()
        self.evaluate()
        self.save()
        
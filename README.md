## Introduction

This is a DOTA 2 hero picking robot. 

There are 6 basic modules in total, including Miner.py, preprocessing.py, predictor.py, pickers.py, bpsimulator.py, tools.py. 

Miner.py : mine history data from Valve server
preprocessing.py : preprocess data and extract useful information, which basically means win rate of every hero and between 2 heroes and balabala. 
Predictor.py : predict outcome of the game given draft. 
Bpsimulator.py : simulator picking process, build an environment where 2 players can draft against each other. 
Pickers.py : built a human player interface and defined 3 robots to do drafting.

Tools.py : some additional tools. 




Necessary data has been added, including win rate data and trained predictor.h5 and hero_id dictionary.
Updated to 2019.03.20.


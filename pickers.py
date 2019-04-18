#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 17:38:01 2019

@author: shiry10
"""


import pickle
import numpy as np
import random
import json
import tools

from keras.models import load_model




class Random_picker:
    """Randomly pick hero"""
    def __init__(self, side='Radiant', pool=set(list(range(1,24)) + list(range(25, 115)) + [119,120])):
        self.pool = pool
        
    def pick(self, Round, picked, avail=None, Max_sampling=0):
        """
        randomly select hero
        avail: list of available heroes
        picked: list of picked heroes
        max_sampling: no use
        """
        if Round < 0 or Round > 9:
            raise Exception("Not started or have finished! Round out of range", Round)
        if avail == None:
            avail = list(self.pool)
        for hero in picked:
            if hero in avail:
                avail.remove(hero)
        return random.choice(avail)
    
    
    


class Greedy_picker:
    def __init__(self, side='Radiant', pool=set(list(range(1,24)) + list(range(25, 115)) + [119,120])):
        self.pool = pool
        f = open('winrate_1hero.txt','rb') 
        self.winrate_1hero = pickle.load(f) 
        f.close()
        f = open('winrate_single.txt','rb') 
        self.winrate_single = pickle.load(f) 
        f.close()
        self.side = side
        if side == 'Dire':
            self.winrate_1hero = 1 - self.winrate_1hero
            self.winrate_single = 1 - self.winrate_single
        
        
    def pick(self, Round, picked, avail=None, Max_sampling=0):
        """
        return the highest winrate hero against the last picked hero. 
        """
        if not avail:
            avail = list(self.pool)
        for hero in picked:
            if hero in avail:
                avail.remove(hero)
        if not picked:
            cur_winrate = self.winrate_single
        else:
            cur_winrate = self.winrate_1hero[picked[-1]]
        winrate_argsort = cur_winrate.argsort()[::-1]
        top = self.select_top_from_available(avail, winrate_argsort, random_range=10)
        return random.choice(top)
    
    
    def select_top_from_available(self, avail, winrate_argsort, random_range=10):
        top = []
        ind = 0
        while random_range > 0:
            if winrate_argsort[ind] not in avail:
                ind += 1
            else:
                top.append(winrate_argsort[ind])
                random_range -= 1
                ind += 1
        return top
        
    





class Monte_Carlo_picker:
    
    def __init__(self, side='Radiant', data=None, model_name='predictor.h5', pool=set(list(range(1,24)) + list(range(25, 115)) + [119,120])):
        self.data = data
        # initialize hero pool
        self.pool = pool
        # load environment
        self.predictor = load_model(model_name)
        self.side = side
        
    
    def pick(self, Round, picked, avail=None, Max_sampling=1000):
        """
        Round: int, round of current pick 
        picked: list, list of picked heroes
        Max_sampling: max number of Monte Carlo sampling
        return picked hero of this round
        """
        # check if the input is valid
        if Round != len(picked):
            raise Exception("Invalid input: Round and picked hero don't match", Round, picked)
        # remove picked hero from hero pool
        if avail == None:
            avail = list(self.pool)
        for hero in picked:
            if hero in avail:
                avail.remove(hero)
        
        # First pick: randomly pick some high winrate hero available in the hero pool 
        if Round == 0:
            return self.firstpick(avail)
        # Second pick: randomly pick some high winrate hero against the picked
        if Round == 1:
            return self.secondpick(avail, picked)
        # Third pick: randomly pick some high winrate hero against the picked
        if Round == 2:
            return self.thirdpick(avail, picked)
        # For further pick, do Monte Carlo sampling
        return self.Monte_Carlo(avail, Round, picked, Max_sampling)
        
        
    def select_top_from_available(self, avail, winrate_argsort, random_range=10):
        top = []
        ind = 0
        while random_range > 0:
            if winrate_argsort[ind] not in avail:
                ind += 1
            else:
                top.append(winrate_argsort[ind])
                random_range -= 1
                ind += 1
        return top
    
        
    def firstpick(self, avail, random_range=10):
        """
        For first pick, randomly pick heros from 
        top #random_range heros from available heroes. 
        """
        f = open('winrate_single.txt','rb') 
        winrate_single = pickle.load(f) 
        f.close()
        if self.side == 'Dire':
            winrate_single = 1 - winrate_single
        winrate_argsort = winrate_single.argsort()[::-1]
        top = self.select_top_from_available(avail, winrate_argsort, random_range)
        return random.choice(top)
    
    
    def secondpick(self, avail, picked, random_range=10):
        """
        For second pick, randomly pick heroes from 
        top #random_range heroes against the picked hero. 
        """
        f = open('winrate_1hero.txt','rb') 
        winrate_1hero = pickle.load(f) 
        f.close()
        winrate = winrate_1hero[picked[0]]
        if self.side == 'Dire':
            winrate = 1 - winrate
        winrate_argsort = winrate.argsort()[::-1]
        top = self.select_top_from_available(avail, winrate_argsort, random_range)
        return random.choice(top)
    
    
    def thirdpick(self, avail, picked, random_range=10):
        """
        For third pick, randomly pick heroes from 
        top #random_range heroes against the picked hero. 
        """
        f = open('winrate_2hero.txt','rb') 
        winrate_2hero = pickle.load(f) 
        f.close()
        winrate = winrate_2hero[picked[0], picked[1]]
        if self.side == 'Dire':
            winrate = 1 - winrate
        winrate_argsort = winrate.argsort()[::-1]
        top = self.select_top_from_available(avail, winrate_argsort, random_range)
        return random.choice(top)
        
        
    def Monte_Carlo(self, avail, Round, picked, Max_sampling):
        """
        Do Monte Carlo sampling and return heroes with largest reward value. 
        """
        # policy is the probability of selecting a hero in avail
        policy = np.zeros([max(avail)+1])
        selected_times = np.ones([max(avail)+1])
        # initially, for all heroes in avail, probability of picking all heroes is equal. 
        for hero in avail:
            policy[hero] = 0.1
        # Do sampling Max_sampling times
        for i in range(Max_sampling):
            # single_sampling should return slected hero in first following round 
            # and return win probability. 
            selected_hero, win_probability = self.single_sampling_equal_prob(avail, Round, picked) 
            selected_times[selected_hero] += 1
            if self.side == 'Dire':
                win_probability = 1 - win_probability
            policy[selected_hero] += win_probability
        policy = policy / selected_times
#         print(policy)
        return np.argmax(policy)
            
    
    def single_sampling_equal_prob(self, avail, Round, picked):
        """
        Do sampling for a single time. 
        """
        if Round < 10:
            selected = random.choice(avail)
            new_avail, new_picked = avail.copy(), picked.copy()
            new_avail.remove(selected)
            new_picked.append(selected)
            win_probability = self.single_sampling_equal_prob(new_avail, Round+1, new_picked)[1]
            return selected, win_probability
        if Round == 10:
            lineup = self.assign_team(picked)
            lineup = np.array(lineup).reshape(1, 10)
            win_probability = self.predictor.predict(lineup)
#             print(lineup, win_probability)
            return None, win_probability
            
            
    def assign_team(self, picked, order=[0,2,4,6,8]):
        """
        picked: list of picked heroes
        order: indices of radiant heroes in picked
        return: list 
        """
        lineup_r, lineup_d = [], []
        for i, hero in enumerate(picked):
            if i in order:
                lineup_r.append(hero)
            else:
                lineup_d.append(hero)
        return lineup_r + lineup_d
    
    
    def e_greedy(self, policy, e=0.1):
        pro = random.random()
        if pro > e:
            return np.argmax(policy)
        else:
            nonzero = [ind for ind in range(len(policy)) if policy[ind] != 0]
            return random.choice(nonzero)
        


class Human:
    """Human player"""
    def __init__(self, side='Radiant', show_name=False, pool=set(list(range(1,24)) + list(range(25, 115)) + [119,120])):
        self.pool = pool
        self.side = side
        self.show_name = show_name
        
    def pick(self, Round, picked, avail=None, Max_sampling=0):
        """
        randomly select hero
        avail: list of available heroes
        picked: list of picked heroes
        max_sampling: no use
        """
        if avail == None:
            avail = list(self.pool)
        for hero in picked:
            if hero in avail:
                avail.remove(hero)
        
        R_team = picked[::2]
        D_team = picked[1::2]
        if self.side == 'Radiant':
            your_team = R_team
            enermy_team = D_team
        else:
            your_team = D_team
            enermy_team = R_team         
        
        print()
        print('Radiant team: ', R_team, 'Dire team: ', D_team)
        if self.show_name:
            t = tools.tools()
            t.show_name_single(R_team, 'Radiant')
            t.show_name_single(D_team, 'Dire')
        print(self.side + "'s turn: ")
        
        while True:
            try:
                hero = int(input('Pick your hero ID:  '))
            except ValueError:
                print("Invalid input")
            if hero in avail:
                return hero
            if hero not in avail:
                print('Unavailable hero, pick again')

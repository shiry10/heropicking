
import numpy as np
import json
from keras.models import load_model
import tools



class bpsimulator:
    
    def __init__(self, R_picker, D_picker, order=[0,2,4,6,8], model_name='predictor.h5', show_result=False, show_name=False):
        self.pool = set(list(range(1,24)) + list(range(25, 115)) + [119,120])
        self.order = order
        self.R = R_picker
        self.D = D_picker
        self.predictor = load_model('predictor.h5')
        self.Round = 10
        self.show_result = show_result
        self.show_name = show_name
        
    
    def simulate(self, max_sampling=200):
        avail = list(self.pool)
        picked = []
        for r in range(self.Round):
            if r in self.order:
                selected = self.R.pick(r, picked, avail, max_sampling)
            else:
                selected = self.D.pick(r, picked, avail, max_sampling)
            if selected not in avail:
                print(selected)
            avail.remove(selected)
            picked.append(selected)
        lineup = self.assign_team(picked)
#         print(lineup)
        lineup = np.array(lineup).reshape(1, 10)
        win_probability = self.predictor.predict(lineup)
#         print(win_probability)
        if self.show_result:
            print()
            print('Radiant: ', lineup[0, :5], '    ', 'Dire: ', lineup[0, 5:])
            if self.show_name:
                t = tools.tools()
                t.show_name_lineup(lineup[0])
            if win_probability > 0.5:
                print('Radiant win')
            else:
                print('Dire win')
        
        return int(win_probability > 0.5)
        
        
    def assign_team(self, picked):
        """
        picked: list of picked heroes
        order: indices of radiant heroes in picked
        return: list 
        """
        lineup_r, lineup_d = [], []
        for i, hero in enumerate(picked):
            if i in self.order:
                lineup_r.append(hero)
            else:
                lineup_d.append(hero)
        return lineup_r + lineup_d
        
        
    def test(self):
        a = self.R.pick(4, [1,2,3,4])
        print(a)
    
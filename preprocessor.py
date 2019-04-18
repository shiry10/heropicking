
import pickle
import numpy as np





class preprocessor:
    def winrate_single(self):
        """记录每个英雄自己的胜率"""
        f = open('draft_win.txt','rb') 
        draft_win = pickle.load(f) 
        f.close()
        win_count = np.zeros([130]) / 100
        match_count = np.ones([130]) / 100
        for match in draft_win:
            for hero in match[:5]:
                match_count[hero] += 1
                win_count[hero] += match[-1]
            for hero in match[5:10]:
                match_count[hero] += 1
                win_count[hero] += 1 - match[-1]
        win_rate = win_count / match_count
        f = open('winrate_single.txt','wb')
        pickle.dump(win_rate,f)
        f.close()
    
    def winrate_1hero(self):
        """
        针对一个英雄的胜率分布
        矩阵第i行，第j列的元素代表英雄i对英雄j的胜率，即ij分别在两边，i获胜的比率
        """
        f = open('draft_win.txt','rb') 
        draft_win = pickle.load(f) 
        f.close()
        
        win_count = np.zeros([130, 130]) / 100
        match_count = np.ones([130, 130]) / 100
        for match in draft_win:
            for hero_r in match[:5]:
                for hero_d in match[5:10]:
                    match_count[hero_r, hero_d] += 1
                    win_count[hero_r, hero_d] += match[-1]
        win_rate = win_count / match_count

        f = open('winrate_1hero.txt','wb')
        pickle.dump(win_rate,f)
        f.close()
        
        
    def winrate_2hero(self):
        """
        针对两个英雄（天辉夜魇各一个）的胜率分布
        矩阵中位于（i, j, k）的元素代表在天辉有英雄i夜魇有英雄j的情况下，天辉选出英雄k的胜率
        """
        f = open('draft_win.txt','rb') 
        draft_win = pickle.load(f) 
        f.close()
        
        win_count = np.zeros([130, 130, 130]) / 100
        match_count = np.ones([130, 130, 130]) / 100
        for match in draft_win:
            for hero_r1 in match[:5]:
                for hero_d1 in match[5:10]:
                    for hero_r2 in match[0:5]:
                        if hero_r2 != hero_r1:
                            match_count[hero_r1, hero_d1, hero_r2] += 1
                            win_count[hero_r1, hero_d1, hero_r2] += match[-1]
        win_rate = win_count / match_count
        
        f = open('winrate_2hero.txt','wb')
        pickle.dump(win_rate,f)
        f.close()
        
    
    def winrate_single_dict(self):
        """记录每个英雄自己的胜率"""
        f = open('draft_win.txt','rb') 
        draft_win = pickle.load(f) 
        f.close()
        win_count = {}
        match_count = {}
        for match in draft_win:
            for hero in match[:5]:
                match_count[hero] = match_count.get(hero, 0) + 1
                win_count[hero] = win_count.get(hero, 0) + match[-1] == 1
            for hero in match[5:10]:
                match_count[hero] = match_count.get(hero, 0) + 1
                win_count[hero] = win_count.get(hero, 0) + match[-1] == 0
        win_rate = {}
        for hero in match_count:
            win_rate[hero] = win_count[hero] / match_count[hero]
        f = open('winrate_single_dict.txt','wb')
        pickle.dump(win_rate,f)
        f.close()
                    
                
    
    def winrate_1hero_dict(self):
        """
        针对一个英雄的胜率分布
        矩阵第i行，第j列的元素代表英雄i对英雄j的胜率，即ij分别在两边，i获胜的比率
        """
        f = open('draft_win.txt','rb') 
        draft_win = pickle.load(f) 
        f.close()
        win_count = {}
        match_count = {}
        for match_index in range(len(draft_win)):
            for hero_r in draft_win[match_index, 0:5]:
                for hero_d in draft_win[match_index, 5:10]:
                    match_count[(hero_r, hero_d)] = match_count.get((hero_r, hero_d), 0) + 1
                    win_count[(hero_r, hero_d)] = win_count.get((hero_r, hero_d), 0) + draft_win[match_index, -1]
        win_rate = {}
        for heroes in win_count:
            win_rate[heroes] = win_count[heroes] / match_count[heroes]

        f = open('winrate_1hero_dict.txt','wb')
        pickle.dump(win_rate,f)
        f.close()
        
        
    def winrate_2hero_dict(self):
        """
        针对两个英雄（天辉夜魇各一个）的胜率分布
        矩阵中位于（i, j, k）的元素代表在天辉有英雄i夜魇有英雄j的情况下，天辉选出英雄k的胜率
        """
        f = open('draft_win.txt','rb')
        draft_win = pickle.load(f)
        f.close()
        win_count = {}
        match_count = {}
        for match_index in range(len(draft_win)):
            for hero_r1 in draft_win[match_index, 0:5]:
                for hero_d1 in draft_win[match_index, 5:10]:
                    for hero_r2 in draft_win[match_index, 0:5]:
                        if hero_r2 != hero_r1:
                            match_count[(hero_r1, hero_d1, hero_r2)] = match_count.get((hero_r1, hero_d1, hero_r2), 0) + 1
                            win_count[(hero_r1, hero_d1, hero_r2)] = win_count.get((hero_r1, hero_d1, hero_r2), 0) + draft_win[match_index, -1]
        win_rate = {}
        for heroes in win_count:
            win_rate[heroes] = win_count[heroes] / match_count[heroes]
        
        f = open('winrate_2hero_dict.txt','wb')
        pickle.dump(win_rate,f)
        f.close()
        

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import rcParams
import json

class tools:
    '''helper tools'''
    def __init__(self):
        with open('hero_data_dict.txt') as json_file:  
            self.hero_data_dict = json.load(json_file)
    
    def show_name_single(self, picked, side):
        name = []
        for hero in picked:
            name.append(self.hero_data_dict[str(hero)]['localized_name'])
        print(side+': ', name)
    
    def show_name_lineup(self, lineup):
        lineup_name = []
        for i, hero in enumerate(lineup):
            lineup_name.append(self.hero_data_dict[str(hero)]['localized_name'])
        print('Radiant: ', lineup_name[:5])
        print('Dire: ', lineup_name[5:])
        
    def show_image_single(self, picked, side):
#         %matplotlib inline
        n = len(picked)
        # figure size in inches optional
        rcParams['figure.figsize'] = n, 1
        # read images
        img_url = [self.hero_data_dict[str(picked[i])]['url_small_portrait'] for i in range(n)]
        img = [mpimg.imread(img_url[i]) for i in range(n)]
        # display images
        fig, ax = plt.subplots(1,n)
        for i in range(n):
            ax[i].imshow(img[i])
            ax[i].set_axis_off()
            ax[i].set_xticks([]),ax[i].set_yticks([])
        ax[0].set_title(side)
        
    
    def show_image_lineup(self, lineup):
        # %matplotlib inline
        n = len(lineup)
        rcParams['figure.figsize'] = n, 1
        # read images
        img_url = [self.hero_data_dict[str(lineup[i])]['url_small_portrait'] for i in range(n)]
        img = [mpimg.imread(img_url[i]) for i in range(n)]
        # display images
        fig, ax = plt.subplots(1,n)
        for i in range(5):
            ax[i].imshow(img[i])
            ax[i].set_axis_off()
            ax[i].set_xticks([]),ax[i].set_yticks([])
        ax[0].set_title('Radiant')
        for i in range(5, 10):
            ax[i].imshow(img[i])
            ax[i].set_axis_off()
            ax[i].set_xticks([]),ax[i].set_yticks([])
        ax[5].set_title('Dire')
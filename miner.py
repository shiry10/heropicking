
import json
import logging
import pandas as pd
import ssl
import time
from urllib.request import urlopen
import urllib.error
from pandas.io.json import json_normalize
import pickle
import numpy as np
import os
import itertools
import heapq
import random


class Miner:
    def mine_data(self,
                  file_name=None,
                  first_match_id=0,
                  last_match_id=9999999999,
                  stop_at=None,
                  timeout=15,
                  save_every=1000):
        
        global OPENDOTA_URL
        OPENDOTA_URL = "https://api.opendota.com/api/publicMatches?less_than_match_id="
        global REQUEST_TIMEOUT
        REQUEST_TIMEOUT = 0.3
        global COLUMNS
        COLUMNS = ['match_id', 'radiant_win', 'radiant_team', 'dire_team', 'avg_mmr', 'num_mmr',
                   'game_mode', 'lobby_type']
        HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        global logger
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        results_dataframe = pd.DataFrame()
        current_chunk = 1
        current_match_id = last_match_id
        games_remaining = stop_at

        while current_match_id > first_match_id:
            try:
                current_link = OPENDOTA_URL + str(current_match_id)
                logger.info("Mining chunk starting at match ID %d", current_match_id)
                req = urllib.request.Request(url=current_link, headers=HEADERS)
                response = urllib.request.urlopen(req, timeout=timeout)
    #             response = urlopen(current_link, timeout=timeout)
            except (urllib.error.URLError, ssl.SSLError) as error:
                logger.error("Failed to make a request starting at match ID %d", current_match_id)
                logger.info("Waiting %d seconds before retrying", timeout)
                time.sleep(timeout)
                current_match_id -= 1  
                continue

            try:
                response_json = json.load(response)
                last_match_id = response_json[-1]['match_id']
            except (ValueError, KeyError) as error:
                logger.error("Corrupt JSON starting at match ID %d, skipping it", current_match_id)
                current_match_id -= 1
                continue

            current_match_id = last_match_id

            if games_remaining:
                games_remaining -= len(response_json)

            current_dataframe = json_normalize(response_json)

            if len(current_dataframe) == 0:
                logger.info("Found an empty dataframe, skipping 10 games")
                current_match_id -= 10
                continue

            results_dataframe = results_dataframe.append(current_dataframe, ignore_index=True)

            if len(results_dataframe) >= current_chunk * save_every:
                current_chunk += 1

                if file_name:
                    pd.DataFrame(results_dataframe, columns=COLUMNS).to_csv(file_name, index=False)
                    logger.info("Saving to csv. Total of games mined: %d", len(results_dataframe))

                    if stop_at:
                        if len(results_dataframe) >= stop_at:
                            return results_dataframe

            if stop_at:
                if len(results_dataframe) >= stop_at:
                    break

            time.sleep(REQUEST_TIMEOUT)

        return results_dataframe
    
    def to_csv(self, 
               last_match_id, 
               first_match_id = 0, 
               file_count = 20, 
               start_file = 0, 
               matches_per_file = 20000):
        """
        starting from last_match_id, search matches whose id smaller than last_match_id, save into csv every matches_per_file matches
        first_match is the upper bound match id
        """
        for i in range(start_file, start_file + file_count):
            print(i)
            last_match_id_current = last_match_id - i * matches_per_file
            file_name = 'rawdata_' + str(i) + '.csv'
            currunt_dataframe = self.mine_data(file_name = file_name,
                                                  first_match_id = first_match_id,
                                                  last_match_id = last_match_id_current,
                                                  stop_at = matches_per_file)
            currunt_dataframe.to_csv('rawdata_' + str(i) + '.csv')
            
            
    def extract_target_mmr(self, high = 99999, low = 4000):
        """extract matches whose mmr in [low, high] from csv, save into target_mmr"""
        # initialize empty target_mmr. cover exsisting data to avoid duplicating data. 
        target_mmr = pd.DataFrame(columns=['match_id',
                                         'radiant_win',
                                         'radiant_team', 
                                         'dire_team', 
                                         'avg_mmr', 
                                         'num_mmr', 
                                         'game_mode', 
                                         'lobby_type'])
        target_mmr.to_csv('target_mmr.csv')
        # save matches into target_mmr dataframe
        i = 0
        path = 'rawdata_' + str(i) + '.csv'
        while os.path.isfile(path):
            dataset_df = pd.read_csv(path)
            dataset_df = dataset_df[(dataset_df.avg_mmr > low) & (dataset_df.avg_mmr < high)][['match_id', 'radiant_win', 'radiant_team', 'dire_team', 'avg_mmr', 'num_mmr', 'game_mode', 'lobby_type']]
            target_mmr = target_mmr.append(dataset_df)
            i += 1
            path = 'rawdata_' + str(i) + '.csv'
        # save target_mmr dataframe into target_mmr csv
        target_mmr.to_csv('target_mmr.csv')
        
        
    def formulate(self):
        """
        convert target_mmr into numpy array
        """
        # initialize new empty file
        draft_win = np.empty([])
        f = open('draft_win.txt','wb')  
        pickle.dump(draft_win,f)
        f.close()
        # read lineup and outcome from target_mmr
        target_mmr = pd.read_csv('target_mmr.csv')
        draft_win_df = target_mmr.loc[:, ['radiant_team', 'dire_team', 'radiant_win']]
        # convert into numpy array
        # Radiant
        draft_win_df_r = pd.DataFrame(draft_win_df.radiant_team.str.split(',',4).tolist(), columns = ['r1','r2','r3','r4','r5'])
        # Dire
        draft_win_df_d = pd.DataFrame(draft_win_df.dire_team.str.split(',',4).tolist(), columns = ['d1','d2','d3','d4','d5'])
        # outcome
        draft_win_df_w = draft_win_df.radiant_win
        # join
        draft_win_df = draft_win_df_r.join(draft_win_df_d).join(draft_win_df_w)
        # save into numpy array
        draft_win_np = draft_win_df.values
        # str to int
        draft_win_np = draft_win_np.astype(np.int)
        # sort lineup (hero id)
        draft_win_np[:, :5].sort()
        draft_win_np[:, 5:10].sort()
        print(draft_win_np.shape)
        # augment data by swap the lineup
        augmented = draft_win_np.copy()
        augmented[:, :5] = draft_win_np[:, 5:10]
        augmented[:, 5:10] = draft_win_np[:, :5]
        augmented[:, -1] = 1 - draft_win_np[:, -1]
        draft_win_np_augmented = np.concatenate((draft_win_np, augmented), axis=0)
        # pickle
        f = open('draft_win.txt','wb')  
        pickle.dump(draft_win_np_augmented,f)
        f.close()
        # read pickle numpy array
        f = open('draft_win.txt','rb') 
        draft_win = pickle.load(f) 
        f.close()
        print('draft_win shape:\n', draft_win.shape)
        print('draft_win:\n', draft_win[0:2])
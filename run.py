#!/usr/bin/env python
# coding: utf-8

import argparse
import numpy as np
import csv

import warnings
warnings.filterwarnings("ignore")

import sys
sys.path.append('./src')
sys.path.append('./models')

import pandas as pd
from tqdm import tqdm
tqdm.pandas()

from model import AcikhackModel

parser = argparse.ArgumentParser()
parser.add_argument('-data-path',  type=str, required=True, help='Girdi dosyasinin adresi')
args = parser.parse_args()

print("Submission scripti baslatildi!")
print("Girdi verisi okunuyor...")
df = pd.read_csv(args.data_path)

subm_null_df = df.copy()

comparison_cols = [
# 'baslik', 
# 'kurum',
# 'url',
# 'kanunum_url'

## THESE SHOULD BE ENABLED vvv
    
    'rega_no',
    'sira_no',
    'mukerrer_no',
    'donem',
    'kategori',
    'rega_tarihi',
    'mevzuat_no',
    'belge_sayi',
    'mevzuat_tarihi', 
    'madde_sayisi',
]

subm_null_df[comparison_cols] = np.nan
subm_null_df[["mukerrer_no", "madde_sayisi"]] = 0

print("Model olusturuluyor...")
ah_model = AcikhackModel(checkpoint_path="./models")

print("Model calistiriliyor...")
submission_df = ah_model.run_pipeline(subm_null_df)

submission_df["rega_no"] = submission_df["rega_no"].astype("string").fillna("")

submission_df.to_csv("ornek-eval-dataset.csv", index=False)

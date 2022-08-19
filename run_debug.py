#!/usr/bin/env python
# coding: utf-8

import argparse

import warnings
warnings.filterwarnings("ignore")

import sys
sys.path.append('./src')
sys.path.append('./models')

import pandas as pd
import numpy as np

from tqdm import tqdm
tqdm.pandas()

from model import AcikhackModel

parser = argparse.ArgumentParser()
parser.add_argument('-data-path',  type=str, required=True, help='Girdi dosyasinin adresi')
args = parser.parse_args()

print("Debug scripti baslatildi!")
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
df["mukerrer_no"].fillna(0, inplace=True)
df["madde_sayisi"].fillna(0, inplace=True)

print("Model olusturuluyor...")
ah_model = AcikhackModel(checkpoint_path="./models")

print("Model calistiriliyor...")
submission_df = ah_model.run_pipeline(subm_null_df)

submission_df["exact_match"] = 1

print("\n\n")
print("*"*20)
print("Basari tablosu:")
print("*"*20)

for comparison_col in comparison_cols:
#     if comparison_col in ["donem"]:
#         continue
    # Mevzuat specific evaluation rule
    if comparison_col in ["mevzuat_no", "mevzuat_tarihi"]:
        submission_df.loc[submission_df.kategori == "Yönetmelik", comparison_col] = "devre_disi"
        df.loc[df.kategori == "Yönetmelik", comparison_col] = "devre_disi"
    
    # Madde sayisi specific evaluation rule
    if comparison_col == "madde_sayisi":
        col_success = (abs(submission_df[comparison_col].fillna(0) - df[comparison_col].fillna(0))<2).astype(int)
    else:
        col_success = (submission_df[comparison_col].fillna(-1111) == df[comparison_col].fillna(-1111)).astype(int)
    
    print(f"Score for '{comparison_col}': {col_success.mean()}")
    submission_df["exact_match"] *= col_success

print("\nOverall score:", submission_df["exact_match"].mean())






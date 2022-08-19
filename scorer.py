#!/usr/bin/env python
# coding: utf-8

import argparse

import warnings
warnings.filterwarnings("ignore")

import sys
sys.path.append('./src')
sys.path.append('./models')

import pandas as pd

from tqdm import tqdm
tqdm.pandas()

parser = argparse.ArgumentParser()
parser.add_argument('-gt-data-path',  type=str, required=True, help='GT dosyasinin adresi')
parser.add_argument('-pred-data-path',  type=str, required=True, help='Tahmin dosyasinin adresi')

args = parser.parse_args()

print("Degerlendirme scripti baslatildi!")
print("GT verisi okunuyor...")
gt_df = pd.read_csv(args.gt_data_path)
print("Tahmin verisi okunuyor...")
pred_df = pd.read_csv(args.pred_data_path)

print(gt_df.rega_no)
print(pred_df.rega_no)
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

# subm_null_df[comparison_cols] = np.nan
# subm_null_df[["mukerrer_no", "madde_sayisi"]] = 0
gt_df["mukerrer_no"].fillna(0, inplace=True)
gt_df["madde_sayisi"].fillna(0, inplace=True)


pred_df["exact_match"] = 1

print("\n\n")
print("*"*20)
print("Basari tablosu:")
print("*"*20)

for comparison_col in comparison_cols:
#     if comparison_col in ["donem"]:
#         continue
    # Mevzuat specific evaluation rule
    if comparison_col in ["mevzuat_no", "mevzuat_tarihi"]:
        pred_df.loc[pred_df.kategori == "Yönetmelik", comparison_col] = "devre_disi"
        gt_df.loc[gt_df.kategori == "Yönetmelik", comparison_col] = "devre_disi"
    
    # Madde sayisi specific evaluation rule
    if comparison_col == "madde_sayisi":
        col_success = (abs(pred_df[comparison_col].fillna(0) - gt_df[comparison_col].fillna(0))<2).astype(int)
    else:
        col_success = (pred_df[comparison_col].fillna(-1111) == gt_df[comparison_col].fillna(-1111)).astype(int)
    
    print(f"Score for '{comparison_col}': {col_success.mean()}")
    pred_df["exact_match"] *= col_success

print("\nOverall score:", pred_df["exact_match"].mean())






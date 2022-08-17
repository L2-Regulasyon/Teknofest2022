from functools import reduce
from utils import FeatureExtractor
import numpy as np
import pandas as pd
import constants


def competition_evaluator(gt_df,
                          pred_df):
    pass


def filter_dataframe(input_df: pd.DataFrame,
                     selected_categories: list = [],
                     custom_filter_array: list = []):
    filter_list = []

    if isinstance(selected_categories, list):
        for selected_category in selected_categories:
            filter_list.append(input_df.kategori == selected_category)

    if isinstance(custom_filter_array, list):
        for custom_filter in custom_filter_array:
            filter_list.append(custom_filter)

    total_filter = reduce((lambda x, y: x & y), filter_list)

    return input_df[total_filter].copy()


def show_false_predictions(input_df: pd.DataFrame,
                           feature_extractor: FeatureExtractor,
                           cols: list = [],
                           include_na: bool = False,
                           first_n: int = -1):
    tmp_df = input_df.copy()
    tmp_df = tmp_df[tmp_df.kategori.isin(feature_extractor.cols)].copy()

    label = feature_extractor.feature_name
    label_pred = label + "_pred"
    tmp_df.loc[tmp_df[label_pred].isna(), label_pred] = constants.NAN_LABEL

    if not include_na:
        tmp_df = tmp_df[~tmp_df[label].isna()]
    else:
        tmp_df.loc[tmp_df[label].isna(), label] = constants.NAN_LABEL

    return tmp_df[tmp_df[label] != tmp_df[label_pred]][[label, label_pred] + cols][:first_n]


def calculate_accuracy(input_df: pd.DataFrame,
                       feature_extractor: FeatureExtractor,
                       include_na: bool = False
                       ):

    tmp_df = input_df.copy()
    tmp_df = tmp_df[tmp_df.kategori.isin(feature_extractor.cols)].copy()

    label = feature_extractor.feature_name
    label_pred = label + "_pred"
    tmp_df.loc[tmp_df[label_pred].isna(), label_pred] = constants.NAN_LABEL

    if not include_na:
        tmp_df = tmp_df[~tmp_df[label].isna()]
    else:
        tmp_df.loc[tmp_df[label].isna(), label] = constants.NAN_LABEL

    tp_count = len(tmp_df[tmp_df[label] == tmp_df[label_pred]])

    accuracy = np.round((tp_count / len(tmp_df)), 4)
    result_string = "Veri Sayisi: " + str(len(tmp_df)) + "\nDogru Tahmin Sayisi: " +\
                    str(tp_count) + "\nYanlis Tahmin Sayisi: " + str(len(tmp_df) - tp_count) +\
                    "\nBasari Orani: " + str(accuracy)
    print(result_string)

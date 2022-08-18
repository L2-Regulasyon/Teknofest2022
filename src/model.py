from utils import (
RegaNoExtractor,
SiraNoExtractor,
MukerrerNoExtractor,
DonemExtractor,
RegaTarihiExtractor,
MevzuatNoExtractor,
BelgeSayisiExtractor,
MevzuatTarihiExtractor,
MaddeSayisiExtractor,
)

from catboost import Pool, CatBoostClassifier
import pickle
import os
import numpy as np

class AcikhackModel:
    def __init__(self, checkpoint_path: str = ""):
        self.checkpoint_path = checkpoint_path
        self.classifier = None
        self.feature_extractors = [
            BelgeSayisiExtractor(submission_mode=True),
            SiraNoExtractor(submission_mode=True),
            RegaNoExtractor(submission_mode=True),
            MukerrerNoExtractor(submission_mode=True),
            MaddeSayisiExtractor(submission_mode=True),
            RegaTarihiExtractor(submission_mode=True),
            MevzuatNoExtractor(submission_mode=True),
            MevzuatTarihiExtractor(submission_mode=True),
            DonemExtractor(submission_mode=True)
        ]

    def post_process(self, input_df):
        input_df.loc[~input_df.mevzuat_no.isna(), "belge_sayi"] = np.nan
        return input_df

    def run_pipeline(self, input_df):
        result_df = input_df.copy()
        result_df = self.classify(result_df)
        result_df = self.extract(result_df)
        result_df = self.post_process(result_df)
        return result_df

    def classify(self, input_df):
        print("Kategori cikariliyor...")
        tfidf = pickle.load(open(os.path.join(self.checkpoint_path, 'tfidf.pickle'), 'rb'))
        model = CatBoostClassifier()
        model = model.load_model(os.path.join(self.checkpoint_path, "model.cbm"))

        cat_preds = model.predict(tfidf.transform(input_df.loc[:, "data_text"]).toarray()).ravel()
        input_df["kategori"] = cat_preds
        return input_df

    def extract(self, input_df):
        result_df = input_df.copy()
        for feature_extractor in self.feature_extractors:
            feature_extractor.extract(result_df)
        return result_df

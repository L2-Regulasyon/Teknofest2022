import unidecode
import numpy as np
import re

class FeatureExtractor:
    def __init__(self):
        self.feature_name = None
        self.cols = []

    def _extractor_func(self, row_data):
        raise NotImplementedError()

    def extract(self, input_df):
        print(f"'{self.feature_name}' cikariliyor... -> '{self.feature_name}_pred'")
        feature_indexer = input_df.kategori.isin(self.cols)
        input_df[self.feature_name + '_pred'] = None
        input_df.loc[feature_indexer,
                     self.feature_name + '_pred'] = input_df[feature_indexer].progress_apply(
            lambda x: self._extractor_func(x),
            axis=1)


class BelgeSayisiExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.feature_name = "belge_sayi"
        self.cols = ["Genelge"]

    def _extractor_func(self, row_data):
        std_txt = unidecode.unidecode(row_data.data_text).lower()
        belge_sayi = np.nan
        try:
            belge_sayi = std_txt.replace(":", " ") \
                .split('sayi ')[1] \
                .split("\n")[0] \
                .replace("i", "İ") \
                .upper()
        except:
            pass
        return belge_sayi


class MaddeSayisiExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.feature_name = "madde_sayisi"
        self.cols = ["Kanun", "Kanun Hükmünde Kararname", "Cumhurbaşkanlığı Kararnamesi",
                     "Tüzük", "Yönetmelik"]

    def _extractor_func(self, row_data):
        std_txt = unidecode.unidecode(row_data.data_text).lower()
        madde_sayi = np.nan
        try:
            madde_sayi = int(std_txt.replace("-", ":") \
                             .split('\nmadde ')[-1] \
                             .split(":")[0])
            gecici_madde_sayi = int(std_txt.replace("-", ":") \
                                    .split('\ngecici madde ')[-1] \
                                    .split(":")[0])
            madde_sayi += gecici_madde_sayi

        except:
            pass
        return madde_sayi


class MevzuatNoExtractor(FeatureExtractor):

    def __init__(self):
        super().__init__()
        self.feature_name = "mevzuat_no"
        self.cols = ["Kanun", "Kanun Hükmünde Kararname",
                     "Genelge", "Cumhurbaşkanlığı Kararnamesi",
                     "Tüzük", "Yönetmelik"]

    def _extractor_func(self, row_data):
        std_txt = unidecode.unidecode(row_data.data_text).lower()
        mevzuat_no = np.nan

        try:
            #######################################################
            if row_data.kategori == 'Kanun':
                mevzuat_no = std_txt.split('\nkanun no. ')[-1] \
                    .split(" ")[0]
            #######################################################
            elif row_data.kategori == 'Kanun Hükmünde Kararname':
                mevzuat_no = std_txt.split('\nkarar sayisi : khk/')[-1] \
                    .split("\n")[0]
            #######################################################
            elif row_data.kategori == 'Genelge':
                if 'gib.gov.tr' in row_data.url:
                    std_txt = unidecode.unidecode(row_data.baslik).lower()

                    try:
                        # date format
                        mevzuat_no = re.search('([0-9]+[\s]*[\/-][\s]*[0-9]+$)+', std_txt).group(1)
                    except:
                        # digit format
                        if "seri no: " in std_txt:
                            mevzuat_no = std_txt.split('seri no: ')[-1]
                        else:
                            pass  # there is no mevzuat-no
                elif 'kms.kaysis.gov.tr' in row_data.url:
                    std_txt = std_txt.replace("genelge ", "genelge").replace("\n\n", "\n")
                    mevzuat_no = std_txt.split('\ngenelge\n')[1] \
                        .split("\n")[0].replace(" ", "").replace("-", "/")
                    mevzuat_no = "/".join(substr.rjust(2, '0') for substr in mevzuat_no.split("/"))
            #######################################################
            elif row_data.kategori == 'Cumhurbaşkanlığı Kararnamesi':
                std_txt = unidecode.unidecode(row_data.baslik).lower()
                mevzuat_no = std_txt.split('kararname numarasi: ')[-1] \
                    .split(")")[0]
            #######################################################
            elif row_data.kategori == 'Tüzük':
                mevzuat_no = std_txt.split('bkk no: ')[-1] \
                    .split("\n")[0]
            #######################################################
            elif row_data.kategori == 'Yönetmelik':
                std_txt = unidecode.unidecode(row_data.url).lower()
                if 'mevzuatno=' in std_txt:
                    mevzuat_no = std_txt.split('mevzuatno=')[-1] \
                        .split("&")[0]
                elif 'mevzuatkod=' in std_txt:
                    mevzuat_no = std_txt.split('mevzuatkod=')[-1] \
                        .split(".")[-1] \
                        .split("&")[0]
                if len(mevzuat_no) > 4:
                    mevzuat_no = mevzuat_no[:4] + "/" + mevzuat_no[4:]
        except:
            pass

        return mevzuat_no

class RegaTarihiExtractor(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.feature_name = "rega_tarihi"
        self.cols = ["Kanun", "Kanun Hükmünde Kararname","Resmi Gazete"
                      "Cumhurbaşkanlığı Kararnamesi",
                     "Tüzük", "Yönetmelik","Tebliğ"]
    
    def _extractor_func(self, row_data):
        std_txt = unidecode.unidecode(row_data.data_text).lower()
        rega_tarihi = np.nan
        try:
            if row_data.kategori == 'Kanun':
                rega_tarihi = std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[0]
            elif row_data.kategori == 'Kanun Hükmünde Kararname':
                rega_tarihi = std_txt.split("resmi gazete tarihi: ", 1)[1].split('resmi gazete sayisi:', 1)[0]
        except:
            pass
        return rega_tarihi

class MevzuatTarihiExtractor(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.feature_name = "mevzuat_tarihi"
        self.cols = ["Kanun", "Kanun Hükmünde Kararname",
                     "Genelge", "Cumhurbaşkanlığı Kararnamesi",
                     "Tüzük", "Özelge"]
    
    def _extractor_func(self, row_data):
        std_txt = unidecode.unidecode(row_data.data_text).lower()
        mevzuat_tarihi = np.nan
        try:
            if row_data.kategori == 'Kanun':
                mevzuat_tarihi = std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[1].split('kabul tarihi : ')[1].split('\n')[0]
            elif row_data.kategori == 'Kanun Hükmünde Kararname':
                mevzuat_tarihi = std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[1].split('kararnamenin tarihi : ')[1].split('\n')[0]
            elif row_data.kategori == 'Genelge':
                mevzuat_tarihi = std_txt.split("tarih ", 1)[1].split('\n')[0] 
        except:
            pass
        return mevzuat_tarihi


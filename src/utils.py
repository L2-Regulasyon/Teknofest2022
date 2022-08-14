import unidecode
import numpy as np
import re
import constants

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
        self.cols = constants.COLS_BELGE_SAYISI

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
        self.cols = constants.COLS_MADDE_SAYISI

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
        self.cols = constants.COLS_MEVZUAT_NO

    def _extractor_func(self, row_data):
        std_txt = unidecode.unidecode(row_data.data_text).lower()
        mevzuat_no = np.nan

        try:
            kaysis_ekbelge_exception = False
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
                ########
                elif 'kms.kaysis.gov.tr' in row_data.url:
                    date_formatted_regexp = '(([0-9]{4})[\/-][\s]*[0-9]*[-]*[0-9]+)+'

                    # trying to find from title
                    try:  # date format
                        std_txt = unidecode.unidecode(row_data.baslik).lower()

                        if "degisik" in std_txt:
                            std_txt = std_txt.split("degisik")[-1]

                        if "iliskin" in std_txt:
                            iliskin_splitted = std_txt.split("iliskin")[-1]
                            iliskin_splitted_founds = re.findall(date_formatted_regexp, iliskin_splitted)
                            if len(iliskin_splitted_founds) > 0:
                                std_txt = iliskin_splitted

                        found_date_typeds = re.findall(date_formatted_regexp, std_txt)
                        mevzuat_no = found_date_typeds[0][0]

                        # adaptation for year/month-serie format
                        mevzuat_no = mevzuat_no.replace("/", "-")
                        kaysis_ekbelge_exception = mevzuat_no.count("-") > 1
                        mevzuat_no = mevzuat_no.replace("-", "/", 1) if kaysis_ekbelge_exception else mevzuat_no.replace("-", "/")

                    # it's not in title
                    except:
                        # trying to find from text
                        try:
                            std_txt = unidecode.unidecode(row_data.data_text).lower()
                            std_txt = std_txt.replace("genelge ", "genelge").replace("\n\n", "\n")
                            mevzuat_no = std_txt.split('\ngenelge\n')[-1].split("\n")[0]
                        # there isn't any mevzuat no (we hope not)
                        except:
                            pass
                ########
                elif 'mevzuat.gov.tr' in row_data.url:
                    # if the url consists the mevzuat_kod directly
                    if "MevzuatKod" in row_data.url:
                        mevzuat_no = row_data.url.split("MevzuatKod=")[-1].split("&")[0]
                    # if doesn't consist
                    else:
                        url_regexp = "(([0-9]{8})[\/-][\s]*[0-9]*[-]*[0-9]+)+"

                        # trying to find from url
                        try:
                            std_txt = unidecode.unidecode(row_data.url).lower()
                            url_founds = re.findall(url_regexp, std_txt)[-1][0]
                            year = url_founds[:4]
                            serie = url_founds.split("-")[-1]
                            mevzuat_no = year + "/" + serie
                        # there isn't any mevzuat no (we hope not)
                        except:
                            pass
                ########
                elif 'bddk.org.tr' in row_data.url:
                    # trying to find from text
                    try:
                        std_txt = unidecode.unidecode(row_data.data_text).lower()
                        std_txt = std_txt.replace("genelge ", "genelge").replace("\n\n", "\n").replace("\n\n", "\n")
                        mevzuat_no = std_txt.split('genelge\n')[-1].split("\n")[0]
                    # there isn't any mevzuat no (we hope not)
                    except:
                        pass
                ########
                elif 'sgk.gov.tr' in row_data.url:
                    date_formatted_regexp = '(([0-9]{4})[\/-][\s]*[0-9]*[-]*[0-9]+)+'
                    # trying to find from title
                    try:  # date format
                        std_txt = unidecode.unidecode(row_data.baslik).lower()
                        mevzuat_no = re.findall(date_formatted_regexp, std_txt)[0][0]
                    # there isn't any mevzuat no (we hope not)
                    except:
                        pass
                ########
                elif 'tspakb.org.tr' in row_data.url:
                    # trying to find from text
                    try:
                        std_txt = unidecode.unidecode(row_data.data_text).lower().replace("\ngenelge no: ", '\ngenelge no:')
                        mevzuat_no = std_txt.split('\ngenelge no:')[-1].split("\n")[0]
                    # there isn't any mevzuat no (we hope not)
                    except:
                        pass
                ########
                elif 'borsaistanbul.com' in row_data.url:
                    # trying to find from title
                    try:
                        std_txt = unidecode.unidecode(row_data.baslik).lower()
                        mevzuat_no = re.sub("[^0-9]", "", std_txt) # leaving only numericals
                    # there isn't any mevzuat no (we hope not)
                    except:
                        pass
                ########
                elif 'tkgm.gov.tr' in row_data.url:
                    std_txt = unidecode.unidecode(row_data.data_text).lower()
                    # trying to find from text
                    try:
                        std_txt = std_txt.replace("no ", "no").replace(":", "")
                        std_txt = std_txt.split("genelge no")[-1].split("\n")[0]
                        four_digit_regex = "(([:\s]|^)[0-9]{4}([\s]|$))+"
                        year_mo_regex = "[0-9]{4}[/-][0-9]+"
                        four_digit_founds = re.findall(four_digit_regex, std_txt)
                        year_mo_founds = re.findall(year_mo_regex, std_txt)

                        if len(four_digit_founds) > 0:
                            mevzuat_no = four_digit_founds[0][0]
                        else:
                            mevzuat_no = year_mo_founds[0]
                    except:
                        # trying to find from title
                        try:
                            std_txt = unidecode.unidecode(row_data.baslik).lower()
                            mevzuat_no = std_txt.split("sayili")[0].split(",")[-1]
                        # there isn't any mevzuat no (we hope not)
                        except:
                            pass
                ########
                elif 'resmigazete.gov.tr' in row_data.url:
                    std_txt = unidecode.unidecode(row_data.data_text).lower()
                    # trying to find from text
                    try:
                        std_txt = std_txt.replace("no", "no").replace(" ", "").replace("\n\n", "\n").replace("\n\n", "\n")
                        mevzuat_no = std_txt.split("genelge\n")[-1].split("\n")[0]
                    except:
                        pass
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

            if not kaysis_ekbelge_exception:
                mevzuat_no = mevzuat_no.replace("-", "/").replace(" ", "").replace(":", "")

        # there is no mevzuat_no
        except:
            pass

        return mevzuat_no

class RegaTarihiExtractor(FeatureExtractor):
    def __init__(self):
        super().__init__()
        self.feature_name = "rega_tarihi"
        self.cols = constants.COLS_REGA_TARIHI
    
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
        self.cols = constants.COLS_MEVZUAT_TARIHI
    
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


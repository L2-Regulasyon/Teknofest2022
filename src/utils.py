import unidecode
import numpy as np
import re
import constants
import pandas as pd
from re import sub
import dateparser


class FeatureExtractor:
    def __init__(self, submission_mode=False):
        self.feature_name = None
        self.cols = []
        self.submission_mode = submission_mode
        print("Yarisma submission modu:", "ACIK" if self.submission_mode else "KAPALI")

    def _extractor_func(self, row_data):
        raise NotImplementedError()

    def extract(self, input_df):
        output_col_name = self.feature_name + '_pred' if not self.submission_mode else self.feature_name
        print(f"'{self.feature_name}' cikariliyor... -> '{output_col_name}'")
        feature_indexer = input_df.kategori.isin(self.cols)

        if not self.submission_mode:
            input_df[output_col_name] = np.nan

        input_df.loc[feature_indexer,
                     output_col_name] = input_df[feature_indexer].progress_apply(
            lambda x: self._extractor_func(x),
            axis=1)


class BelgeSayisiExtractor(FeatureExtractor):

    def __init__(self, submission_mode=False):
        super().__init__(submission_mode)
        self.feature_name = "belge_sayi"
        self.cols = constants.COLS_BELGE_SAYISI

    def _extractor_func(self, row_data):
        std_txt = unidecode.unidecode(row_data.data_text).lower()
        belge_sayi = row_data[self.feature_name]
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

    def __init__(self, submission_mode=False):
        super().__init__(submission_mode)
        self.feature_name = "madde_sayisi"
        self.cols = constants.COLS_MADDE_SAYISI

    def _extractor_func(self, row_data):
        std_txt = unidecode.unidecode(row_data.data_text).lower()

        #     std_txt = sub('"[^"]*[$"]', '', std_txt)

        madde_sayi = row_data[self.feature_name]
        madde_regexp = '[\n]madde[\s]*[0-9]*[\s]*[/]*[\s]*[\w]*\s[-]\s'
        mukerrer_madde_regexp = '[\n]mukerrer\smadde\s[0-9]+[\s]*[/]*[\s]*[\w]*\s[-]\s'
        gecici_madde_regexp = '[\n]gecici\smadde\s(([0-9]+|[\w]+)[\(]*[0-9]*[\)]*[\s])*[-]\s'
        ek_gecici_madde_regexp = '[\n]gecici\sek\smadde\s[[0-9]+[\s]]*[-]\s'
        ek_madde_regexp = '[\n]ek\smadde[\s]*([0-9])*[/]*[\s]*[\w]*\s-\s'

        try:
            madde_list = []
            for regfound in re.findall(madde_regexp, std_txt):
                try:
                    madde_list.append(int(re.sub("[^0-9]", "", regfound)))
                except:
                    madde_list.append(1)

            # if "resmigazete" not in row_data.url:
            #     madde_sayi = len(madde_list)
            # else:
            #     madde_sayi = max(madde_list) + (len(madde_list) - len(set(madde_list)))

            madde_sayi = len(madde_list)

            mukerrer_madde_list = [regfound for regfound in re.findall(mukerrer_madde_regexp, std_txt)]
            mukerrer_madde_sayi = len(mukerrer_madde_list)
            madde_sayi += mukerrer_madde_sayi

            ek_gecici_madde_list = [regfound for regfound in re.findall(ek_gecici_madde_regexp, std_txt)]
            ek_gecici_madde_sayi = len(ek_gecici_madde_list)
            madde_sayi += ek_gecici_madde_sayi

            gecici_madde_list = [regfound for regfound in re.findall(gecici_madde_regexp, std_txt)]
            gecici_madde_sayi = len(gecici_madde_list)
            madde_sayi += gecici_madde_sayi

            ek_madde_list = [regfound for regfound in re.findall(ek_madde_regexp, std_txt)]
            ek_madde_sayi = len(ek_madde_list)
            madde_sayi += ek_madde_sayi

            madde_sayi = int(madde_sayi)
        except:
            pass

        return madde_sayi


class MevzuatNoExtractor(FeatureExtractor):

    def __init__(self, submission_mode=False):
        super().__init__(submission_mode)
        self.feature_name = "mevzuat_no"
        self.cols = constants.COLS_MEVZUAT_NO

    def _extractor_func(self, row_data):
        std_txt = unidecode.unidecode(row_data.data_text).lower()
        mevzuat_no = row_data[self.feature_name]

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
                try:
                    # gib.gov.tr format
                    edited_std_txt = std_txt.replace("seri", "").replace("sira", "").replace("no", "").replace(
                        "genelgesi", "genelge")
                    mevzuat_no = re.findall('ic\sgenelge[\s]*[\:]*[\s]*([0-9]+[\s]*[\/\\]*[\s]*[0-9]*)[\s]*[\n]+',
                                            edited_std_txt)[0].replace("\n", "")
                ################
                except:
                    try:
                        # kms.kaysis.gov.tr format
                        edited_std_txt = std_txt.replace("seri", "")
                        mevzuat_no = re.findall('genelge[\s]*[\w\d]*[\n]+([0-9]+[\s]*[/\\\-]*[\s]*[0-9]*)[\s]*[\n]+',
                                                edited_std_txt)[0] \
                            .replace("\n", "").replace("-", "/").replace(" ", "")
                    ################
                    except:
                        try:
                            # mevzuat.gov.tr format
                            edited_std_txt = std_txt.replace("seri", "")
                            mevzuat_no = \
                                re.findall('genelge[\s]*([0-9]+[\s]*[/\\\-]*[\s]*[0-9]*)[\s]*[\n]+',
                                           edited_std_txt)[0].replace("\n", "").replace("-", "/").replace(" ", "")
                        ################
                        except:
                            try:
                                # sgk.gov.tr format
                                edited_std_txt = std_txt.replace(" ", "")
                                mevzuat_no = \
                                    re.findall('genelge[\s]*[\w\d]*[\n]+([0-9]+[\s]*[/\\\-]*[\s]*[0-9]*)[\s]*[\n]+',
                                               edited_std_txt)[0].replace("\n", "").replace("-", "/").replace(" ", "")
                            ################
                            except:
                                try:
                                    # tspakb.org.tr format
                                    edited_std_txt = str(std_txt)
                                    mevzuat_no = \
                                        re.findall(
                                            'genelge[\s]*no[\s]*[\:]*[\s]*([0-9]+[\s]*[/\\\-]*[\s]*[0-9]*)[\s]*[\n]+',
                                            edited_std_txt)[0].replace("\n", "").replace("-", "/").replace(" ",
                                                                                                           "")
                                ################
                                except:
                                    try:
                                        # tkgm.gov.tr format
                                        edited_std_txt = std_txt.replace("sayisi", "").replace(".", "").replace("no",
                                                                                                                "")

                                        mevzuat_no_by_genelge_no_row = \
                                            re.findall(
                                                'genelge[\s]*[\:\-]*[\s]*[0-9]+[\s]*[/\\\-]*[\s]*[0-9]*[\s]+([0-9]+)[\s]*[\n]+',
                                                edited_std_txt)

                                        mevzuat_no_by_genelge_no_row_inverse = \
                                            re.findall(
                                                'genelge[\s]*[\:\-]*[\s]*([0-9]+)[\s]*[0-9]+[\s]*[/\\\-]*[\s]*[0-9]*[\s]*[\n]+',
                                                edited_std_txt)

                                        if len(mevzuat_no_by_genelge_no_row) > 0:
                                            mevzuat_no = mevzuat_no_by_genelge_no_row[0].replace("\n", "").replace("-",
                                                                                                                   "/").replace(
                                                " ", "")
                                        elif len(mevzuat_no_by_genelge_no_row_inverse) > 0:
                                            mevzuat_no = mevzuat_no_by_genelge_no_row_inverse[0].replace("\n",
                                                                                                         "").replace(
                                                "-", "/").replace(" ", "")
                                        else:
                                            mevzuat_no = \
                                                re.findall(
                                                    ',[\s]*([0-9]+[\s]*[/\\\-]*[\s]*[0-9]*)[\s]*sayili',
                                                    edited_std_txt)[0].replace("\n", "").replace("-", "/").replace(" ",
                                                                                                                   "")
                                    ################
                                    except:
                                        pass  # Hope we don't fall in to this state

            #######################################################
            elif row_data.kategori == 'Cumhurbaşkanlığı Kararnamesi':
                kararname_no_regexp = '[\(]*kararname\snumarasi[\s]*[\:]*[\s]*([0-9]+)[\)]*'
                kararname_sayisi_regexp = '[\(]*kararname\ssayisi[\s]*[\:]*[\s]*([0-9]+)[\)]*'
                try:
                    mevzuat_no = re.findall(kararname_no_regexp, std_txt)[0]
                except:
                    mevzuat_no = re.findall(kararname_sayisi_regexp, std_txt)[0]

            #######################################################
            elif row_data.kategori == 'Tüzük':
                mevzuat_no = std_txt.split('bkk no: ')[-1] \
                    .split("\n")[0]
            #######################################################
            elif row_data.kategori == 'Yönetmelik':
                # Won't be included
                pass

            # if not kaysis_ekbelge_exception:
            #     mevzuat_no = mevzuat_no.replace("-", "/").replace(" ", "").replace(":", "")

        # there is no mevzuat_no
        except:
            pass

        return mevzuat_no


class RegaTarihiExtractor(FeatureExtractor):
    def __init__(self,submission_mode=False):
        super().__init__(submission_mode)
        self.feature_name = "rega_tarihi"
        self.cols = constants.COLS_REGA_TARIHI
    
    def tarih_duzelt(self,text):
        text = text.replace('\n', '')
        text = text.replace('/n', '')
        text = text.replace(' ', '')
        text = text.replace('î', 'i')
        text = text.replace('nısan', 'nisan')
        text = text.replace('mayis', 'mayıs')
        text = text.replace('ekım', 'ekim')
        text = text.replace('kasim', 'kasım')
        text = text.replace('aralik', 'aralık')
        return text

    def _extractor_func(self, row_data):
        NoneType = type(None)
        aylar=['ocak','subat','mart','nisan','mayis','haziran','temmuz','agustos','eylul','ekim','kasim','aralik']
        rega_tarihi = np.nan
        
        try:
            std_txt = unidecode.unidecode(row_data.data_text).lower()
            if row_data.kategori == 'Kanun':
                rega_tarihi = std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[0]
            #######################################################
            elif row_data.kategori == 'Kanun Hükmünde Kararname':
                rega_tarihi =  std_txt.split("resmi gazete tarihi: ", 1)[1].split('resmi gazete sayisi:', 1)[0]
            #######################################################
            elif row_data.kategori == 'Resmi Gazete':
                std_txt = unidecode.unidecode(row_data.data_text).lower()
                a=std_txt.split('sayi')[0].replace(' ','').split('\n')
                while '' in a:
                    a.remove('')
                date2=pd.to_datetime(dateparser.parse(self.tarih_duzelt(a[-2]),languages=['tr']),dayfirst=True)
                if type(date2) == NoneType:
                    date2=pd.to_datetime(dateparser.parse(self.tarih_duzelt(a[-1]),languages=['tr']),dayfirst=True)
                    if type(date2) == NoneType:
                        date2=pd.to_datetime(dateparser.parse(self.tarih_duzelt(a[-3]),languages=['tr']),dayfirst=True)
                        if type(date2) == NoneType:
                            date2=pd.to_datetime(dateparser.parse(self.tarih_duzelt(a[-4]),languages=['tr']),dayfirst=True)
                            if type(date2) == NoneType:
                                date2=pd.to_datetime(dateparser.parse(self.tarih_duzelt(a[-5]),languages=['tr']),dayfirst=True)
                                if type(date2) == NoneType:
                                    a=std_txt.replace(' ','').split('sayi')[0].replace(' ','').split('\n')
                                    while '' in a:
                                        a.remove('')
                                    date2=pd.to_datetime(dateparser.parse(self.tarih_duzelt(a[-2]),languages=['tr']),dayfirst=True)
                                    if type(date2) == NoneType:
                                        date2=pd.to_datetime(dateparser.parse(self.tarih_duzelt(a[-1]),languages=['tr']),dayfirst=True)
                                        if type(date2) == NoneType:
                                            date2=pd.to_datetime(dateparser.parse(self.tarih_duzelt(a[-3]),languages=['tr']),dayfirst=True)
                                            if type(date2) == NoneType:
                                                a=''.join(std_txt.lower().split('sayı')[0].split(' ')[-4:])
                                                ''.join(std_txt.lower().split('sayı')[0].split(' ')[-4:])
                                                date2=pd.to_datetime(dateparser.parse(self.tarih_duzelt(a),languages=['tr']),dayfirst=True)
                                                if type(date2) == NoneType:
                                                    std_txt=std_txt.replace(' ','').replace('\n','')
                                                    for ay in aylar:
                                                        if ay in std_txt:
                                                            gun=std_txt.split(ay)[0][-2:]
                                                            yil=std_txt.split(ay)[1][:4]
                                                            date2=''.join([gun,ay,yil])
                                                            date2=pd.to_datetime(dateparser.parse(self.tarih_duzelt(date2),languages=['tr']),dayfirst=True)
                                                            if type(date2) != NoneType:
                                                                break
                                                        else:
                                                            date=np.nan

                rega_tarihi=date2
            #######################################################
            elif row_data.kategori == "Cumhurbaşkanlığı Kararnamesi":
                rega_tarihi = std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[0].replace(" ","")
            #######################################################
            elif row_data.kategori == 'Tüzük':  
                rega_tarihi=std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[0].replace(" ","")
            #######################################################
            elif row_data.kategori == 'Yönetmelik':
                rega_tarihi = std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[0]
            #######################################################
            elif row_data.kategori == 'Tebliğ':
                rega_tarihi = std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[0]
        except:
            rega_tarihi=np.nan
        try:
            rega_tarihi=str(pd.to_datetime(rega_tarihi,dayfirst=True).date())
        except:
            rega_tarihi=np.nan
        return rega_tarihi
    

class MevzuatTarihiExtractor(FeatureExtractor):
    def __init__(self, submission_mode=False):
        super().__init__(submission_mode)
        self.feature_name = "mevzuat_tarihi"
        self.cols = constants.COLS_MEVZUAT_TARIHI
    
    def tarih_duzelt(self,text):
        text = text.replace('\n', '')
        text = text.replace('/n', '')
        text = text.replace(' ', '')
        text = text.replace('î', 'i')
        text = text.replace('nısan', 'nisan')
        text = text.replace('mayis', 'mayıs')
        text = text.replace('ekım', 'ekim')
        text = text.replace('kasim', 'kasım')
        text = text.replace('aralik', 'aralık')
        return text

    def _extractor_func(self, row_data):
        #std_txt = unidecode.unidecode(row_data.data_text).lower()
        std_txt = row_data.data_text.lower()
        mevzuat_tarihi = np.nan
        try:
            if row_data.kategori == 'Kanun':
                std_txt = unidecode.unidecode(row_data.data_text).lower()
                mevzuat_tarihi = pd.to_datetime(std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[1]\
                                                    .split('kabul tarihi : ')[1].split('\n')[0],dayfirst=True)

            #######################################################
            elif row_data.kategori == 'Kanun Hükmünde Kararname':
                std_txt = unidecode.unidecode(row_data.data_text).lower()
                mevzuat_tarihi = pd.to_datetime(std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[1]\
                                                    .split('kararnamenin tarihi : ')[1].split('\n')[0],dayfirst=True)
            #######################################################
            elif row_data.kategori == 'Genelge':
                std_txt = unidecode.unidecode(row_data.data_text).lower()
                try:
                    mevzuat_tarihi = std_txt.split("sayi",1)[0]
                    regex = re.compile('[0-9]{1,2}[/.][0-9]{2}[/.][0-9]{4}')
                    mevzuat_tarihi=regex.findall(mevzuat_tarihi)[0]
                    mevzuat_tarihi=pd.to_datetime(mevzuat_tarihi,dayfirst=True)
                except:
                    
                    try:
                        mevzuat_tarihi = std_txt.split("tarih",1)[0]
                        regex = re.compile('[0-9]{1,2}[/.][0-9]{2}[/.][0-9]{4}')
                        mevzuat_tarihi=regex.findall(mevzuat_tarihi)[0]
                        mevzuat_tarihi=pd.to_datetime(mevzuat_tarihi,dayfirst=True)
                    except:
                        try:
                            mevzuat_tarihi = std_txt
                            regex = re.compile('[0-9]{1,2}[/.][0-9]{2}[/.][0-9]{4}')
                            mevzuat_tarihi=regex.findall(mevzuat_tarihi)[0]
                            mevzuat_tarihi=pd.to_datetime(mevzuat_tarihi,dayfirst=True)
                        except:
                            try:
                                mevzuat_tarihi=pd.to_datetime(re.findall(r'\d{2}/\d{2}/\d{4}', std_txt.replace('-',' '))[0],dayfirst=True)
                            except:
                                try:
                                    mevzuat_tarihi=pd.to_datetime(re.findall(r'\d{1}/\d{1}/\d{4}', std_txt)[0],dayfirst=True)
                                except:
                                    mevzuat_tarihi=np.nan
            #######################################################
            elif row_data.kategori == 'Cumhurbaşkanlığı Kararnamesi':
                mevzuat_tarihi = self.tarih_duzelt(row_data.data_text.split('\n')[-1])
                mevzuat_tarihi = pd.to_datetime(dateparser.parse(mevzuat_tarihi,languages=['tr']),dayfirst=True)
            #######################################################
            elif row_data.kategori == 'Tüzük':
                mevzuat_tarihi = pd.to_datetime(std_txt.split("bkk no: ",1)[0].split("karar tarihi: ",1)[1].replace(",","")\
                                                .replace(" ",""),dayfirst=True)
            #######################################################
            elif row_data.kategori == 'Özelge':
                std_txt = unidecode.unidecode(row_data.data_text).lower()
                try:
                    mevzuat_tarihi = std_txt.split("konu",1)[0]
                    regex = re.compile('[0-9]{1,2}[/.][0-9]{2}[/.][0-9]{4}')
                    mevzuat_tarihi=regex.findall(mevzuat_tarihi)[0]
                    mevzuat_tarihi=pd.to_datetime(mevzuat_tarihi,dayfirst=True)
                except:
                    try:
                        mevzuat_tarihi = std_txt.split("sayi",1)[0]
                        regex = re.compile('[0-9]{1,2}[/.][0-9]{2}[/.][0-9]{4}')
                        mevzuat_tarihi=regex.findall(mevzuat_tarihi)[0]
                        mevzuat_tarihi=pd.to_datetime(mevzuat_tarihi,dayfirst=True)
                    except:
                        try:
                            mevzuat_tarihi = std_txt.split('*')[0]
                            regex = re.compile('[0-9]{1,2}[/.][0-9]{2}[/.][0-9]{4}')
                            mevzuat_tarihi=regex.findall(mevzuat_tarihi)[0]
                            mevzuat_tarihi=pd.to_datetime(mevzuat_tarihi,dayfirst=True)
                        except:
                            mevzuat_tarihi=np.nan
        except:
            pass
        try:
            mevzuat_tarihi=str(mevzuat_tarihi.date())
        except:
            mevzuat_tarihi=np.nan
            
        return mevzuat_tarihi
    
class DonemExtractor(FeatureExtractor):
    def __init__(self,submission_mode=False):
        super().__init__(submission_mode)
        self.feature_name = "donem"
        self.cols = constants.COLS_DONEM
        
    def _extractor_func(self, row_data):
        #std_txt = row_data.data_text#.lower().replace(' ','')
        std_txt = unidecode.unidecode(row_data.data_text).lower()
        donem = np.nan  
        try:
            if row_data.kategori == 'Komisyon Raporu':
                try:
                    regex = re.compile('donem:[0-9]{1,2}')
                    donem=regex.findall(std_txt.replace(' ',''))
                    donem=re.findall(r'\d+', donem[0])
                    donem=''.join([donem[0],'. Dönem'])
                except:
                    try:
                        regex = re.compile('yasamayili[0-9]{1,2}')
                        donem=regex.findall(std_txt.replace(' ',''))
                        donem=re.findall(r'\d+', donem[0])
                        donem=''.join([donem[0],'. Dönem'])
                    except:
                        try:
                            regex = re.compile('yasamadonemi[0-9]{1,2}')
                            donem=regex.findall(std_txt.replace(' ','').replace('\n',''))
                            donem=re.findall(r'\d+', donem[0])
                            donem=''.join([donem[0],'. Dönem'])
                        except:
                            donem="1. Dönem"
        except:
            pass
        return donem
class FeatureExtractor_Vectorized(FeatureExtractor):
    def __init__(self, submission_mode=False):
        super().__init__(submission_mode=submission_mode)

    def extract(self, input_df):
        output_col_name = self.feature_name + '_pred' if not self.submission_mode else self.feature_name
        print(f"'{self.feature_name}' cikariliyor... -> '{output_col_name}'")
        feature_indexer = input_df.kategori.isin(self.cols)

        if not self.submission_mode:
            input_df[output_col_name] = np.nan


        input_df.loc[feature_indexer,
                     output_col_name] = self._post_process_func(self._pre_process_func(input_df.loc[feature_indexer, "data_text"]).apply(
                                                                self._extractor_func
                                                                ))
                     
    def _extractor_func(self, row_data):
        raise NotImplementedError()

    def _pre_process_func(self, col_data):
        return col_data

    def _post_process_func(self, col_data):
        return col_data
    
    def iter_pattern(self, string, pattern, group=2):
        collection = re.finditer(pattern, string)

        if not collection:
            raise Exception(f"The pattern {pattern} isn't found in {string}")

        for match in collection:
            try:
                match_ = match.group(group)
            except Exception as e:
                raise e
            else:
                break

        return match_

    def extract(self, input_df):
        output_col_name = self.feature_name + '_pred' if not self.submission_mode else self.feature_name
        print(f"'{self.feature_name}' cikariliyor... -> '{output_col_name}'")
        feature_indexer = input_df.kategori.isin(self.cols)

        if not self.submission_mode:
            input_df[output_col_name] = np.nan
        input_df.loc[feature_indexer,
                     output_col_name] = self._post_process_func(self._pre_process_func(input_df.loc[feature_indexer, "data_text"]).apply(
                                                                self._extractor_func
                                                                ))
class SiraNoExtractor(FeatureExtractor_Vectorized):
    def __init__(self, submission_mode=False):
        super().__init__(submission_mode)
        self.feature_name = "sira_no"
        self.cols = constants.COLS_SIRA_NO

    def _pre_process_func(self, col_data):
        return col_data.str.lower()\
                    .str.replace("'", " ")\
                    .str.replace("©", "ek")\
                    .str.replace("\(c\)", "ek")\
                    .str.replace("ek", " ek")\
                    .str.replace(":", "")\
                    .replace({"birinci": "1",
                                "ikinci": "2",
                                "ücüncü": "3",
                                "üçüncü": "3",
                                "dördüncü": "4",
                                "besinci": "5",
                                "beşinci": "5",
                                "altıncı": "6",
                                "yedinci": "7",
                                "sekizinci": "8",
                                "dokuzuncu": "9",
                                'birinci': '1',
                                'ikinci': '2',
                                'ucuncu': '3',
                                'uçuncu': '3',
                                'dörduncu': '4',
                                'besinci': '5',
                                'beşinci': '5',
                                'altıncı': '6',
                                'yedinci': '7',
                                'sekizinci': '8',
                                'dokuzuncu': '9'
                                }, regex=True)\
                    .str.replace("\s+", " ")\
                    .str.replace("s ira", "sira")\
                    .str.replace("slra", "sira")\
                    .str.replace("ı", "i")\
                    .str.replace("y", "")\
    
    def _post_process_func(self, col_data):
        return col_data

    def _extractor_func(self, row_data):
        pattern = "(\d+) (e \| nci|e \| ci|e ] nei|e 1 nci|e 1 nc|e|a) (ek|ilâve|ilave)"

        try:
          sira_no = str(int(self.iter_pattern(row_data, pattern, 1))) + " ek 1"#int(re.search(pattern, row).group(2))
        except Exception as e:
          pattern = "(\d+) (ek|e+k|e|a) (\d+)"
          try:
            sira_no = str(int(self.iter_pattern(row_data, pattern, 1))) + " ek " + str(int(self.iter_pattern(row_data, pattern, 3)))

          except Exception as e:
            pattern = "(s\.|sira) saisi (\d+)"
            try:
              sira_no = str(int(self.iter_pattern(row_data, pattern, 2)))

            except Exception as e:
              sira_no = 0

            else:
              pass

          else:
            pass

        return sira_no


class MukerrerNoExtractor(FeatureExtractor_Vectorized):
    def __init__(self, submission_mode=False):
        super().__init__(submission_mode)
        self.feature_name = "mukerrer_no"
        self.cols = constants.COLS_MUKERRER_NO
        self.valid_one_cases = pd.Series()

    def _pre_process_func(self, col_data):
        return col_data.astype(str).str.lower().str.replace("\s+", " ")

    def _post_process_func(self, col_data):
        return col_data

    def _extractor_func(self, row_data):
        pattern = "(\d+)\. mükerrer"

        try:
          mukerrer_no = int(self.iter_pattern(row_data, pattern, 1))#int(re.search(pattern, row).group(2))
        except Exception as e:

          try:
            pattern = "(\d+) mükerrer"
            mukerrer_no = int(self.iter_pattern(row_data, pattern, 1))#int(re.search(pattern, row).group(2))
            if mukerrer_no and mukerrer_no > 10:
                mukerrer_no = 1

          except Exception as e:
              mukerrer_no = 0
              pass

        return mukerrer_no

class RegaNoExtractor(FeatureExtractor_Vectorized):
    def __init__(self, submission_mode=False):
        super().__init__(submission_mode)
        self.feature_name = "rega_no"
        self.cols = constants.COLS_REGA_NO

    def _post_process_func(self, col_data):
        return col_data.fillna("").astype(str).str.split(".").str.get(0).str.replace(".", "").str.slice(0, 5).replace("", np.nan)

    def _pre_process_func(self, col_data):
        return col_data.str.lower()\
                       .str.replace("\n+", "***")\
                       .str.replace("\s+", "")\
                       .str.replace("sayi", "sayı")\
                       .str.replace("sayısı", "sayı")\
                       .str.replace("sayılı", "sayı")\
                       .str.replace("sayıfa", "sayfa")

    def _extractor_func(self, row_data):
        pattern = "(sayı:)(\d+)"

        try:
          rega_no = int(self.iter_pattern(row_data, pattern, 2))#int(re.search(pattern, row).group(2))
        except Exception as e:
            
            try:
              pattern = "(\d+)(sayı)"
              rega_no = int(self.iter_pattern(row_data, pattern, 1))#int(re.search(pattern, row).group(1))
            
            except Exception as e:
                #print(e)
                rega_no = None

        return rega_no
# Kamuda Mevzuat Arama Motoru Geliştirme
### Takım: L2 Regülasyon

<img src='data/img/cropped-logo_Ack2.png' width='450'>

Bu kütüphane, L2 Regülasyon takımının `TeknoFest` yarışması `Kamuda Mevzuat Arama Motoru Geliştirme` adlı alt kolu için hazırladığı konsept uygulamanın kaynak kodlarını içermektedir.

---

## Kullanım

### Gereksinimler
Kullandığınız `conda` paket yöneticisinin en son sürümü kurulu olmalıdır. Lütfen [bu linkteki](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) yönergeleri izleyin.

### Ortam Kurulumu
Projeyi herhangi bir problem yaşamadan çalıştırabilmek için lütfen aşağıdaki komutları kullanarak sanal geliştirme ortamınızı oluşturun:
```bash
conda env create -f environment.yml
conda activate acikhack
```

### Uygulamanın Çalıştırılması
Aşağıdaki kod ile tanımlayacağınız veri ile bütün süreci koşup çıktı alabilirsiniz. Sonuçlar aynı dizine `ornek-eval-dataset.csv` ismi altında kaydedilecektir.
```bash
python run.py -data-path VERI_ADRESI
```

Aşağıdaki kod ile eğitim için verilen veriyi tanımlayarak süreci koşabilir ve başarı skorunu görüntüleyebilirsiniz.
```bash
python run_debug.py -data-path VERI_ADRESI
```

Aşağıdaki kod ile ürettiğiniz tahminleri ve ground-truth verileri besleyerek sadece skorlama rutinini çalıştırabilirsiniz.
```bash
python scorer.py -gt-data-path ORJINAL_VERI_ADRESI -pred-data-path TAHMIN_VERI_ADRESI
```

### Analiz Dosyaları
`/notebook` klasörü altındaki notebook dosyalarını:
```bash
jupyter notebook
```
yazıp bir jupyter server açtıktan sonra inceleyebilirsiniz.

### Paket Sürümlerinin Ayarlanması (Opsiyonel)
Projeyi doğrudan çalıştırmak istiyorsanız bu adımı atlayabilirsiniz. Fakat proje ortamında kullanılan kütüphanelere ekleme veya değişiklik yapmak istiyorsanız aşağıdaki rutini izlemelisiniz.
Eğer bir kütüphane eklemek istiyorsanız, ismini `req.in` dosyasına ekleyin,  ve `req.txt` dosyasını aşağıdaki komut ile yeniden oluşturun.
```
pip-compile req.in
```
ve oluşturduğunuz en güncel gereksinim listesini aşağıdaki komut ile ortamınıza kurun:
```
pip install -r req.txt
```

---

### Veri ile ilgili problemler
Yarışma dahilinde ekibimize sağlanan veride bazı tutarsızlıklar ve çıkmazlar olduğunu keşfettik. Bunlar aşağıdaki şekilde sıralanabilir:

##### Mevzuat No
- Genelge tipi mevzuat numaralarına ait asli etiket değerlerinin (ground truth) bazıları `2017/9` formatında verilmişken bazıları ise `2017/09` formatında verilmiş. Ürettiğimiz çözüm başa sıfır koyma işlemini (zero-padding) yapmıyor olacak. (`2017/09`)
- Genelge tipi mevzuat numaralarına ait asli etiket değerlerinin (ground truth) bazıları `2017/9` formatında verilmişken bazıları ise `2017 /09`, `2017 / 09` gibi boşluk hataları ile verilmiş. Ürettiğimiz çözüm çıktıyı standardize etmek adına boşlukları siliyor (`2017/09`). Bu yüzden bu tip hatalara sahip asli etiket değerine sahip olan satırlar tahmin yanlışmış gibi sahte bir sonuç üretebilir.
- `KAYSIS` kaynaklı bazı verilerde asıl etiket değeri `32945953-010.06.01-E.1046330` kodunun `1046330` kısmı olarak verilmişken bazı verilerde `YIL/NUMARA` olarak verilmiş. Satırlardan iki türlü de veri alabiliyoruz fakat beklenen formatın hangisi olduğu net olmadığı için `YIL/NUMARA` formatında bıraktık.
- Bazı verilerin mevzuat numaralarının tamamı ya da bir kısmı el ile yazıldığı için OCR tarafından eksik veya hatalı okunmuş. Modelin yanlışlarının bazıları OCR'dan gelen ham verinin yanlışlığından kaynaklanıyor. Orjinal siteye gidip veriyi özel bir şekilde işlemek hem zaman hem kaynak açısından problemli olacağından bu kol üzerine yoğunlaşmadık.
- `https://kms.kaysis.gov.tr/Home/Goster/68870` adresine sahip verinin text sütunu hatalı olduğu için herhangi bir şekilde veri çıkarmak mümkün değil.

#### Rega Tarihi
- Kanun kategorisinde `25 TEŞRİNİSANİ 1931`,`7 KÂNUNUSANİ 1930` gibi osmanlıca tarihler bulunmaktadır. Bu tarihleri haritalandırarak kodlamak mümkün olsa da, pdf formatından aktarılan metinlerdeki bozulma eski tarihli dosyaların tahminini güçleştirmektedir.

#### Dönem
- Komisyon raporlarında `data_text` içinde 189 kayıtta `Dönem` e benzer bir bilgi bulunmamaktadır. Bu nedenle dönem bilgisine erişilememektedir. 
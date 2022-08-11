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
Şu an proje sayfasından analiz ve başlangıç kodlarına ulaşılabilir.  `/notebook` klasörü altındaki notebook dosyalarını:
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
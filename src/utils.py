def find_dates(text,date_type,kategori):
    std_txt=unidecode.unidecode(text).lower()
    if kategori=='kanun':
        if date_type=='rega':
            match=std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[0]
        elif date_type=='mevzuat':
            match=std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[1].split('kabul tarihi : ')[1].split('\n')[0]
    elif kategori=='khk':
        if date_type=='rega':
            match=std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[0]
        elif date_type=='mevzuat':
            match=std_txt.split("resmi gazete tarihi: ",1)[1].split('resmi gazete sayisi:',1)[1].split('kararnamenin tarihi : ')[1].split('\n')[0]
    elif kategori=='genelge':
        if date_type=='mevzuat':
            match=std_txt.split("tarih ",1)[1].split('\n')[0]
    return match
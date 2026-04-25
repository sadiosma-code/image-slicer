import streamlit as st
from PIL import Image
import zipfile
import io

st.set_page_config(page_title="Email Image Slicer", layout="wide")
st.title("✂️ Email Image Slicer")

uploaded_file = st.file_uploader("Görseli Buraya Bırak", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    w, h = img.size
    num_slices = 4
    slice_h = h // num_slices
    
    zip_buffer = io.BytesIO()
    html_rows = ""
    
    # DÜZELTME: Tüm yazma işlemleri bu 'with' bloğunun İÇİNDE olmalı
    with zipfile.ZipFile(zip_buffer, "w") as zip_f:
        for i in range(num_slices):
            upper = i * slice_h
            lower = (i + 1) * slice_h if i < num_slices - 1 else h
            
            part = img.crop((0, upper, w, lower))
            part_w, part_h = part.size
            
            img_byte_arr = io.BytesIO()
            part.save(img_byte_arr, format='JPEG', quality=90)
            img_name = f"image_{i+1}.jpg"
            
            # Görseli ekle
            zip_f.writestr(img_name, img_byte_arr.getvalue())
            
            # HTML satırını hazırla
            display_h = int(part_h * (600/part_w))
            html_rows += f'<tr><td align="center"><img src="{img_name}" width="600" height="{display_h}" style="display:block;width:100%;height:auto;border:0;" border="0" /></td></tr>'

        # HTML'i birleştir
        full_html = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>@media screen and (max-width:600px){{.container{{width:100% !important}}}}</style></head><body style="margin:0;padding:0;background-color:#f4f4f4;"><table width="100%" border="0" cellpadding="0" cellspacing="0"><tr><td align="center"><table width="600" border="0" cellpadding="0" cellspacing="0" class="container" style="background-color:#ffffff;">{html_rows}</table></td></tr></table></body></html>'
        
        # HTML dosyasını zip kapanmadan İÇERİYE ekle
        zip_f.writestr("index.html", full_html)

    # İndirme butonu artık güvenle ZIP'i sunabilir
    st.success("✅ İşlem Tamamlandı!")
    st.download_button(
        label="🎁 ZIP Olarak İndir (Görseller + HTML)", 
        data=zip_buffer.getvalue(), 
        file_name="mailing_paketi.zip", 
        mime="application/zip"
    )

import streamlit as st
from PIL import Image, ImageDraw
import zipfile
import io

st.set_page_config(page_title="Pro Email Slicer", layout="wide")
st.title("✂️ İnteraktif Email Image Slicer")

# Sidebar Ayarları
st.sidebar.header("⚙️ Kesim Ayarları")
num_slices = st.sidebar.slider("Kaç parçaya bölünsün?", 2, 10, 4)
img_quality = st.sidebar.slider("Görsel Kalitesi", 10, 100, 90)

uploaded_file = st.file_uploader("Görseli Yükleyin", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Orijinal görseli aç
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    w, h = img.size
    slice_h = h // num_slices

    # ÖNİZLEME OLUŞTURMA (Kesim çizgilerini göster)
    preview_img = img.copy()
    draw = ImageDraw.Draw(preview_img)
    
    # Kesim çizgilerini çiz (Kırmızı ve belirgin)
    for i in range(1, num_slices):
        y = i * slice_h
        draw.line([(0, y), (w, y)], fill="red", width=int(h/100)) # Görsel boyutuna göre dinamik çizgi kalınlığı
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🖼️ Kesim Önizlemesi")
        st.image(preview_img, caption="Kırmızı çizgiler kesim noktalarını gösterir.", use_container_width=True)

    # İŞLEME VE ZIP
    zip_buffer = io.BytesIO()
    html_rows = ""
    
    with zipfile.ZipFile(zip_buffer, "w") as zip_f:
        for i in range(num_slices):
            upper = i * slice_h
            lower = (i + 1) * slice_h if i < num_slices - 1 else h
            
            part = img.crop((0, upper, w, lower))
            img_byte_arr = io.BytesIO()
            part.save(img_byte_arr, format='JPEG', quality=img_quality)
            
            img_name = f"image_{i+1}.jpg"
            img_path = f"images/{img_name}"
            zip_f.writestr(img_path, img_byte_arr.getvalue())
            
            display_h = int(part.size[1] * (600/w))
            html_rows += f'<tr><td align="center"><img src="{img_path}" width="600" height="{display_h}" style="display:block;width:100%;height:auto;border:0;" border="0" /></td></tr>'

        full_html = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>@media screen and (max-width:600px){{.container{{width:100% !important}}}}</style></head><body style="margin:0;padding:0;background-color:#f4f4f4;"><table width="100%" border="0" cellpadding="0" cellspacing="0"><tr><td align="center"><table width="600" border="0" cellpadding="0" cellspacing="0" class="container" style="background-color:#ffffff;">{html_rows}</table></td></tr></table></body></html>'
        zip_f.writestr("index.html", full_html)

    with col2:
        st.subheader("📦 Çıktı Merkezi")
        st.info(f"Görsel yüksekliği: {h}px. Her bir parça yaklaşık {slice_h}px olacak.")
        st.download_button(
            label="🚀 Paketi Hazırla ve İndir", 
            data=zip_buffer.getvalue(), 
            file_name="pro_mailing_paketi.zip", 
            mime="application/zip"
        )

import streamlit as st
from PIL import Image, ImageDraw
import zipfile
import io

st.set_page_config(page_title="Manual Email Slicer", layout="wide")
st.title("✂️ Manuel Kesim Noktalı Image Slicer")

# Sidebar Ayarları
st.sidebar.header("⚙️ Kesim Ayarları")
num_parts = st.sidebar.number_input("Toplam Kaç Parça Olacak?", min_value=2, max_value=10, value=3)
img_quality = st.sidebar.slider("Görsel Kalitesi", 10, 100, 90)

# Kesim noktaları için dinamik sliderlar oluştur
st.sidebar.subheader("📍 Kesim Noktalarını Belirle (%)")
cut_points_pct = []
for i in range(num_parts - 1):
    point = st.sidebar.slider(f"{i+1}. Kesim Noktası (%)", 0, 100, int((i+1) * 100 / num_parts), key=f"point_{i}")
    cut_points_pct.append(point)

# Noktaları küçükten büyüğe sırala (Hata önleyici)
cut_points_pct.sort()

uploaded_file = st.file_uploader("Görseli Yükleyin", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    w, h = img.size
    
    # Yüzdelik değerleri piksele çevir
    cut_pixels = [int(p * h / 100) for p in cut_points_pct]
    # Başlangıç ve bitiş piksellerini ekle (0 ve h)
    all_points = [0] + cut_pixels + [h]

    # ÖNİZLEME (Kırmızı çizgilerle)
    preview_img = img.copy()
    draw = ImageDraw.Draw(preview_img)
    for px in cut_pixels:
        draw.line([(0, px), (w, px)], fill="red", width=int(h/120))
        # Çizginin üzerine yüzde kaç olduğunu yaz
        draw.text((10, px + 5), f"%{int(px/h*100)}", fill="red")

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🖼️ Kesim Önizlemesi")
        st.image(preview_img, caption="Soldaki slider'larla çizgileri aşağı yukarı oynatabilirsin.", use_container_width=True)

    # İŞLEME VE ZIP
    zip_buffer = io.BytesIO()
    html_rows = ""
    
    with zipfile.ZipFile(zip_buffer, "w") as zip_f:
        for i in range(len(all_points) - 1):
            upper = all_points[i]
            lower = all_points[i+1]
            
            part = img.crop((0, upper, w, lower))
            img_byte_arr = io.BytesIO()
            part.save(img_byte_arr, format='JPEG', quality=img_quality)
            
            img_name = f"image_{i+1}.jpg"
            img_path = f"images/{img_name}"
            zip_f.writestr(img_path, img_byte_arr.getvalue())
            
            # HTML Row (Responsive)
            p_w, p_h = part.size
            display_h = int(p_h * (600/p_w))
            html_rows += f'<tr><td align="center"><img src="{img_path}" width="600" height="{display_h}" style="display:block;width:100%;height:auto;border:0;" border="0" /></td></tr>'

        full_html = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>@media screen and (max-width:600px){{.container{{width:100% !important}}}}</style></head><body style="margin:0;padding:0;background-color:#f4f4f4;"><table width="100%" border="0" cellpadding="0" cellspacing="0"><tr><td align="center"><table width="600" border="0" cellpadding="0" cellspacing="0" class="container" style="background-color:#ffffff;">{html_rows}</table></td></tr></table></body></html>'
        zip_f.writestr("index.html", full_html)

    with col2:
        st.subheader("📦 Çıktı Merkezi")
        st.info(f"Orijinal Yükseklik: {h}px")
        for i in range(len(all_points)-1):
            st.write(f"Parça {i+1}: {all_points[i+1] - all_points[i]}px")
            
        st.download_button(
            label="🚀 Özel Kesim Paketini İndir", 
            data=zip_buffer.getvalue(), 
            file_name="ozel_mailing_paketi.zip", 
            mime="application/zip"
        )

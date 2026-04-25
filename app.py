import streamlit as st
from PIL import Image, ImageDraw
import zipfile
import io

# Sayfa Ayarları
st.set_page_config(page_title="Color-Coded Image Slicer", layout="wide")
st.title('🎨 Renk Kodlu Profesyonel Image Slicer')

# Profesyonel Renk Paleti (Belirgin ve Kontrast Renkler)
COLORS = [
    "#FF0000", # Kırmızı
    "#00FF00", # Yeşil
    "#0000FF", # Mavi
    "#FF00FF", # Magenta
    "#FF8C00", # Turuncu
    "#00CED1", # Turkuaz
    "#8A2BE2", # Mor
    "#FFD700", # Altın
]

# Yan Menü Ayarları
st.sidebar.header("⚙️ Kesim Ayarları")
num_parts = st.sidebar.number_input("Toplam Kaç Parça?", min_value=2, max_value=len(COLORS)+1, value=3)
img_quality = st.sidebar.slider("Görsel Kalitesi", 10, 100, 90)

uploaded_file = st.file_uploader("Görseli Yükleyin", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    w, h = img.size
    
    # 2. Renk Kodlu Sliderlar
    st.sidebar.subheader("📍 Çizgi Konumları")
    cut_points_data = []
    
    for i in range(num_parts - 1):
        color = COLORS[i % len(COLORS)]
        default_val = int((i + 1) * 100 / num_parts)
        
        # Slider başlığına renkli bir emoji veya metin ekleyelim
        st.sidebar.markdown(f"<span style='color:{color}; font-weight:bold;'>▆ {i+1}. Çizgi</span>", unsafe_allow_index=True, unsafe_allow_html=True)
        point = st.sidebar.slider(f"Konum %", 0, 100, default_val, key=f"p_{i}", label_visibility="collapsed")
        
        cut_points_data.append({"pixel": int(point * h / 100), "color": color, "pct": point})
    
    # Noktaları piksel değerine göre sırala (HTML yapısının bozulmaması için)
    cut_points_data.sort(key=lambda x: x["pixel"])
    all_points = [0] + [d["pixel"] for d in cut_points_data] + [h]

    # 3. ÖNİZLEME (Renkli Çizgiler)
    preview_img = img.copy()
    draw = ImageDraw.Draw(preview_img)
    line_width = max(12, int(h / 80)) # Daha belirgin çizgiler
    
    for data in cut_points_data:
        px = data["pixel"]
        color = data["color"]
        # Çizgiyi çiz
        draw.line([(0, px), (w, px)], fill=color, width=line_width)
        # Etiket ekle
        draw.rectangle([0, px - line_width*3, 250, px], fill=color)
        draw.text((10, px - line_width*2.5), f"KESIM: %{data['pct']}", fill="white")

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🖼️ İnteraktif Önizleme")
        st.image(preview_img, use_container_width=True)

    # 4. İŞLEME VE ZIP
    if st.button("🚀 Renkli Dilimleri Paketle"):
        zip_buffer = io.BytesIO()
        html_rows = ""
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_f:
            for i in range(len(all_points) - 1):
                upper = all_points[i]
                lower = all_points[i+1]
                
                if lower > upper:
                    part = img.crop((0, upper, w, lower))
                    img_byte_arr = io.BytesIO()
                    part.save(img_byte_arr, format='JPEG', quality=img_quality)
                    
                    img_name = f"image_{i+1}.jpg"
                    img_path = f"images/{img_name}"
                    zip_f.writestr(img_path, img_byte_arr.getvalue())
                    
                    p_w, p_h = part.size
                    display_h = int(p_h * (600/p_w))
                    html_rows += f'<tr><td align="center"><img src="{img_path}" width="600" height="{display_h}" style="display:block;width:100%;height:auto;border:0;" border="0" /></td></tr>'

            full_html = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>@media screen and (max-width:600px){{.container{{width:100% !important}}}}</style></head><body style="margin:0;padding:0;background-color:#f4f4f4;"><table width="100%" border="0" cellpadding="0" cellspacing="0"><tr><td align="center"><table width="600" border="0" cellpadding="0" cellspacing="0" class="container" style="background-color:#ffffff;">{html_rows}</table></td></tr></table></body></html>'
            zip_f.writestr("index.html", full_html)
            
        st.success("✅ Renk kodlu kesim paketi hazır!")
        st.download_button(label="🎁 ZIP İndir", data=zip_buffer.getvalue(), file_name="renkli_mailing_paketi.zip", mime="application/zip")

    with col2:
        st.subheader("📊 Dil

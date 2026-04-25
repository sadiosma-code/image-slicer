import streamlit as st
from PIL import Image
import zipfile
import io
from streamlit_drawable_canvas import st_canvas

# Sayfa Ayarları
st.set_page_config(page_title="Drag-and-Drop Email Slicer", layout="wide")
st.title("✂️ İnteraktif "Sürükle-Bırak" Email Image Slicer")
st.write("Görseli yükle, kırmızı çizgileri mouse ile sürükle ve "Paketi Hazırla" butonuna bas.")

# Ayarlar (Quality)
img_quality = st.sidebar.slider("Görsel Kalitesi", 10, 100, 90)

uploaded_file = st.file_uploader("Görseli Yükleyin", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # 1. Orijinal Görseli Aç
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    w, h = img.size
    
    # 2. Tuval (Canvas) Ayarları
    # Görsel çok uzunsa ekrana sığdırmak için boyutunu ölçekleyelim (Önizleme için)
    display_width = 600 # Ekranda 600px genişlikte göstereceğiz
    scale_factor = display_width / w
    display_height = int(h * scale_factor)

    st.subheader("🖼️ Görsel Üzerinde Çizgileri Sürükle")
    
    # Başlangıç çizgilerini oluşturalım (%25, %50, %75'e 3 çizgi)
    initial_drawing = {
        "version": "4.4.0",
        "objects": [
            {"type": "line", "x1": 0, "y1": int(display_height * 0.25), "x2": display_width, "y2": int(display_height * 0.25), "stroke": "red", "strokeWidth": 5, "selectable": True},
            {"type": "line", "x1": 0, "y1": int(display_height * 0.50), "x2": display_width, "y2": int(display_height * 0.50), "stroke": "red", "strokeWidth": 5, "selectable": True},
            {"type": "line", "x1": 0, "y1": int(display_height * 0.75), "x2": display_width, "y2": int(display_height * 0.75), "stroke": "red", "strokeWidth": 5, "selectable": True},
        ]
    }

    # Tuvali Oluştur
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Objelerin iç dolgusu
        stroke_width=5,
        stroke_color="red",
        background_image=img, # Arka plan olarak yüklenen görsel
        update_streamlit=True,
        width=display_width,
        height=display_height,
        drawing_mode="transform", # Objeleri sürüklemek için "transform" modu
        initial_drawing=initial_drawing,
        display_toolbar=False, # Üstteki toolbar'ı gizle
        key="canvas",
    )

    # 3. Kesim Noktalarını Yakala
    cut_pixels = []
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        for obj in objects:
            if obj["type"] == "line":
                # Çizginin y koordinatını al (Önizleme boyutunda)
                y_on_display = obj["top"]
                # Orijinal görsel boyutuna geri ölçekle
                y_original = int(y_on_display / scale_factor)
                
                # Sınırlama (Hata önleyici)
                if 0 < y_original < h:
                    cut_pixels.append(y_original)

    # Noktaları sırala (0, cut1, cut2, cut3, h)
    cut_pixels = sorted(list(set(cut_pixels))) # Aynı yerden geçen çizgileri teke indir
    all_points = [0] + cut_pixels + [h]

    st.write("📍 Kesim Noktaları (Pixel):", cut_pixels)

    # 4. İşleme ve ZIP
    if st.button("✂️ Paketi Hazırla ve İndir"):
        zip_buffer = io.BytesIO()
        html_rows = ""
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_f:
            # En az 2 nokta olmalı (0 ve h)
            if len(all_points) > 2:
                for i in range(len(all_points) - 1):
                    upper = all_points[i]
                    lower = all_points[i+1]
                    
                    if lower > upper: # Hata önleyici
                        part = img.crop((0, upper, w, lower))
                        
                        img_byte_arr = io.BytesIO()
                        part.save(img_byte_arr, format='JPEG', quality=img_quality)
                        
                        img_name = f"image_{i+1}.jpg"
                        img_path = f"images/{img_name}"
                        zip_f.writestr(img_path, img_byte_arr.getvalue())
                        
                        # HTML Satırı (Responsive)
                        p_w, p_h = part.size
                        html_rows += f'<tr><td align="center"><img src="{img_path}" width="600" height="{int(p_h * (600/p_w))}" style="display:block;width:100%;height:auto;border:0;" border="0" /></td></tr>'

                # HTML dosyasını zip'e ekle
                full_html = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>@media screen and (max-width:600px){{.container{{width:100% !important}}}}</style></head><body style="margin:0;padding:0;background-color:#f4f4f4;"><table width="100%" border="0" cellpadding="0" cellspacing="0"><tr><td align="center"><table width="600" border="0" cellpadding="0" cellspacing="0" class="container" style="background-color:#ffffff;">{html_rows}</table></td></tr></table></body></html>'
                zip_f.writestr("index.html", full_html)
                
                st.success(f"✅ İşlem Tamamlandı! {len(all_points)-1} parça hazırlandı.")
                st.download_button(
                    label="🎁 Mailing Paketini İndir", 
                    data=zip_buffer.getvalue(), 
                    file_name="pro_mailing_paketi.zip", 
                    mime="application/zip"
    
                )

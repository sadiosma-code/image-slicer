import streamlit as st
from PIL import Image
import zipfile
import io
from streamlit_drawable_canvas import st_canvas

# Sayfa Ayarları
st.set_page_config(page_title="Drag-and-Drop Email Slicer", layout="wide")
st.title('✂️ İnteraktif "Sürükle-Bırak" Email Image Slicer')
st.write("Görseli yükle, kırmızı çizgileri mouse ile sürükle ve 'Paketi Hazırla' butonuna bas.")

# Ayarlar (Quality)
img_quality = st.sidebar.slider("Görsel Kalitesi", 10, 100, 90)

uploaded_file = st.file_uploader("Görseli Yükleyin", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    w, h = img.size
    
    # Görseli ekrana sığdır (Önizleme ölçekleme)
    display_width = 600 
    scale_factor = display_width / w
    display_height = int(h * scale_factor)

    st.subheader("🖼️ Görsel Üzerinde Çizgileri Sürükle")
    
    # Başlangıç çizgileri
    initial_drawing = {
        "version": "4.4.0",
        "objects": [
            {"type": "line", "left": 0, "top": int(display_height * 0.25), "width": display_width, "height": 0, "stroke": "red", "strokeWidth": 5, "selectable": True},
            {"type": "line", "left": 0, "top": int(display_height * 0.50), "width": display_width, "height": 0, "stroke": "red", "strokeWidth": 5, "selectable": True},
            {"type": "line", "left": 0, "top": int(display_height * 0.75), "width": display_width, "height": 0, "stroke": "red", "strokeWidth": 5, "selectable": True},
        ]
    }

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=5,
        stroke_color="red",
        background_image=img,
        update_streamlit=True,
        width=display_width,
        height=display_height,
        drawing_mode="transform",
        initial_drawing=initial_drawing,
        display_toolbar=False,
        key="canvas",
    )

    cut_pixels = []
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        for obj in objects:
            if obj["type"] == "line":
                y_on_display = obj["top"]
                y_original = int(y_on_display / scale_factor)
                if 0 < y_original < h:
                    cut_pixels.append(y_original)

    cut_pixels = sorted(list(set(cut_pixels)))
    all_points = [0] + cut_pixels + [h]

    st.write("📍 Kesim Noktaları (Pixel):", cut_pixels)

    if st.button("✂️ Paketi Hazırla"):
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
                    html_rows += f'<tr><td align="center"><img src="{img_path}" width="600" height="{int(p_h * (600/p_w))}" style="display:block;width:100%;height:auto;border:0;" border="0" /></td></tr>'

            full_html = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>@media screen and (max-width:600px){{.container{{width:100% !important}}}}</style></head><body style="margin:0;padding:0;background-color:#f4f4f4;"><table width="100%" border="0" cellpadding="0" cellspacing="0"><tr><td align="center"><table width="600" border="0" cellpadding="0" cellspacing="0" class="container" style="background-color:#ffffff;">{html_rows}</table></td></tr></table></body></html>'
            zip_f.writestr("index.html", full_html)
            
        st.success("✅ Paket Hazırlandı!")
        st.download_button(
            label="🎁 İndir", 
            data=zip_buffer.getvalue(), 
            file_name="pro_mailing_paketi.zip", 
            mime="application/zip"
        )

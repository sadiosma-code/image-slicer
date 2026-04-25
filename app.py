import streamlit as st
from PIL import Image
import zipfile
import io

st.set_page_config(page_title="Email Image Slicer Pro", layout="wide")
st.title("✂️ Email Image Slicer Pro")

# Yan Menü (Sidebar) Ayarları
st.sidebar.header("⚙️ Ayarlar")
num_slices = st.sidebar.slider("Kaç parçaya bölünsün?", min_value=2, max_value=10, value=4)
img_quality = st.sidebar.slider("Görsel Kalitesi (JPEG)", min_value=10, max_value=100, value=90)
st.sidebar.info("İpucu: Dosya boyutu çok büyükse kaliteyi 70-80 arasına çekebilirsiniz.")

uploaded_file = st.file_uploader("Görseli Buraya Bırak", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    w, h = img.size
    # Dinamik dilim yüksekliği
    slice_h = h // num_slices
    
    zip_buffer = io.BytesIO()
    html_rows = ""
    
    with zipfile.ZipFile(zip_buffer, "w") as zip_f:
        for i in range(num_slices):
            upper = i * slice_h
            # Son parçada kalan tüm pikselleri al
            lower = (i + 1) * slice_h if i < num_slices - 1 else h
            
            part = img.crop((0, upper, w, lower))
            part_w, part_h = part.size
            
            img_byte_arr = io.BytesIO()
            # Dinamik kalite ayarı burada kullanılıyor
            part.save(img_byte_arr, format='JPEG', quality=img_quality)
            
            img_name = f"image_{i+1}.jpg"
            img_path = f"images/{img_

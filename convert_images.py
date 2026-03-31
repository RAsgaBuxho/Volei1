from PIL import Image
import os

assets_dir = r"volei/assets"

# Converter JPEG para PNG
imagens = [
    ("Escudo vila linda.jpeg", "Escudo vila linda.png"),
    ("aguia do volei.jpeg", "aguia do volei.png")
]

for jpeg_file, png_file in imagens:
    jpeg_path = os.path.join(assets_dir, jpeg_file)
    png_path = os.path.join(assets_dir, png_file)
    
    if os.path.exists(jpeg_path):
        try:
            img = Image.open(jpeg_path)
            # Converter para RGB se necessário (remove alpha channel)
            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                rgb_img.save(png_path, "PNG", quality=95)
            else:
                img.save(png_path, "PNG", quality=95)
            print(f"✅ Convertido: {jpeg_file} → {png_file}")
        except Exception as e:
            print(f"❌ Erro ao converter {jpeg_file}: {e}")
    else:
        print(f"❌ Arquivo não encontrado: {jpeg_path}")

print("\n✅ Conversão concluída!")

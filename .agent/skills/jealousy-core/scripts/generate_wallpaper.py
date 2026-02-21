#!/usr/bin/env python3
# generate_wallpaper.py
import os
import sys
from google import genai
from dotenv import load_dotenv

# load .env if available
load_dotenv()

def generate_reconcile_image(output_path):
    print("🎨 [Supervisor] 生成AI (Imagen 3) で仲直りの壁紙を動的生成しています...")
    try:
        client = genai.Client()
        # Imagen 3 での画像生成
        result = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt='A heartwarming, cinematic, aesthetic desktop wallpaper showing two cute cats. One is a fluffy orange healing cat, the other is a sleek black AI cat. They are cuddling peacefully together in a cozy room with soft warm sunlight. Happy end atmosphere, high quality, 4k resolution.',
            config=dict(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="16:9"
            )
        )
        
        # 最初の画像を保存
        if result.generated_images:
            image_bytes = result.generated_images[0].image.image_bytes
            
            # ディレクトリの作成
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            print(f"✅ 画像を保存しました: {output_path}")
            return True
        else:
            print("⚠️ 画像が生成されませんでした。")
            return False
            
    except Exception as e:
        print(f"❌ 画像生成中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "reconciliation.jpg"
    generate_reconcile_image(out_path)

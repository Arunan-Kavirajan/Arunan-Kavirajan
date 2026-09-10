import cv2
import numpy as np
from rembg import remove
from PIL import Image
import io
import os

# Configuration
INPUT_IMAGE = "1000077404.png"
OUTPUT_SVG = "portrait.svg"
COLS = 90
RAMP = " .`:-=+*cs#%@"

def process_image(input_path):
    print("1/4: Removing background...")
    with open(input_path, 'rb') as i:
        input_data = i.read()
    subject_only = remove(input_data)
    img = Image.open(io.BytesIO(subject_only)).convert("RGBA")
    
    # Replace transparency with pure white
    white_bg = Image.new("RGBA", img.size, "WHITE")
    white_bg.paste(img, (0, 0), img)
    img = white_bg.convert("RGB")
    
    print("2/4: Cropping tightly to chest/neck level...")
    width, height = img.size
    # 0.52 keeps only the top 52% of the image, making the face larger in the grid
    crop_height = int(height * 0.52) 
    img = img.crop((0, 0, width, crop_height))
    
    print("3/4: Applying the digital darkroom pipeline...")
    cv_img = np.array(img)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
    
    # Bilateral Filter: Smooths the skin while keeping edges (eyes, jaw) sharp
    smoothed = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    
    # CLAHE: Local contrast per tile
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    contrasted = clahe.apply(smoothed)
    
    # Darkening curve: Fixes washout and forces shadows
    gamma = 1.7
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    darkened = cv2.LUT(contrasted, table)
    
    return Image.fromarray(darkened)

def generate_ascii_svg(img, cols):
    print("4/4: Generating SVG animation...")
    W, H = img.size
    rows = int(cols * (H / W) * 0.48)
    img = img.resize((cols, rows), Image.Resampling.LANCZOS)
    pixels = np.array(img)
    
    char_width = 7.74  
    char_height = 15
    svg_width = cols * char_width
    svg_height = rows * char_height
    
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%">',
        '<style>text { font-family: "JetBrains Mono", "DejaVu Sans Mono", "Liberation Mono", Consolas, monospace; font-size: 12.9px; fill: #737373; }</style>',
        f'<rect width="{svg_width}" height="{svg_height}" fill="transparent"/>'
    ]
    
    for i, row in enumerate(pixels):
        line_chars = []
        for pixel_val in row:
            ramp_idx = int(( (255 - pixel_val) / 255 ) * (len(RAMP) - 1))
            char = RAMP[ramp_idx]
            
            if char == '<': char = '&lt;'
            elif char == '>': char = '&gt;'
            elif char == '&': char = '&amp;'
            
            line_chars.append(char)
            
        text_str = "".join(line_chars)
        y_pos = (i + 1) * char_height
        clip_id = f"wipe{i}"
        delay = i * 0.09
        
        svg_lines.append(f'''
        <clipPath id="{clip_id}">
            <rect x="0" y="{y_pos - char_height}" width="0" height="{char_height}">
                <animate attributeName="width" values="0;{svg_width}" dur="0.5s" begin="{delay}s" fill="freeze" />
            </rect>
        </clipPath>
        <text x="0" y="{y_pos}" clip-path="url(#{clip_id})" xml:space="preserve">{text_str}</text>
        <rect x="0" y="{y_pos - char_height + 2}" width="{char_width}" height="{char_height - 2}" fill="#737373" opacity="0">
            <animate attributeName="x" values="0;{svg_width}" dur="0.5s" begin="{delay}s" fill="freeze" />
            <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.9;1" dur="0.55s" begin="{delay}s" fill="freeze" />
        </rect>
        ''')
        
    svg_lines.append('</svg>')
    
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))

if __name__ == "__main__":
    if not os.path.exists(INPUT_IMAGE):
        print(f"Error: {INPUT_IMAGE} not found in the root directory.")
        exit(1)
    processed_img = process_image(INPUT_IMAGE)
    generate_ascii_svg(processed_img, COLS)
    print(f"Success! Saved to {OUTPUT_SVG}")
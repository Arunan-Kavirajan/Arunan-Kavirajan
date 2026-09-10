import cv2
import numpy as np
from rembg import remove
from PIL import Image
import io

# Settings
INPUT_IMAGE = "image_321cb0.jpg"
OUTPUT_SVG = "portrait.svg"
COLS = 90
# The ASCII ramp from light to dark. Space is used for the removed background.
RAMP = " .`:-=+*cs#%@" 

def process_image(input_path):
    # 1. Remove Background
    with open(input_path, 'rb') as i:
        input_data = i.read()
    subject_only = remove(input_data)
    img = Image.open(io.BytesIO(subject_only)).convert("RGBA")
    
    # Create a white background to replace transparency (maps to empty space in ASCII)
    white_bg = Image.new("RGBA", img.size, "WHITE")
    white_bg.paste(img, (0, 0), img)
    img = white_bg.convert("RGB")
    
    # 2. Convert to OpenCV format (numpy array)
    cv_img = np.array(img)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
    
    # 3. Apply CLAHE (forces local contrast so your features don't wash out)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    contrasted = clahe.apply(gray)
    
    # 4. Apply Darkening Curve (Gamma Correction)
    # This pushes the mid-tones down so your suit and hair map to denser characters
    gamma = 1.7
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    darkened = cv2.LUT(contrasted, table)
    
    return Image.fromarray(darkened)

def generate_ascii_svg(img, cols):
    W, H = img.size
    # Monospace fonts are ~twice as tall as they are wide. 0.48 compensates for this.
    rows = int(cols * (H / W) * 0.48)
    img = img.resize((cols, rows), Image.Resampling.LANCZOS)
    pixels = np.array(img)
    
    # SVG Configuration
    char_width = 7.74  # Based on 12.9px font-size with 0.600em advance
    char_height = 15
    svg_width = cols * char_width
    svg_height = rows * char_height
    
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="100%" height="100%">',
        # Fallback fonts covering standard OS rendering
        '<style>text { font-family: "JetBrains Mono", "DejaVu Sans Mono", "Liberation Mono", Consolas, monospace; font-size: 12.9px; fill: #737373; }</style>',
        f'<rect width="{svg_width}" height="{svg_height}" fill="transparent"/>'
    ]
    
    for i, row in enumerate(pixels):
        line_chars = []
        for pixel_val in row:
            # Map pixel brightness (0-255) to ramp index (0-12)
            # Invert so dark pixels = dense characters
            ramp_idx = int(( (255 - pixel_val) / 255 ) * (len(RAMP) - 1))
            char = RAMP[ramp_idx]
            
            # HTML escape
            if char == '<': char = '&lt;'
            elif char == '>': char = '&gt;'
            elif char == '&': char = '&amp;'
            
            line_chars.append(char)
            
        text_str = "".join(line_chars)
        y_pos = (i + 1) * char_height
        
        # SMIL Animation: ClipPath typing effect
        clip_id = f"wipe{i}"
        delay = i * 0.09
        
        svg_lines.append(f'''
        <clipPath id="{clip_id}">
            <rect x="0" y="{y_pos - char_height}" width="0" height="{char_height}">
                <animate attributeName="width" values="0;{svg_width}" dur="0.5s" begin="{delay}s" fill="freeze" />
            </rect>
        </clipPath>
        <text x="0" y="{y_pos}" clip-path="url(#{clip_id})" xml:space="preserve">{text_str}</text>
        <!-- The little cursor block -->
        <rect x="0" y="{y_pos - char_height + 2}" width="{char_width}" height="{char_height - 2}" fill="#737373" opacity="0">
            <animate attributeName="x" values="0;{svg_width}" dur="0.5s" begin="{delay}s" fill="freeze" />
            <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.9;1" dur="0.55s" begin="{delay}s" fill="freeze" />
        </rect>
        ''')
        
    svg_lines.append('</svg>')
    
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))

if __name__ == "__main__":
    print("Processing image...")
    processed_img = process_image(INPUT_IMAGE)
    print("Generating ASCII SVG...")
    generate_ascii_svg(processed_img, COLS)
    print(f"Done! Saved to {OUTPUT_SVG}")
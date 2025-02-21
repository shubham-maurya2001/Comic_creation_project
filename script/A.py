import google.generativeai as genai
import os
from PIL import Image, ImageDraw, ImageFont

# 🔹 Configure Google Gemini API Key
genai.configure(api_key="AIzaSyAMJvhklS_aLswXGyPpySOABH3lEz5h5Ls")  # Replace with your actual API key

# 🔹 Function to Generate Captions Using Gemini
def generate_captions(user_input, num_captions=5):
    """Generate comic captions using Google Gemini API."""
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Generate {num_captions} short, engaging captions for a comic about: {user_input}. Provide only the list."

    try:
        response = model.generate_content(prompt)
        if response and response.text:
            captions = [line.strip('- ') for line in response.text.strip().split("\n") if line]
            return captions[:num_captions]  # Ensure correct number of captions
        else:
            print("❌ No captions generated.")
            return []
    except Exception as e:
        print(f"❌ API Error: {e}")
        return []

# 🔹 Function to Overlay Text on Image
def overlay_text_on_image(image_path, text, output_path):
    """Overlays text on an image and saves it."""
    try:
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        # Load a font (default if no TTF available)
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()

        # Calculate text size correctly
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        img_width, img_height = image.size
        position = ((img_width - text_width) // 2, img_height - 50)

        # Draw text
        draw.rectangle([(position[0] - 10, position[1] - 5), (position[0] + text_width + 10, position[1] + text_height + 5)], fill=(0, 0, 0, 150))
        draw.text(position, text, fill="white", font=font)

        image.save(output_path)
        return output_path
    except Exception as e:
        print(f"❌ Error overlaying text: {e}")
        return None

# 🔹 Function to Combine Images into a Comic Strip
def create_comic_strip(image_paths, output_filename="final_comic.png", layout="grid", images_per_row=3):
    """Combines images into a comic strip."""
    images = [Image.open(img) for img in image_paths if os.path.exists(img)]
    if not images:
        print("❌ No valid images to create a comic strip.")
        return
    img_width, img_height = images[0].size

    rows = (len(images) + images_per_row - 1) // images_per_row
    final_width = img_width * images_per_row
    final_height = img_height * rows
    comic_strip = Image.new("RGB", (final_width, final_height), (255, 255, 255))

    x_offset, y_offset = 0, 0
    for i, img in enumerate(images):
        comic_strip.paste(img, (x_offset, y_offset))
        x_offset += img_width
        if (i + 1) % images_per_row == 0:
            x_offset = 0
            y_offset += img_height

    comic_strip.save(output_filename)
    print(f"✅ Comic strip saved as {output_filename}")

# 🔹 Main Execution
if __name__ == "__main__":
    user_theme = input("Enter a comic theme : ")
    
    image_folder = "./images"  # Change to your image folder
    image_files = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith((".png", ".jpg", ".jpeg"))])

    if not image_files:
        print("❌ No images found in the folder.")
        exit()

    captions = generate_captions(user_theme, num_captions=len(image_files))
    if captions:
        captioned_images = [overlay_text_on_image(img, cap, f"captioned_{i+1}.png") for i, (img, cap) in enumerate(zip(image_files, captions))]
        captioned_images = [img for img in captioned_images if img]

        if captioned_images:
            create_comic_strip(captioned_images, output_filename="final_comic.png", layout="grid", images_per_row=3)
    else:
        print("❌ Failed to generate captions.")

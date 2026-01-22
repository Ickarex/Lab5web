from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS
import urllib.request
import os
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
image_downloaded = False

# Создаем папку resources при запуске приложения
def ensure_resources_folder():
    resources_path = "resources"
    if not os.path.exists(resources_path):
        os.makedirs(resources_path, exist_ok=True)
        print(f"Created {resources_path} directory")

# Вызываем при запуске
ensure_resources_folder()

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/api/changeimage", methods=['POST'])
def change():
    data = request.json
    url = data.get('url')
    mode = data.get('mode')
    print("="*50)
    print(f"url: {url}; mode: {mode}")
    print("="*50)
    filename = "resources/temp_image.png"

    if not url :
        return jsonify({"error": "неверные данные"}), 400
    
    if not image_downloaded:        
        urllib.request.urlretrieve(url, filename)
        image_downloaded = True

    loadedImage = Image.open(filename)
    if mode == "change":
        changedImage = changeImage(loadedImage)
    elif mode == "watermark":
        changedImage = watermarkAdd(loadedImage)
    else:
        changedImage = loadedImage
    changedImage.save(filename)
    return jsonify({
        "message": f"succesful, mode: {mode}",
        "url": "/getimage"
        })

#endpoint для получения локального обработанного изображения
@app.route('/getimage')
def getimage():
    return send_from_directory('resources', 'temp_image.png')

def changeImage(image):
    print("Image is changing now")
    image_arr = np.array(image)
    image_arr = np.transpose(image_arr, (1,0,2))
    res = Image.fromarray(image_arr)
    return res

def watermarkAdd(image):
    print("Watermark on/off")
    watermark = Image.open("./resources/watermark.png")
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    if watermark.mode != 'RGBA':
        watermark = watermark.convert('RGBA')
    bg_width, bg_height = image.size
    wm_width, wm_height = watermark.size
    x = bg_width - wm_width
    y = bg_height - wm_height
    image.paste(watermark, (x, y), watermark)
    return image

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
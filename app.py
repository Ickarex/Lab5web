from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS
import urllib.request
import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


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
    image_downloaded = data.get("isloaded")
    watermark_active = data.get("iswatermark")
    chessSize = int(data.get("chessSize"))
    print(f"chessSize: {chessSize}")
    if (not chessSize) | (chessSize < 1):
        chessSize = 1
    elif (chessSize > 100):
        chessSize = 100
    print("="*50)
    print(f"url: {url}; mode: {mode}")
    print("="*50)
    filename = "resources/temp_image.png"
    img_without_wm = "resources/temp_image_without_watermark.png"

    if not url :
        return jsonify({"error": "неверные данные"}), 400
    
    if not image_downloaded:        
        urllib.request.urlretrieve(url, filename)
        image_downloaded = True

    loadedImage = Image.open(filename)

    if mode == "change":
        changedImage = changeImage(loadedImage, chessSize)
    elif (mode == "watermark") & watermark_active:
        loadedImage.save(img_without_wm)
        changedImage = watermarkAdd(loadedImage)
    elif (mode == "watermark") & (not watermark_active):
        changedImage = Image.open(img_without_wm)
    elif (mode == "return"):
        urllib.request.urlretrieve(url, filename)
        changedImage = Image.open(filename)
    else:
        changedImage = loadedImage
        changedImage.save(img_without_wm)
    changedImage.save(filename)
    gist(changedImage)
    return jsonify({
        "message": f"succesful, mode: {mode}",
        "chessSize": f"{chessSize}",
        "url": "/getimage",
        "graphurl": "/getgraph"
        })

#endpoint для получения локального обработанного изображения
@app.route('/getimage')
def getimage():
    return send_from_directory('resources', 'temp_image.png')

@app.route('/getgraph')
def getgraph():
    return send_from_directory('resources', 'graph.png')

def gist(image):
    img_array = np.array(image)
    r_channel = img_array[:,:,0].ravel()
    g_channel = img_array[:,:,0].ravel()
    b_channel = img_array[:,:,0].ravel()

    plt.figure(figsize=(12,8))
    plt.subplot(1,3,1)
    plt.hist(r_channel, bins=256, color='red', alpha=1, label='Red')
    plt.ylabel('Частота')
    plt.subplot(1,3,2)
    plt.hist(g_channel, bins=256, color='green', alpha=1, label='Green')
    plt.title('Распределение цветов по каналам')
    plt.xlabel('Значение пикселя')   
    plt.subplot(1,3,3)
    plt.hist(b_channel, bins=256, color='blue', alpha=1, label='Blue') 
    plt.grid(True, alpha=0.3)
    plt.savefig("resources/graph.png", dpi=300, bbox_inches='tight')
    plt.close

def changeImage(image, chessSize):
    print("Image is changing now")
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    image_arr = np.array(image)
    height, width = image_arr.shape[:2]
    cell_h, cell_w = height*chessSize//100, width*chessSize//100
    for i in range(0, height, 2*cell_h):
        for j in range(0, width, 2*cell_w):
            image_arr[i:cell_h+i,j:cell_w+j,:] = [255,255,255,1]
            image_arr[i+cell_h:i+2*cell_h, j+cell_w:j+2*cell_w,:] = [255,255,255,1]
    image = Image.fromarray(image_arr)
    return image

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
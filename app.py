from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_cors import CORS
import urllib.request
import os
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app)

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
    if not url :
        return jsonify({"error": "неверные данные"}), 400
    print(url)
    filename = "./resources/temp_image.jpg"
    urllib.request.urlretrieve(url, filename)
    loadedImage = Image.open(filename)
    changedImage = changeImage(loadedImage)
    changedImage.save(filename)
    return jsonify({
        "message": "succesful",
        "url": "/getimage"
        })

#endpoint для получения локального обработанного изображения
@app.route('/getimage')
def getimage():
    return send_from_directory('resources', 'temp_image.jpg')

def changeImage(image):
    print("Image is changing now")
    image_arr = np.array(image)
    image_arr = np.transpose(image_arr, (1,0,2))
    res = Image.fromarray(image_arr)
    return res

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
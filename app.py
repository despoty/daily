from flask import Flask, redirect
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
from datetime import datetime
import os

app = Flask(__name__)

# 获取 Bing 每日一图 URL
def get_bing_image_url():
    url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1"
    response = requests.get(url)
    data = response.json()
    image_url = "https://www.bing.com" + data['images'][0]['url']
    return image_url

# 高斯模糊和裁剪处理
def process_image(image_url, date_obj=None):
    if date_obj is None:
        date_obj = datetime.now()
        
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    img = img.resize((1600, 400))
    img = img.filter(ImageFilter.GaussianBlur(radius=3))

    current_time = date_obj.strftime("%Y年%m月%d日")
    font_path = "./font/PingFang.otf"
    font = ImageFont.truetype(font_path, size=90)

    draw = ImageDraw.Draw(img)
    text_bbox = draw.textbbox((0, 0), current_time, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((img.width - text_width) // 2, int((img.height - text_height) // 2.5))

    shadow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)
    shadow_offset = (2, 2)
    shadow_position = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
    shadow_draw.text(shadow_position, current_time, fill="black", font=font)
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=3))
    img.paste(shadow_img, (0, 0), shadow_img)

    draw.text(position, current_time, fill="white", font=font)

    now = date_obj
    directory = f"/image/{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}"
    os.makedirs(directory, exist_ok=True)
    output_image_path = f"{directory}/daily-{now.strftime('%Y%m%d')}.png"
    img.save(output_image_path)
    
    image_url_prefix = os.environ.get('IMAGE_URL_PREFIX', 'https://image.95pter.com/')
    url = f"{image_url_prefix}{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}/daily-{now.strftime('%Y%m%d')}.png"
    return url

@app.route('/')
def index():
    image_url = get_bing_image_url()
    url = process_image(image_url)
    return redirect(url)

@app.route('/<date_str>')
def index_date(date_str):
    try:
        parsed_date = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        parsed_date = datetime.now()
    image_url = get_bing_image_url()
    url = process_image(image_url, date_obj=parsed_date)
    return redirect(url)

if __name__ == "__main__":
    app.run(debug=True)

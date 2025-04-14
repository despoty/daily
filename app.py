import os
from flask import Flask, send_file, request
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
def process_image(image_url, date):
    # 获取图像数据
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # 高分辨率处理，使用更大的尺寸
    img = img.resize((1600, 400))  # 增加分辨率，确保文本清晰

    # 高斯模糊
    img = img.filter(ImageFilter.GaussianBlur(radius=3))

    # 使用指定日期或当前日期
    current_time = date.strftime("%Y年%m月%d日")

    # 使用支持中文的OTF字体（确保字体文件存在）
    font_path = "./font/PingFang.otf"  # 请确保路径和字体文件正确
    font = ImageFont.truetype(font_path, size=90)  # 增加字体大小

    # 在图片上添加日期
    draw = ImageDraw.Draw(img)

    # 使用 textbbox 计算文本边界框
    text_bbox = draw.textbbox((0, 0), current_time, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # 计算文本位置
    position = ((img.width - text_width) // 2, int((img.height - text_height) // 2.5))

    # 添加黑色阴影并应用高斯模糊
    shadow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)
    shadow_offset = (2, 2)  # 可调整阴影偏移值
    shadow_position = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
    shadow_draw.text(shadow_position, current_time, fill="black", font=font)
    # 应用高斯模糊
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=3))
    # 将模糊后的阴影合并到原图
    img.paste(shadow_img, (0, 0), shadow_img)

    # 在图像上绘制日期文字
    draw.text(position, current_time, fill="white", font=font)

    # 保存或返回图像
    now = date
    directory = f"./image/{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}"
    os.makedirs(directory, exist_ok=True)
    output_image_path = f"{directory}/daily-{now.strftime('%Y%m%d')}.png"
    img.save(output_image_path)
    
    # 使用环境变量中的 URL 前缀（默认为 https://image.95pter.com/）
    image_url_prefix = os.environ.get('IMAGE_URL_PREFIX', 'https://image.95pter.com/')
    url = f"{image_url_prefix}{now.strftime('%Y')}/{now.strftime('%m')}/{now.strftime('%d')}/daily-{now.strftime('%Y%m%d')}.png"
    return url

@app.route('/generate', methods=['GET'])
def generate_image():
    # 获取 URL 中的日期参数，格式为 YYYYDDMM
    date_str = request.args.get('date')

    # 检查是否提供日期，并且日期格式正确
    if date_str and len(date_str) == 8:
        try:
            # 尝试将日期字符串解析为日期
            date = datetime.strptime(date_str, "%Y%d%m")
        except ValueError:
            return "Invalid date format. Please use YYYYDDMM.", 400
    else:
        # 如果没有日期参数或格式错误，使用当前日期
        date = datetime.now()

    # 获取 Bing 图片 URL
    image_url = get_bing_image_url()

    # 处理图像并获得本地文件路径
    output_image_path = process_image(image_url, date)

    # 返回处理后的图片
    return send_file(output_image_path, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)

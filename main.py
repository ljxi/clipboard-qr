#!/usr/bin/env python3
"""
剪切板二维码工具
1. 无参数：读取剪切板图片并识别 (pyzbar)
2. 有参数：将参数内容生成二维码，打印到终端并复制图像到剪切板 (qrcode)
"""

import sys
import io
from PIL import ImageGrab, Image
from pyzbar import pyzbar
import pyperclip
import qrcode

def get_clipboard_image():
    """从剪切板获取图片"""
    try:
        img = ImageGrab.grabclipboard()
        if img is None:
            return None
        # 如果是文件路径列表，读取第一个图片文件
        if isinstance(img, list):
            if len(img) > 0 and img[0].lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                img = Image.open(img[0])
            else:
                return None
        return img
    except Exception as e:
        print(f"获取剪切板图片时出错: {e}")
        return None

def decode_qrcode(image):
    """解码图片中的二维码"""
    try:
        decoded_objects = pyzbar.decode(image)
        if not decoded_objects:
            print("图片中没有检测到二维码")
            return None
        
        results = []
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            results.append({'type': obj.type, 'data': data})
        return results
    except Exception as e:
        print(f"解码二维码时出错: {e}")
        return None

def generate_and_copy_qr(text):
    """生成二维码，打印 ASCII 并复制到剪切板"""
    try:
        # 1. 创建二维码对象
        qr = qrcode.QRCode(border=2)
        qr.add_data(text)
        qr.make(fit=True)

        # 2. 在终端打印 ASCII 二维码
        print(text)
        qr.print_ascii(invert=True)

        # 3. 生成图像并复制到剪切板
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 将 PIL Image 放入剪切板 (Windows 环境下的特殊处理)
        output = io.BytesIO()
        img.save(output, format='PNG')
        data = output.getvalue()
        output.close()

        # 注意：ImageGrab 只能读取，写入剪切板通常需要依赖特定平台的库或重载
        # 这里使用一种简单且兼容性较好的方式重新把 img 存入剪切板
        send_to_clipboard(img)
        
        print("✓ 二维码图像已复制到剪切板！")
    except Exception as e:
        print(f"生成二维码失败: {e}")

def send_to_clipboard(image):
    """将 PIL Image 对象存入剪切板 (兼容 Windows/macOS)"""
    import platform
    curr_os = platform.system()
    
    if curr_os == "Windows":
        # Windows 需要特殊格式
        output = io.BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]  # 去掉 BMP 文件头
        output.close()
        
        import win32clipboard
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        finally:
            win32clipboard.CloseClipboard()
    elif curr_os == "Darwin": # macOS
        output = io.BytesIO()
        image.save(output, format="PNG")
        data = output.getvalue()
        output.close()
        
        import subprocess
        p = subprocess.Popen(['pbcopy', '-Prefer', 'png'], stdin=subprocess.PIPE)
        p.communicate(input=data)

def main():
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 模式：生成二维码
        content = " ".join(sys.argv[1:])
        generate_and_copy_qr(content)
    else:
        # 模式：识别二维码
        img = get_clipboard_image()
        if img is None:
            print("提示：剪切板中没有图片。")
            print("用法：")
            print("  识别：先复制图片，然后直接运行脚本")
            print("  生成：qr '要生成的文本'")
            return
        
        results = decode_qrcode(img)
        if results:
            content = "\n".join([i['data'] for i in results])
            print(content)
            pyperclip.copy(content)
            print(f"✓ 已识别 {len(results)} 个二维码，内容已复制到剪切板：")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"\n发生错误: {e}")
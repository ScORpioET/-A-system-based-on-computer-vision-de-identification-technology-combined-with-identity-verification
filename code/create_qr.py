import os
import qrcode
from PIL import Image
from pyzbar import pyzbar


def make_qr_code_easy(content, save_path=None):
    img = qrcode.make(data=content)
    if save_path:
        img.save(save_path)
    else:
        img.show()


def make_qr_code(content, save_path=None):
    qr_code_maker = qrcode.QRCode(version=5,
                                  error_correction=qrcode.constants.ERROR_CORRECT_M,
                                  box_size=8,
                                  border=4,
                                  )
    qr_code_maker.add_data(data=content)
    qr_code_maker.make(fit=True)
    img = qr_code_maker.make_image(fill_color="black", back_color="white")
    if save_path:
        img.save(save_path)
    else:
        img.show()  # 中間圖不顯示


def make_qr_code_with_icon(content, icon_path, save_path=None):
    if not os.path.exists(icon_path):
        raise FileExistsError(icon_path)

    # First, generate an usual QR Code image
    qr_code_maker = qrcode.QRCode(version=5,
                                  error_correction=qrcode.constants.ERROR_CORRECT_H,
                                  box_size=8,
                                  border=4,
                                  )
    qr_code_maker.add_data(data=content)
    qr_code_maker.make(fit=True)
    qr_code_img = qr_code_maker.make_image(
        fill_color="black", back_color="white").convert('RGBA')

    # Second, load icon image and resize it
    icon_img = Image.open(icon_path)
    code_width, code_height = qr_code_img.size
    icon_img = icon_img.resize(
        (code_width // 4, code_height // 4), Image.ANTIALIAS)

    # Last, add the icon to original QR Code
    qr_code_img.paste(icon_img, (code_width * 3 // 8, code_width * 3 // 8))

    if save_path:
        qr_code_img.save(save_path)  # 保存二維碼圖片
        # qr_code_img.show()  # 顯示二維碼圖片
    else:
        print("save error!")


def decode_qr_code(code_img_path):
    if not os.path.exists(code_img_path):
        raise FileExistsError(code_img_path)

    # Here, set only recognize QR Code and ignore other type of code
    return pyzbar.decode(Image.open(code_img_path), symbols=[pyzbar.ZBarSymbol.QRCODE])


if __name__ == "__main__":
    print("============QRcodetest===============")
    print("         1、Make a QRcode            ")
    print("         2、Scan a QRcode            ")
    print("=====================================")
    print("1、請輸入編碼信息：")
    # code_Data = input('>>:').strip()
    code_Data = ''
    for i in range(2953):
        code_Data += '1'
    print("正在編碼：")
    # ==生成普通二維碼
    make_qr_code_easy("make_qr_code_easy", "qrcode.png")
    results = decode_qr_code("qrcode.png")
    if len(results):
        print(results[0].data.decode("utf-8"))
    else:
        print("Can not recognize.")
    # ==帶圖片二維碼解碼
    make_qr_code("make_qr_code", "qrcode.png")
    results = decode_qr_code("qrcode.png")
    if len(results):
        print(results[0].data.decode("utf-8"))
    else:
        print("Can not recognize.")
    # ==生成帶中心圖片的二維碼
    make_qr_code_with_icon(
        code_Data, "gray.png", "qrcode.png")  # 內容，center圖片，生成二維碼圖片
    results = decode_qr_code("qrcode.png")
    print("2、正在解碼：")
    if len(results):
        print("解碼結果是：")
        print(results[0].data.decode("utf-8"))
    else:
        print("Can not recognize.")
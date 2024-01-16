from io import BytesIO

import qrcode
from PIL import Image


def generate(url, **kwargs):
    fill_color = "black"
    back_color = "white"
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color=fill_color, back_color=back_color)

    # if "logo" in kwargs:
    #     logo = Image.open((kwargs["logo"]))
    #     base_width = 100
    #
    #     # adjust logo size
    #     width_percent = base_width / float(logo.size[0])
    #     height_size = int((float(logo.size[1]) * float(width_percent)))
    #     logo = logo.resize((base_width, height_size), Image.ANTIALIAS)
    #     new_logo_size = (
    #         (qr_image.size[0] - logo.size[0]) // 2,
    #         (qr_image.size[1] - logo.size[1]) // 2,
    #     )
    #     qr_image.paste(logo, new_logo_size)

    stream = BytesIO()
    qr_image.save(stream, "PNG")
    return stream


def qr_generate(url=None, logo_link=None, **kwargs):
    # taking base width
    basewidth = 1000
    if logo_link:
        logo = Image.open(logo_link)
        # adjust image size
        width, height = qr_size_calculate(basewidth, logo)
        logo = logo.resize((width, height), Image.ANTIALIAS)

    QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)

    # adding URL or text to QRcode
    QRcode.add_data(url)

    # generating QR code
    QRcode.make()

    # taking color name from user
    QRcolor = "#000000"

    # adding color to QR code
    QRimg = QRcode.make_image(fill_color=QRcolor, back_color="white").convert("RGB")
    QRimg = QRimg.resize((1000, 1000))
    if logo_link:
        # set size of QR code
        pos = ((QRimg.size[0] - logo.size[0]) // 2, (QRimg.size[1] - logo.size[1]) // 2)
        QRimg.paste(logo, pos)

    # save the QR code generated
    # QRimg.save("gfg_QR.png")

    stream = BytesIO()
    QRimg.save(stream, "PNG")
    return stream


def qr_size_calculate(basewidth=None, logo=None):
    # adjust image size
    if logo:
        wpercent = basewidth / (float(logo.size[0]))
        hsize = int((float(logo.size[1]) * float(wpercent)))
        if hsize > 250:
            return qr_size_calculate(basewidth / 1.1, logo)
        return int(basewidth), hsize
    return 0, 0

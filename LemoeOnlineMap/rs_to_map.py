from PIL import Image, ImageFile
import os
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None


def parse_image(rspic, x_start=0, y_start=0):
    size = rspic.size[0]
    size_now = size
    if not os.path.exists('./static/map_db/'):
        os.mkdir('./static/map_db/')
    for z in range(10):
        if not os.path.exists(f'./static/map_db/{z}/'):
            os.mkdir(f'./static/map_db/{z}/')
        scale = int(2 ** z)
        for x in range(scale):
            if not os.path.exists(f'./static/map_db/{z}/{-(scale + 1) // 2 + x + 1}/'):
                os.mkdir(f'./static/map_db/{z}/{-(scale + 1) // 2 + x + 1}/')
            for y in range(scale):
                pic = rspic.crop((x * size / (2 ** z), y * size / (2 ** z), (x + 1) * size / (2 ** z), (y + 1) * size / (2 ** z)))
                # print(pic.size)
                if pic.size[0] != 256:
                    pic = pic.resize((256, 256))
                pic.save(f'./static/map_db/{z}/{-(scale + 1) // 2 + x + 1}/{-(scale + 1) // 2 + y + 1}.webp')
        size_now = size_now // 2
        if size_now < 256: break
    return


'''
def parse_dir(dir0):
    for i in range(-4, 4):
        for j in range(-4, 4):
            pic = Image.open(f'{dir0}/{i}_{j}.png')
            parse_image(pic, i, j)
    return
'''


if __name__ == '__main__':
    from tkinter.filedialog import askdirectory
    from tkinter.filedialog import askopenfilename
    pic0 = askopenfilename(title='打开图片')
    pic0 = Image.open(pic0)
    parse_image(pic0)

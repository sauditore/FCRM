from wand.image import Image


def create_file_preview(in_file, out_file):
    try:
        i = Image(filename=in_file, depth=32, resolution=150)
        converted = i.convert('jpg')
        converted.resize(200, 100)
        converted.save(filename=out_file)
        return True
    except:
        return False

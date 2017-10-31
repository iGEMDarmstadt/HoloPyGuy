import os
from PIL import Image
import numpy as np

#Takes all pics in "raw pics" directory, convert to grey scale,
#cutting into square images, and same to "ready pics" directory


def create_temp_pictures(filenames):
    filelist = []
    cnt = 0
    for filename in filenames:
        im = Image.open(filename)

        half_the_width = im.size[0] / 2
        half_the_height = im.size[1] / 2

        cut = np.minimum(half_the_height, half_the_width)

        im = im.crop(
                    (
                half_the_width - cut,
                half_the_height - cut,
                half_the_width + cut,
                half_the_height + cut
                    )
                )
        im = im.convert('L')
        im.save(".{}.jpeg".format(cnt))
        filelist.append(".{}.jpeg".format(cnt))
        cnt = cnt + 1

    print(filelist)
    return filelist

# dir_pic = os.path.join(os.getcwd(), 'raw pics')
# out_dir = os.path.join(os.getcwd(), 'ready pics')
# dir_pic = os.path.join(os.getcwd(), 'new_pic_raw')
# out_dir = os.path.join(os.getcwd(), 'new_pic_ready')


if __name__ == "__main__":
    # dir_pic = os.path.join(os.getcwd(), 'raw pics')
    # out_dir = os.path.join(os.getcwd(), 'ready pics')
    # dir_pic = os.path.join(os.getcwd(), 'new_pic_raw')
    # out_dir = os.path.join(os.getcwd(), 'new_pic_ready')
    dir_pic = os.path.join(os.getcwd(), '10_26')
    out_dir = os.path.join(os.getcwd(), '10_26_processed')

    # os.chdir(dir_pic)

    for filename in os.listdir(dir_pic):
        print(filename)
        im = Image.open(dir_pic + '/' + filename)

        print(im.format, im.size, im.mode)

        half_the_width = im.size[0] / 2
        half_the_height = im.size[1] / 2

        cut = np.minimum(half_the_height, half_the_width)

        im1 = im.crop(
            (
                half_the_width - cut,
                half_the_height - cut,
                half_the_width + cut,
                half_the_height + cut
            )
        )

        print(im1.format, im1.size, im1.mode)
        im1.save(os.path.join(out_dir, filename))
        os.chdir(out_dir)
        os.system("convert " + str(filename) + " -set colorspace Gray -separate -average " + str(filename))


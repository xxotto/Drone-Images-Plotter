import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import Image

import utils as ut


def coordinate_plot(x, y, label):

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.ticklabel_format(useOffset=False, style="plain", axis="both")

    plt.grid(True, linewidth=.5, linestyle="-")  # Configure grid
    plt.rcParams["axes.axisbelow"] = True
    ax.scatter(x, y, s=65, color="steelblue")

    ax.scatter(x[0], y[0], s=65, color="green", label=label[0].split("/")[-1])
    ax.scatter(x[-1], y[-1], s=65, color="darkred", label=label[-1].split("/")[-1])

    [ax.annotate(i, (x[i], y[i]), fontsize=14) for i in range(len(x))]

    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.title("Latitude and Longitude Coordinates", fontsize=16, weight="bold")
    plt.xlabel("Longitude", fontsize=14)
    plt.ylabel("Latitude", fontsize=14, rotation=90)
    plt.legend()

    plt.savefig("results/coordinates_plot.png")


def remove_extra_white_spaces(image):

    # Load image, grayscale, Gaussian blur, Otsu's threshold
    original=image.copy()
    gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur=cv2.GaussianBlur(gray, (25, 25), 0)
    thresh=cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Perform morph operations, first open to remove noise, then close to combine
    noise_kernel=cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening=cv2.morphologyEx(thresh, cv2.MORPH_OPEN, noise_kernel, iterations=2)
    close_kernel=cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    close=cv2.morphologyEx(opening, cv2.MORPH_CLOSE, close_kernel, iterations=3)

    # Find enclosing boundingbox and crop ROI
    coords=cv2.findNonZero(close)
    x, y, w, h=cv2.boundingRect(coords)
    cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 2)
    crop=original[y:y+h, x:x+w]

    return crop



def generate_mosaic(df, max_size_bg):

    fig, ax=plt.subplots()
    bg=np.zeros(max_size_bg, dtype="uint8")

    for i in range(len(df)):
        print(f"\r ### Plotting image {i+1}/{len(df)} ###", end = "")
        im = ut.resize_image(cv2.imread(df.index[i]), df.relative_alt[i])
        im = ut.rotate_image(im, df.yaw[i], df.pitch[i], df.roll[i])
        im = ut.generate_image_transparency(im)
        
        if df.yaw[i] > 0:
            transfer = 50  # move 50 pixels
        else:
            transfer = 0
            
        ut.add_transparent_image(bg, im, df.x_ppm[i] + transfer, df.y_ppm[i])
    
    print()
    
    rslt_path = 'results/images_mosaic.png'
    cv2.imwrite(rslt_path, ut.generate_image_transparency(bg))
    
    # CROP EMPTY SPACES WITH PIL
    im = Image.open(rslt_path)
    im = im.crop(im.getbbox())
    im.save(rslt_path)
    



# Drone images plotter (DIP)
Simple drone images plotter for cases when there is no overlapping between photos.

**Example result:**

![example_result](https://github.com/xxotto/Drone-Images-Plotter/blob/main/results/images_mosaic.png)

Assumptions for running DIP:

- Images taken at a height of 25 or 40 meters.
- All images belong to a specific area.
- Images have EXIF metadata for latitude, longitude, width and height.
- Images have XMP metadata for relative height (above ground level), drone yaw, pitch and roll.

## How to use
1. Clone this repository
```
git clone https://github.com/xxotto/Drone-Images-Plotter.git
cd Drone-Images-Plotter
```

2. Download test images and place them in a folder called images
```
wget --content-disposition https://www.dropbox.com/s/zwonz95jwe41hg9/images.zip?dl=0
mkdir images
unzip -d images/ images.zip
rm images.zip
```

3. Create a virtual environment and install `requirements.txt`
```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

4. Run `DIP.py`
```
python3 DIP.py 
```

## Notes
The python `geometry.py` code was taken from alexhagiopol's [orthomosaic](https://github.com/alexhagiopol/orthomosaic) repository.

If your photos are not taken with a DJI drone and you have keyword errors in `metadata.py` please check the **xmp** function inside this file. You need to uncomment the *'Uncomment to print all xmp metadata'* section, and review the tags your drone uses.

In this way you will be able to add the relative altitude, yaw, pitch and roll labels that your drone has. Please add these tags to the variables, agl_tags, yaw_tags, pitch_tags, and roll_tags in the **get_above_ground_level** and **get_yaw_pitch_roll** functions respectively.

## Future work

- Find an alternative to improve the position of the images.
- Generate orthophotos and use them instead of using raw images.
- Take into account images with altitudes other than 25 or 40 meters.
- Improve and optimize some functions.
- Use a better method to regulate the size of the final result.

## Author

Otto Proaño ([@xxotto](https://github.com/xxotto))

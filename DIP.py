import glob
import pandas as pd
import os

import metadata as md
import graphs as gp
import coords_transform as ct



def main():
    
    # Get image paths
    img_paths = sorted(glob.glob('images/*.JPG'))
    
    # Create location where program places results
    if not os.path.exists('results'):
        os.makedirs('results')
    
    # Extract metadata
    img_md_lst = []
    [img_md_lst.append(md.get_metadata_from_an_img(img_path)) for img_path in img_paths]
    df = pd.DataFrame(img_md_lst).set_index("img_path").rename_axis(None)
    
    # Graph coordinates
    gp.coordinate_plot(x = df.longitude, y = df.latitude, label = df.index)
    
    # Convert reference coordinates to pixels
    zero = (df.longitude.min(), df.latitude.min())
    df[["x_mts", "y_mts"]] = df.apply(lambda row : ct.coords_to_meters(zero, row["longitude"], row["latitude"]), axis = 1).to_list()
    max_pixels_size = ct.from_meters_to_pixels(df)
    df["y_ppm"] = (df.y_ppm - df.y_ppm.max())*-1
    
    # Generate image mosaic
    gp.generate_mosaic(df, max_pixels_size)
    
    
    
if __name__ == "__main__":
  main()
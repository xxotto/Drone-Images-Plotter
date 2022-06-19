from PIL import Image
from exif import Image as exif_Image
import xmltodict
import fractions
from fractions import Fraction



def get_dimensions(imagePath):
    """Extrae las dimensiones, ancho (width) y alto (height) de la metadata de una imagen"""
    dimensions = {"width": None, "height": None}
    try:
        with open(imagePath, "rb") as src:
            img = exif_Image(src)
        if img.has_exif:
            try:
                dimensions["width"] = img.pixel_x_dimension
                dimensions["height"] = img.pixel_y_dimension
            except AttributeError:
                print(AttributeError)
        else:
            print(f"There is NO exif information in {imagePath}")
            return dimensions
    except Exception as e:
        print(f"ERROR in 'get_dimensions' while processing {imagePath} \n{e}")
    return dimensions



def decimal_coords(coords, ref):
    """Transforma coordenadas geográficas a coordenadas decimales"""
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees



def get_image_coordinates(imagePath):
    """Extrae coordenadas (latitud, longitud y altitud) de la metadata de una imagen"""
    coords = {"latitude": None, "longitude": None, "altitude": None}
    try:
        with open(imagePath, "rb") as src:
            img = exif_Image(src)
        if img.has_exif:
            try:
                coords["latitude"] = round(decimal_coords(
                    img.gps_latitude, img.gps_latitude_ref), 6)
                coords["longitude"] = round(decimal_coords(
                    img.gps_longitude, img.gps_longitude_ref), 6)
                coords["altitude"] = round(img.gps_altitude, 6)
            except AttributeError:
                print(AttributeError)
        else:
            print(f"There is NO exif information in {imagePath}")
            return coords
    except Exception as e:
        print(
            f"ERROR in 'get_image_coordinates' while processing {imagePath} \n{e}")
        return coords
    return coords



def get_above_ground_level(metadata):
    """Extrae la altura relativa del dron, también llamada altura sobre el nivel del suelo.
    IMPORTANTE: Dependiendo el tipo de dron usado, la metadata puede cambiar de etiquetas, por lo que se pueden
    generar errores de 'keywords más adelante. Se recomienda seguir añadiendo nuevas etiquetas a la 'TAG list'"""
    alt = {"relative_alt": None}
    # TAG LIST: Keep adding tags of each new drone model
    agl_tags = ["Camera:AboveGroundAltitude", "@drone-dji:RelativeAltitude"]
    try:
        for key, values in metadata["x:xmpmeta"]["rdf:RDF"]["rdf:Description"].items():
            if key in agl_tags:
                # Analize what type of class is the value
                if type(Fraction(values)) is fractions.Fraction:
                    alt["relative_alt"] = round(float(Fraction(values)), 6)
                elif type(values) is str:
                    alt["relative_alt"] = round(float(values), 6)
                return alt
    except Exception as e:
        print(f"ERROR in get_above_ground_level:\n {e}")
        return alt



def get_yaw_pitch_roll(metadata):
    """Extrae giro en el eje Z (yaw), eje Y (pitch) y eje X (roll) de la metadata de una imagen.
    IMPORTANTE: Dependiendo el tipo de dron usado, la metadata puede cambiar de etiquetas, por lo que se pueden
    generar errores de 'keywords más adelante. Se recomienda seguir añadiendo nuevas etiquetas a la 'TAG list'"""
    ypr = {"yaw": None, "pitch": None, "roll": None}
    # TAG LIST: Keep adding tags of each new drone model
    yaw_tags = ["drone-parrot:DroneYawDegree", "@drone-dji:FlightYawDegree"]
    pitch_tags = ["drone-parrot:DronePitchDegree",
                  "@drone-dji:FlightPitchDegree"]
    roll_tags = ["drone-parrot:DroneRollDegree", "@drone-dji:FlightRollDegree"]
    try:
        for key, values in metadata["x:xmpmeta"]["rdf:RDF"]["rdf:Description"].items():
            if key in yaw_tags:
                ypr["yaw"] = float(values)
            if key in pitch_tags:
                ypr["pitch"] = float(values)
            if key in roll_tags:
                ypr["roll"] = float(values)
        return ypr
    except Exception as e:
        print(f"ERROR get_yaw_pitch_roll:\n {e}")
        return {"yaw": None, "pitch": None, "roll": None}



def xmp(imagePath):
    """Extrae metadata en formato xmp"""
    try:
        with Image.open(imagePath) as im:
            for segment, content in im.applist:
                marker, body = content.split(b"\x00", 1)
                if segment == "APP1" and marker == b"http://ns.adobe.com/xap/1.0/":
                    # parse the XML string with any method you like
                    md = xmltodict.parse(body)
                    """ 
                    # Uncomment to print all xmp metadata
                    for key, values in md["x:xmpmeta"]["rdf:RDF"]["rdf:Description"].items():
                        print(key + " " + values)
                     """
                    relative_alt = get_above_ground_level(md)
                    ypr = get_yaw_pitch_roll(md)
                    return {**relative_alt, **ypr}
    except KeyError as e:
        print(f"ERROR in 'xmp' while processing {imagePath} \n{e}")
        return {"relative_alt": None, "yaw": None, "pitch": None, "roll": None}



def get_metadata_from_an_img(imgPath):
    """Función para extraer metadata (longitude, latitude, altitude, altitud relativa width, height, yaw, pitch, roll) 
    de una imagen"""
    file_info = {'img_path': imgPath}
    file_info.update(get_image_coordinates(imgPath))
    file_info.update(get_dimensions(imgPath))
    file_info.update(xmp(imgPath))
    return file_info
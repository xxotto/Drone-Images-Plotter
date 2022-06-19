from math import cos, sin, asin, sqrt, radians
import numpy as np


def calc_distance(lon1, lat1, lon2, lat2):
	"""
	Calculate the great circle distance between two points on the earth (specified in decimal degrees)
	
	:param lon1: longitud coordenada 0
	:param lat1: latitud coordenada 0
	:param lon2: longitud coordenada 1
	:param lat2: latitud coordenada 1
	:return: distancia en metros entre los 2 puntos
	"""
	# convert decimal degrees to radians
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
	# haversine formula
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
	c = 2 * asin(sqrt(a))
	km = 6371 * c
	return km*1000


def coords_to_meters(zero_coordinate, longitude, latitude):
	"""
	Función para transformar coordenadas de longitud y latitud (grados decimales) a metros, referente
	a un punto 0, el cual será el punto con menor longitud y latitud de un dataset. Retorna 2 valores 
	la distancia "x" (long) y "y" (lat) en metros de distancia respecto al punto cero.

	:param img_df: dataframe con la metadata de cada imagen
	:return1: distancia "x" en metros
	:return2: distancia "y" en metros
	"""
	# Projection of points
	x_proyection = (longitude, zero_coordinate[1])
	y_proyection = (zero_coordinate[0], latitude)
	
	# Distance in meters between points
	#		 					longitud_ref		latitude_ref	longitud_mi_punto  latitud_mi_punto
	x_metros = calc_distance(zero_coordinate[0], zero_coordinate[1], x_proyection[0], x_proyection[1])
	y_metros = calc_distance(zero_coordinate[0], zero_coordinate[1], y_proyection[0], y_proyection[1])
	
	return x_metros, y_metros



def from_meters_to_pixels(df, scale = 10):
	"""
	Función para transformar distancias en metros a una escala en pixeles. Modifica el df dado agregando 2 columnas,
	"x_ppm" x pixeles por metro y "y_ppm" y pixeles por metro.

	:param df: dataframe con la metadata de cada imagen
	"""
	actual_width = int(df.width.mode())
	actual_height = int(df.height.mode())

	rescaled_width = int(actual_width/scale)
	rescaled_height = int(actual_height/scale)
	
	# Centimetros por pixel (cm/px)
	x_resolution = 1/0.8723
	y_resolution = 1/0.8769

	# Disminuir escala
	x_ppm = (x_resolution*100)/scale
	y_ppm = (y_resolution*100)/scale

	# ppm = pixel por metro
	df["x_ppm"] = (df["x_mts"]*y_ppm).astype("int")
	df["y_ppm"] = (df["y_mts"]*x_ppm).astype("int")

	max_pixels_size = (int(df.y_ppm.max() + rescaled_width*2.5), int(df.x_ppm.max() + rescaled_height*2.5), 3)
	return max_pixels_size



def move_pixels_to_zero(df):
	
	if (df["x_rot"].values < 0).any():
		print("\t\t - IMPORTANT: Rotation in 'x_rot' has generated negative values. Correcting...")
		min_value = df["x_rot"].min()
		df["x_rot"] = (df["x_rot"] - min_value).astype("int")

	if (df["y_rot"].values < 0).any():
		print("\t\t - IMPORTANT: Rotation in 'y_rot' has generated negative values. Correcting...")
		min_value = df["y_rot"].min()
		df["y_rot"] = (df["y_rot"] - min_value).astype("int")



def rotate(p, origin, degrees):
	"""
	Función para rotar en X grados un array de tuplas con coordenadas.

	:param p: array de tuplas con las coordenadas a rotar
	:param origin: tupla con la coordenada de referencia para rotar
	:param degrees: grados decimales que se van a rotar
	"""
	angle = np.deg2rad(degrees)
	R = np.array([[np.cos(angle), -np.sin(angle)],
				  [np.sin(angle),  np.cos(angle)]])
	o = np.atleast_2d(origin)
	p = np.atleast_2d(p)

	return np.squeeze((R @ (p.T-o.T) + o.T).T)

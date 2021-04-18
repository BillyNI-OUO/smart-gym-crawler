
from src import constants
from src.crawler import query
import numpy as np

def search_nearby2(lat_range=(21.8, 25.44), lng_range=(120, 122)):
	"""
	Search the nearby store by grid between lat_range and ln_range with the interval width
	"""
	width = constants.GRID_WIDTH
	places_info_list = []
	for lat in np.arange(lat_range[0], lat_range[1], width):
		for lng in np.arange(lng_range[0], lng_range[1], width):
			places_info_list.extend(query.nearby2((lat+width/2, lng+width/2), keyword = constants.KEYWORD))
	return places_info_list

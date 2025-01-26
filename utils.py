from math import floor

def fix_pos(num):
	return floor(num * 8 / 26.66)
	
def calc_pos(num):
	return floor(num * 100 / 30)
def level_from_value(value):
	if value < 110:
		return value / 10
	elif value > 5105:
		return 100 + (value - 5105) / 100
	else:
		temp = value - 100
		level = 10
		while (temp > level):
			level += 1
			temp -= level
		return level

def value_from_level(level):
	if (level < 11):
		return level * 10
	elif (level > 100):
		return 5105 + (level - 100) * 100
	else:
		value = 100;
		temp = 10
		while (temp < level):
			temp += 1
			value += temp
		return value

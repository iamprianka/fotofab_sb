

def get_date(data):
	if data is not None:
		return data[0:10]
	else:
		return None

def return_none(data):
	return None

def get_bool(data):
	if data=='true':
		return True

def get_int_value(data):
	if data is not None:
		return int(data)
	else:
		return None
dictionary = dict()
reversed_dict = dict()

with open('lang.cfg', 'r') as file:
	lang = file.read().replace('\n', '').split(';')
	lang.remove('')
	for item in lang:
		dictionary[item.split('=')[1]] = item.split('=')[0]
		reversed_dict[item.split('=')[0]] = item.split('=')[1]


def encrypt(mes):
	message = ''
	mes = mes.lower()
	for ch in mes:
		message += reversed_dict[ch]

	return message

def decrypt(mes):
	mes = mes.decode('utf-8')
	for el in dictionary.keys():
		if el in mes:
			mes = mes.replace(el, dictionary[el])

	return mes

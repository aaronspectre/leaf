import config, requests, json
from time import sleep
from threading import Thread

class Client:
	""" HTTP based server """

	SERVER = 'https://sexypegas.pythonanywhere.com'

	def __init__(self):
		self.ui = None
		self.username = str('stranger')
		self.password = str()


	def update(self):
		while True:
			response = requests.post(self.SERVER+'/update', {'user': self.username})

			if response.text == 'Ignore':
				sleep(1)
				continue

			response = json.loads(response.text)
			if len(response) != 0:
				for message in response:
					self.ui.logMessage(f'Server: {message}', 'blue')
					self.ui.register_message(message)
			sleep(1)

	def send_data(self, route, message = None):
		try:
			self.ui.logMessage(f'Client -> {self.SERVER}{route}', 'dodger blue')
			response = requests.post(self.SERVER+route, message)

			if response.status_code == 200:
				self.ui.logMessage(f'Server -> [{response.status_code}] {response.text[:50]}', 'green')

			else:
				self.ui.logMessage(f'Server -> [{response.status_code}] {response.text[:50]}', 'red')
				return False
		except Exception as e:
			self.ui.logMessage(e, 'red')

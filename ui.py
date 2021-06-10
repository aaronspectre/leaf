from tkinter import *
from tkinter import ttk
from threading import Thread
from server import Client

import config, json



class ChatUI:
	def __init__(self):
		#Server client
		self.client = Client()
		self.client.ui = self

		#UI
		self.master = Tk()
		self.master.title('Leaf')
		# self.master.iconbitmap('icon.ico')
		self.master.minsize(300, 400)
		self.master.resizable(FALSE, FALSE)

		self.menu = Menu(self.master)
		self.menu.add_command(label = 'Log', command = self.menuaction)

		self.settingsmenu = Menu(self.menu, tearoff = 0)
		self.settingsmenu.add_command(label = 'Font', command = self.menuaction)

		self.menu.add_cascade(label = 'Settings', menu = self.settingsmenu)
		self.master.config(menu = self.menu)

		self.mainframe = ttk.Frame(self.master)
		self.mainframe.place(relheight = 1, relwidth = 1)
		self.mainframe.columnconfigure(0, weight = 1)
		self.mainframe.rowconfigure(0, weight = 1)

		self.display = Listbox(self.mainframe, font = 'default 10')
		self.display.grid(column = 0, row = 0, sticky = 'NSEW')

		self.bar = ttk.Scrollbar(self.mainframe, orient = 'vertical', command = self.display.yview)
		self.bar.grid(column = 1, row = 0, sticky = 'NSEW')
		self.display.config(yscrollcommand = self.bar.set)

		self.messageField = ttk.Entry(self.mainframe)
		self.messageField.grid(column = 0, row = 1, columnspan = 2,sticky = 'EW')
		self.messageField.focus()


		#Log window
		self.master.update()

		self.log = Toplevel(self.master)
		self.log.title('Log')
		self.log.minsize(350, 400)
		self.log.geometry(f'+{self.master.winfo_x() + self.master.winfo_width() + 20}+{self.master.winfo_y()}')
		self.log.resizable(TRUE, FALSE)

		self.logdisplay = Listbox(self.log, font = 'default 10')
		self.logdisplay.place(relheight = 1, relwidth = 1)

		# self.log.withdraw()

		#Binding Events
		self.master.bind('<Configure>', self.drag)
		self.log.protocol("WM_DELETE_WINDOW", lambda: self.log.withdraw())
		self.master.protocol("WM_DELETE_WINDOW", self.bye)
		self.messageField.bind('<KeyPress>', self.validate)




	#Fixed Logger window
	def drag(self, event):
		if self.log is not None:
			self.master.update()
			self.log.geometry(f'+{self.master.winfo_x() + self.master.winfo_width() + 20}+{self.master.winfo_y()}')


	#Show logger window
	def menuaction(self):
		self.log.deiconify()

	#Message validation
	def validate(self, event):
		mes = self.messageField.get()
		if event.state == 20 and event.keycode == 22:
			self.messageField.delete(0, END)

		if event.keycode == 36 or event.keycode == 104 or event.keycode == 13:
			if mes == 'clear' or mes == 'cls':
				self.display.delete(0, END)
				self.messageField.delete(0, END)
				return

			elif mes == 'exit':
				self.bye()

			elif 'history' in mes:
				self.client.history()
				self.messageField.delete(0, END)

			elif '-font' in mes:
				mes = int(mes.split('-font')[1])
				self.display.config(font = f'default {mes}')
				self.messageField.delete(0, END)

			else:
				self.sendMessage(mes)


	#Send Message
	def sendMessage(self, mes):
		self.display.insert(0, f'you> {mes}')
		self.display.itemconfig(0, fg = 'green')
		self.messageField.delete(0, END)
		thread = Thread(target = self.client.send_data, daemon = True, args = ('/message', {'message': mes, 'user': self.client.username}))
		thread.start()

	#Receive Message
	def receiveMessage(self, message):
		self.display.insert(0, f'stranger> {message}')
		self.display.itemconfig(0, fg = 'blue')

	#Show recived message
	def register_message(self, message):
		self.display.insert(0, f'stranger> {message}')
		self.display.itemconfig(0, fg = 'blue')


	#Connection to Server
	def connect(self):
		self.logMessage(f'Connecting to {self.client.SERVER}', 'dodger blue')
		response = self.client.send_data(route = '/greet', message = {'pass': self.client.password, 'user': self.client.username})
		if response != False:
			self.logMessage('200 Connection established!', 'dodger blue')
			listen_thread = Thread(target = self.client.update, daemon = True)
			listen_thread.start()
		else:
			self.logMessage('Please restart application', 'red')

	#Disconnect from Server
	def bye(self):
		self.logMessage('Closing connection...', 'dodger blue')
		self.client.send_data('/bye', {'user': self.client.username})
		self.master.destroy()


	#Logger
	def logMessage(self, message, color = 'black'):
		self.logdisplay.insert(END, message)
		self.logdisplay.itemconfig(END, fg = color)





class Authentication:
	def __init__(self):
		self.window = Tk()
		self.window.title('Authentication')
		# self.window.iconbitmap('icon.ico')
		self.window.minsize(100, 50)
		self.window.resizable(FALSE, FALSE)

		self.authLabel = Label(self.window, text = 'Authentication', pady = 10)
		self.authLabel.grid(column = 0, row = 0, sticky = 'EW', columnspan = 2)

		self.loginLabel = Label(self.window, text = 'Login', pady = 5, padx = 10)
		self.loginLabel.grid(column = 0, row = 1, sticky = 'EW')
		self.loginField = ttk.Entry(self.window, width = 30)
		self.loginField.focus()
		self.loginField.grid(column = 1, row = 1, sticky = 'EW')
		self.passLabel = Label(self.window, text = 'Password', pady = 5, padx = 10)
		self.passLabel.grid(column = 0, row = 2, sticky = 'EW')
		self.passField = ttk.Entry(self.window, width = 30, show = '*')
		self.passField.grid(column = 1, row = 2, sticky = 'EW')
		self.loginButton = ttk.Button(self.window, text = 'Send', command = lambda: self.authenticate())
		self.loginButton.grid(column = 0, row = 3, columnspan = 2, sticky = 'EW')

		self.loginField.bind('<KeyPress>', self.detectKey)
		self.passField.bind('<KeyPress>', self.detectKey)

		self.window.mainloop()


	def detectKey(self, event):
		if event.keycode == 36 or event.keycode == 104 or event.keycode == 13:
			self.authenticate()

	def authenticate(self):
		username = self.loginField.get()
		password = self.passField.get()

		self.window.destroy()

		ui = ChatUI()

		ui.client.username = username
		ui.client.password = password

		connetion_thread = Thread(target = ui.connect, daemon = True)
		connetion_thread.start()

		ui.master.mainloop()
		



auth = Authentication()
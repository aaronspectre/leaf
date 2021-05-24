from tkinter import *
from tkinter import ttk
from threading import Thread
from server import Client

import config



class ChatUI:
	def __init__(self):
		#Server client
		self.client = Client(port = 7777, fport = 8989)
		self.client.ui = self

		#UI
		self.master = Tk()
		self.master.title('Leaf')
		self.master.iconbitmap('icon.ico')
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
		self.log.minsize(300, 400)
		self.log.geometry(f'+{self.master.winfo_x() + self.master.winfo_width() + 20}+{self.master.winfo_y()}')
		self.log.resizable(TRUE, FALSE)

		self.logdisplay = Listbox(self.log, font = 'default 10')
		self.logdisplay.place(relheight = 1, relwidth = 1)

		self.logMessage(f'Lisntening on {self.client.host}:{self.client.port}', 'orange')

		#Binding Events
		self.log.protocol("WM_DELETE_WINDOW", lambda: self.log.withdraw())
		self.messageField.bind('<KeyPress>', self.validate)
		self.master.bind('<Configure>', self.drag)


	def drag(self, event):
		if self.log is not None:
			self.master.update()
			self.log.geometry(f'+{self.master.winfo_x() + self.master.winfo_width() + 20}+{self.master.winfo_y()}')

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
				close = True
				exit()

			elif '-port' in mes:
				mes = int(mes.split('-port')[1])
				self.client.port = mes
				self.sendMessage(f'Port changed to {mes}')

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
		# mes = config.encrypt(mes)
		self.client.send_data(mes.encode('utf-8'))


	def receiveMessage(self, message):
		self.display.insert(0, f'stranger> {message}')
		self.display.itemconfig(0, fg = 'blue')


	def logMessage(self, message, color = 'black'):
		self.logdisplay.insert(END, message)
		self.logdisplay.itemconfig(END, fg = color)


ui = ChatUI()

listen_thread = Thread(target = ui.client.listen_data, daemon = True)
listen_thread.start()

ui.master.mainloop()
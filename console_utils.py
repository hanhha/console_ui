from threading import Thread, Lock, Event 
from curses    import doupdate
from wingen import WinGen

import curses

class ConsoleScreen(object):
	def __init__ (self):
		self.screen = None
		self.clsLock = Lock ()
		self._execThread = None
		self._Stop = Event ()
		self.enabled = False

	def __del__ (self):
		if self.screen is not None:
			self.end ()

	def start (self):
		self.screen = curses.initscr ()
		curses.noecho ()
		curses.cbreak ()
		self.screen.keypad (True)
		self.screen.scrollok (True)
		self._Stop.clear ()

	def end (self):
		if self.enabled:
			self._Stop.set ()
			self.enabled = False
			if self._execThread is not None:
				self._execThread.join ()

		self.screen.keypad (False)
		curses.nocbreak ()
		curses.echo ()
		curses.endwin ()

class AWindow(object):
	def __init__(self, h, w, y, x, initial_content = None, bkgd = None, archive_limit = 20, **kwargs):
		self._archive_limit = archive_limit
		self._archive       = []
		self._bkgd          = bkgd

		self.create (h, w, y, x, bkgd)

		if initial_content is not None:
			self.addstr (initial_content)

	def create (self, h, w, y, x, bkgd):
		self._win = curses.newwin (h, w, y, x)

		self._win.scrollok (True)
		self._win.clear ()
		self._win.idlok (True)

		self.refresh ()

		if bkgd is not None:
			self.win.bkgd(bkgd)

		self.refresh ()

	@property
	def win (self):
		return self._win

	def clrtoeol (self):
		self._win.clrtoeol ()

	def addstr (self, *args):
		self._win.addstr (*args)
		self.refresh ()
		self._archive.append (args)
		if len(self._archive) > self._archive_limit:
			del self._archive [0]

	def restore (self):
		for archive in self._archive:
			self._win.addstr (*archive)
			self.refresh ()

		self.refresh ()

	def refresh (self):
		self._win.noutrefresh ()

	def resize (self, h, w, y, x):
		self.create (h, w, y, x, self._bkgd)
		self.restore ()

class ABoxWindow(AWindow):
	def __init__(self, h, w, y, x, title = None, initial_content = None, bkgd = None, archive_limit = 20, **kwargs):
		self._title = title

		self.createBox (h, w, y, x, title = title)

		AWindow.__init__ (self, h-2, w-2, y+1, x+1, initial_content = initial_content, bkgd = bkgd, archive_limit = archive_limit, **kwargs)

	def createBox (self, h, w, y, x, title = None):		
		self._WinBox = curses.newwin (h, w, y, x)
		self._WinBox.box ()
		if title is not None:
			self._WinBox.addstr (0, 2, '[' + title + ']')
		self._WinBox.noutrefresh ()

	def resize (self, h, w, y, x):
		self.createBox (h, w, y, x, title = self._title)
		AWindow.resize (self, h - 2, w - 2, y + 1, x + 1)

class SimpleWinMan(ConsoleScreen, WinGen):
	def __init__ (self, layout_root, win_attr, **kwargs):
		self.maxX    = None 
		self.maxY    = None 
		self.verbose = kwargs ['verbose'] if 'verbose' in kwargs else 2

		ConsoleScreen.__init__ (self)
		WinGen.__init__ (self, layout_root)

		self.windows = dict ()
		self.win_attr = win_attr

		self.out_of_service = True

	def start (self):
		ConsoleScreen.start (self)

		self.maxY, self.maxX = self.screen.getmaxyx ()

		self.cook ()
		self.run ()

	def run (self):
		def worker ():
			while (not self._Stop.is_set()):
				resized = curses.is_term_resized(self.maxY, self.maxX)
				if resized:
					self.update_dims (True)

				if self.clsLock.acquire (False):
					doupdate ()
					self.clsLock.release ()

				self._Stop.wait (0.1)

		self._execThread = Thread (name = "curses_ui", target = worker)
		self._execThread.start ()

		self.enabled = True

	def prepare_color (self):
		curses.start_color ()
		curses.init_pair (1, curses.COLOR_GREEN , curses.COLOR_BLACK)
		curses.init_pair (2, curses.COLOR_RED   , curses.COLOR_BLACK)
		curses.init_pair (3, curses.COLOR_WHITE , curses.COLOR_BLACK)

		self.screen.noutrefresh ()

	def update_dims (self, resize = True):
		self.clsLock.acquire ()
		self.generate (resize)
		self.clsLock.release ()

	def cook (self, resize = False):
		self.clsLock.acquire ()
		self.prepare_color ()
		self.generate (False)
		self.clsLock.release ()

	def generate (self, resize):
		try:
			self.maxY, self.maxX = self.screen.getmaxyx ()
			WinGen.update (self, self.maxX, self.maxY)
			self.out_of_service = False
		except ValueError:
			self.out_of_service = True
			self.screen.clear ()
			self.screen.addstr (0,0, "Screen is too small to show in colorful mode!", curses.color_pair(3))
			self.screen.noutrefresh ()
		
		if not self.out_of_service:
			self.screen.clear ()
			self.screen.noutrefresh ()

			for win in self.winpool.keys ():
				self.showWin (win, resize)

	@staticmethod
	def createWindow (h, w, y, x, title = None, refWin = None, initial_content = None, bkgd = None):
		if refWin is None:
			Win = ABoxWindow (h, w, y, x, title = title, initial_content = initial_content, bkgd = bkgd)
		else:
			Win = refWin
			Win.resize (h, w, y, x)

		return Win 

	def showWin (self, k, resize = False):
		if k not in self.windows or resize:
			y, x, h, w = self.winpool[k].getWin ()
			title = self.win_attr [k]['title'] if 'title' in self.win_attr[k] else None
			text  = self.win_attr [k]['text'] if 'text' in self.win_attr[k] else None

			self.windows [k] = self.createWindow (h, w, y, x, title, refWin = self.windows[k] if (k in self.windows) and resize else None, bkgd = curses.color_pair (3), initial_content = text)

	def print_on_screen (self, *args, **kwargs):
		if (('verbose' in kwargs) and (self.verbose >=  kwargs['verbose'])) or ('verbose' not in kwargs):
			for arg in args:
				if type(arg) is str:
					if self.screen is None:
						print (arg)
					else:
						self.screen.addstr (arg)
						self.screen.noutrefresh ()
					break

	def println_on_window (self, wk, *args, **kwargs):
		self.clsLock.acquire ()
		if not self.out_of_service:
			self.windows[wk].addstr (*args)
			self.windows[wk].clrtoeol ()
		else:
			self.print_on_screen (*args, **kwargs)
		self.clsLock.release ()

	def print_on_window (self, wk, *args, **kwargs):
		self.clsLock.acquire ()
		if not self.out_of_service:
			self.windows[wk].addstr (*args)
		else:
			self.print_on_screen (*args, **kwargs)
		self.clsLock.release ()
	
	@staticmethod
	def MsgBox (title = None, info = '...', confirm = False):
		pass	

	def getch (self, block = True):
		self.screen.nodelay (not block)
		return self.screen.getch ()

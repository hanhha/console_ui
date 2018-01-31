class Window(object):
	def __init__ (self):
		self.type = 'win'
		self._w = 0
		self._h = 0
		self._x = 0
		self._y = 0

	@property
	def x (self):
		return self._x

	@x.setter
	def x (self, value):
		self._x = value

	@property
	def y (self):
		return self._y

	@y.setter
	def y (self, value):
		self._y = value

	@property
	def w (self):
		return self._w

	@w.setter
	def w (self, value):
		self._w = value

	@property
	def h (self):
		return self._h

	@h.setter
	def h (self, value):
		self._h = value

	def update (self, w, h):
		self.w, self.h = w, h

	def getWin (self):
		return self.y, self.x, self.h, self.w

class FloatingWindow(Window):
	def __init__ (self):
		Window.__init__ (self)
		self.type = 'fwin'

class Layout(FloatingWindow):
	def __init__ (self, pool):
		FloatingWindow.__init__ (self)
		self.type = 'lay'

		self._tree      = list ()
		self._pool      = pool

		self._n_layouts    = 0
		self._fixed_l      = 0
		self.remaining     = 0
		self.remaining_lay = 0

	def distribute (self):
		if self.remaining <= 0:
			raise ValueError ("Not enough room: {type} : {n} : {f} : {h} : {w}".format (n = self._n_layouts, f = self._fixed_l, type = self.type, h = self.h, w = self.w))
		else:
			for idx, o in enumerate (self._tree):
				self.update_child (self._tree[idx-1] if idx > 0 else None, o)		
				if o.type == 'vlay' or o.type == 'hlay':
					o.distribute ()

	def create (self, tree_dict):
		for k, v in tree_dict.items():
			if k == "HLayout" or k == "VLayout":
				lay = None
				if k == "HLayout":
					lay = HLayout (self._pool)
				else:
					lay = VLayout (self._pool)

				self._tree.append(lay)
				self._n_layouts += 1
				self._tree [-1].create (v)
			else:
				win = FloatingWindow () if v[0] == v[1] == 0 else Window ()
				win.w, win.h = v
				self._pool [k] = win
				self._tree.append(win)
				self._fixed_l += self.get_var_dim (win)
				self._n_layouts += 1 if v[0] == v[1] == 0 else 0

	def update (self, w, h):
		FloatingWindow.update (self, w, h)
		self.remaining_lay = self._n_layouts
		self.remaining = self.get_var_dim(self) - self._fixed_l

	def update_child (self, pre_child_win, child_win):
		assert "Need to implement", 0

	def get_var_dim(self, win):
		assert "Need to implement", 0

class HLayout(Layout):
	def __init__ (self, pool):
		Layout.__init__ (self, pool)
		self.type = 'hlay'

	def get_var_dim(self, win):
		return win.w

	def update_child (self, pre_child_win, child_win):
		ch = self.h
		cy = self.y 

		cx = self.x if pre_child_win is None else pre_child_win.x + pre_child_win.w
		cw = child_win.w if child_win.type == 'win' else self.remaining // self.remaining_lay

		self.remaining -= cw if child_win.type != 'win' else 0
		self.remaining_lay -= 1 if child_win.type != 'win' else 0

		child_win.update (cw, ch)
		child_win.x, child_win.y = cx, cy

class VLayout(Layout):
	def __init__ (self, pool):
		Layout.__init__ (self, pool)
		self.type = 'vlay'

	def get_var_dim (self, win):
		return win.h

	def update_child (self, pre_child_win, child_win):
		cw = self.w
		cx = self.x 

		cy = self.y if pre_child_win is None else pre_child_win.y + pre_child_win.h
		ch = child_win.h if child_win.type == 'win' else self.remaining // self.remaining_lay

		self.remaining -= ch if child_win.type != 'win' else 0
		self.remaining_lay -= 1 if child_win.type != 'win' else 0

		child_win.update (cw, ch)
		child_win.x, child_win.y = cx, cy

class WinGen(object):
	def __init__ (self, layout_root):
		self.winpool = dict ()

		if 'HLayout' in layout_root:
			self.layout = HLayout (self.winpool)
			self.layout.create (layout_root ['HLayout'])
		elif 'VLayout' in layout_root:
			self.layout = VLayout (self.winpool)
			self.layout.create (layout_root ['VLayout'])

	def update (self, newW, newH):
		self.layout.update (newW, newH)
		self.layout.distribute ()

if __name__ == '__main__':   
	from collections import OrderedDict

	ui_sheet = {
		'VLayout': {
			'title'  : (0, 4),
			'tips'   : (0, 6),
			'HLayout': {
				'VLayout'   : {
					'activities': (0, 0),
					'summary'   : (0, 7),
				},
				'current': (0, 0),
			}
		}
	}
	ui_sheet = OrderedDict (ui_sheet)

	wg = WinGen (ui_sheet)
	wg.update (100, 40)
	for k, v in wg.winpool.items ():
		print ("Win {l} : {v}".format (l = k, v = v.getWin()))

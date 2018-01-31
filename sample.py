from curses import wrapper
from collections import OrderedDict
import console_utils as cls

ui_sheet = OrderedDict({
	'VLayout': {
		'title'  : (0, 4),
		'tips'   : (0, 6),
		'HLayout': {
			'VLayout'   : {
				'activities': (0, 0),
				'summary'   : (0, 7)
			},
			'current': (0, 0)
		}
	}
})

ui_win = {
	'tips': {'title':'Tips'},
	'title': {'text': 'Auto System'},
	'activities': {'title': 'Actitivites'},
	'summary': {'title': 'Summary'},
	'current': {'title': 'Latest data'},
}

UI = cls.SimpleWinMan (ui_sheet, ui_win)

def main (stdscr):
	UI.start ()
	UI.getch (True) # Wait for any keypress
	UI.end ()

if __name__ == '__main__':
	wrapper (main)
	exit (0)


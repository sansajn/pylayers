''' vykresly mapu '''
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import cairo, math, os.path
import shapely.geometry

MAX_MAP_LEVEL = 6

class Example(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self)
		self._level = 0
		self._darea = None
		self._window_w = 0
		self._window_h = 0
		self._origin = (0, 0)
		self._mouse_pos = (0, 0)
		# tile_size
		# map_width

		self.init_ui()

	def init_ui(self):
		self.set_events(Gdk.EventMask.KEY_PRESS_MASK)
		self.connect('key-press-event', self.on_key_press)
		
		darea = Gtk.DrawingArea()
		darea.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
		darea.set_events(Gdk.EventMask.POINTER_MOTION_MASK)
		darea.connect('draw', self.on_draw)
		darea.connect('button-press-event', self.on_button_press)
		darea.connect('size-allocate', self.on_size_allocate)
		darea.connect('motion-notify-event', self.on_motion_notify)
		self.add(darea)
		self._darea = darea

		self._set_title()
		self.resize(800, 600)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.connect('delete-event', Gtk.main_quit)
		self.show_all()

	def on_draw(self, widget, cr):
		map_size = self.map_size()
		filtered_count = 0

		cr.translate(self._origin[0], self._origin[1])
		for x in range(0, 2**self._level):
			for y in range(0, 2**self._level):
				# TODO: we can't iterate all images
				if not self._can_see(self._level, x, y):
					filtered_count += 1
					continue

				image_path = 'tiles/%d/%d/%d.png' % (self._level, x, y)
				if not os.path.exists(image_path):
					print("tile '%s' doesn't exists" % (image_path, ))

				self._draw_tile(cr, image_path, x*256, y*256)

		print(self._origin)
		print('%g%% filtered tiles' % (float(filtered_count)/((2**self._level)**2)*100, ))

	def _draw_tile(self, cr, tile_path, x, y):
		img = cairo.ImageSurface.create_from_png(tile_path)
		cr.set_source_surface(img, x, y)
		cr.paint()

	def on_button_press(self, widget, event):
		''' widget:Gtk.Widget, event:Gdk.ButtonEvent '''
		if event.type == Gdk.EventType.BUTTON_PRESS:
			if event.button == 1:  # left mouse button:
				pass
			elif event.button == 3:  # right mouse button
				pass

	def on_motion_notify(self, widget, event):
		''' widget:Gdk.Widget, event:Gdk.EventMotion '''
		if event.state & Gdk.ModifierType.MOD1_MASK:  # alt
			move_vec = (event.x - self._mouse_pos[0], event.y - self._mouse_pos[1])
			self._origin = (self._origin[0] + move_vec[0], self._origin[1] + move_vec[1])
			self.queue_map_draw()

		self._mouse_pos = (event.x, event.y)


	def on_key_press(self, widget, event):
		'''widget:Gdk.Widget, event:Gdk.EventKey'''
		if event.type == Gdk.EventType.KEY_PRESS:
			level_changed = False
			if event.string == '0':
				self.zoom_in()
				level_changed = True
			elif event.string == '9':
				self.zoom_out()
				level_changed = True

			if level_changed:
				self._set_title()

			print('key %d pressed -> %s' % (event.keyval, event.string))

	def on_size_allocate(self, widget, allocation):
		''' widget:Gdk.Widget, allocation:Gdk.Rectangle '''
		self._window_w, self._window_h = (allocation.width, allocation.height)

	def zoom_in(self):
		self._level = min(self._level+1, MAX_MAP_LEVEL)
		self.queue_map_draw()

	def zoom_out(self):
		self._level = max(self._level-1, 0)
		self.queue_map_draw()

	def queue_map_draw(self):
		self._darea.queue_draw()

	def map_size(self):
		return 2**self._level*256

	def _set_title(self):
		self.set_title('simple map render, level:%d' % (self._level, ))

	def _can_see(self, level, x, y):
		xoff, yoff = self._origin
		w, h = (self._window_w, self._window_h)
		view_rect = shapely.geometry.Polygon([
			(-xoff, h-yoff),
			(w-xoff, h-yoff),
			(w-xoff, -yoff),
			(-xoff, -yoff),
			(-xoff, h-yoff)
		])

		tile_rect = shapely.geometry.Polygon([
			(x*256, y*256+256),
			(x*256+256, y*256+256),
			(x*256+256, y*256),
			(x*256, y*256),
			(x*256, y*256+256)
		])

		'''
		if x == 0:
			print('x:%d,y:%d' % (x, y))
			print('origin:', str(self._origin))
			print('view_rect:', str(view_rect))
			print('tile_rect:', str(tile_rect))
			print(view_rect.intersects(tile_rect))
		'''

		return view_rect.intersects(tile_rect)  # TODO: rectangle class will be much more effective
		#return True

def main():
	app = Example()
	Gtk.main()

if __name__ == '__main__':
	main()

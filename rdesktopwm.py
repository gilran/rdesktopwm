import gtk
import gtk.glade
import os
import os.path
import sys
import gobject
import signal
import exceptions

class MainWindow:
	def __init__(self):
		"""
		Doc-string
		"""
		self.xml = gtk.glade.XML("rdesktopwm.glade")
		
		self.list_machines = self.xml.get_widget("listMachines")				

		self.list_store = gtk.ListStore(str, str)
		self.displays = self.xml.get_widget("ntbkDisplays")

		self.xml.get_widget("winMain").show_all()
		self.xml.get_widget("textview1").set_name("tab1")

		self.machines = []
		self.child_widgets = {}

		signal.signal(signal.SIGCHLD, self.reap_child)

		self.buildList()
		
		self.list_machines.connect("row-activated", self.connectToMachine)
		self.xml.get_widget("winMain").connect("destroy", gtk.main_quit)
		self.xml.get_widget("btnRemove").connect("clicked", self.removeMachine)

	def addMachine(self, name, description):
		self.machines.append((name, description))
		self.list_store.append([name, description])
	
	def dropNotebookPage(self, inner_widget):
		for i in range(self.displays.get_n_pages()):
			if self.displays.get_nth_page(i) == inner_widget:
				self.displays.remove_page(i)
				return
		raise exceptions.Exception("Could find page with widget %s" % inner_widget)
		

	def createNewPage(self, treeView, path):
		inner_widget = gtk.TextView()
		self.displays.append_page(inner_widget, gtk.Label(self.machines[path[0]][0]))
		self.displays.show_all()
		self.displays.next_page()
		return inner_widget
	
	def reap_child(self, signum, frame):
		dead_pid, dead_status = os.wait()
		gobject.idle_add(self.dropNotebookPage, self.child_widgets[dead_pid])
		
	def runRdesktop(self, inner_widget, machine):
		child_pid = os.fork()

		if (child_pid != 0):
			self.child_widgets[child_pid] = inner_widget
		else:
			os.execvp("rdesktop", ["rdesktop", "-X", str(inner_widget.window.xid), "-g", "1280x1024", machine])

	def connectToMachine(self, treeView, path, view_column):
		gobject.idle_add(self.runRdesktop, self.createNewPage(treeView, path), self.machines[path[0]][0])

	def buildList(self):
		first_column = gtk.TreeViewColumn("Name")
		second_column = gtk.TreeViewColumn("Description")

		first_renderer = gtk.CellRendererText()
		second_renderer = gtk.CellRendererText()

		first_column.pack_start(first_renderer)
		second_column.pack_start(second_renderer)

		first_column.set_attributes(first_renderer, text=0)
		second_column.set_attributes(second_renderer, text=1)

		self.xml.get_widget("listMachines").append_column(first_column)
		self.xml.get_widget("listMachines").append_column(second_column)

		self.xml.get_widget("listMachines").set_model(self.list_store)

		for line in open(os.path.join(os.path.dirname(sys.argv[0]), "machines.conf")):
			self.addMachine(line.split(" ")[0], " ".join(line.split(" ")[1:]).rstrip())
	
	def removeMachine(self, btn):
		if self.list_machines.get_cursor()[0]:
			self.list_store.remove(self.list_store.get_iter(self.list_machines.get_cursor()[0][0]))

if __name__ == '__main__':
	m = MainWindow()
	gtk.main()

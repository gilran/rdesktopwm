import gtk
import gtk.glade
import os.path
import sys

class MainWindow:
	def __init__(self):
		"""
		Doc-string
		"""
		self.xml = gtk.glade.XML("rdesktopwm.glade")
		
		self.list_machines = self.xml.get_widget("listMachines")				

		self.list_store = gtk.ListStore(str, str)

		self.xml.get_widget("winMain").show_all()

		self.machines = []
		
		self.buildList()
		
		self.list_machines.connect("row-activated", self.connectToMachine)
		self.xml.get_widget("winMain").connect("destroy", gtk.main_quit)
		self.xml.get_widget("btnRemove").connect("clicked", self.removeMachine)

	def addMachine(self, name, description):
		self.machines.append((name, description))
		self.list_store.append([name, description])

	def connectToMachine(self, treeView, path, view_column):
		os.system("rdesktop -g 1280x1024 %s" % self.machines[path[0]][0])

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

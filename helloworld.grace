import gtk

def window = gtk.window(gtk.GTK_WINDOW_TOPLEVEL)
window.title := "Hi!"

def button = gtk.button
button.label := "Hello, world!"

button.connect("clicked", { gtk.main_quit })
window.add(button)
window.connect("destroy", { gtk.main_quit })

window.show_all

gtk.main

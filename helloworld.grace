import gtk

def window = gtk.window(gtk.GTK_WINDOW_TOPLEVEL)
window.set_title "Hi!"

def button = gtk.button
button.set_label "Hello, world!"

button.connect("clicked", { gtk.main_quit })
window.add(button)

window.show_all

gtk.main

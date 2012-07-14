def gtk = platform.gtk

def window = gtk.window(gtk.GTK_WINDOW_TOPLEVEL)
window.title := "Hi!"

def button = gtk.button
button.label := "Hello, world!"

button.on "clicked" do { gtk.main_quit }
window.add(button)
window.on "destroy" do { gtk.main_quit }

window.show_all

gtk.main

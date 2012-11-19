import "gtk" as gtk

var hbox
if (gtk.GTK_MAJOR_VERSION == 3) then {
    hbox := gtk.box(gtk.GTK_ORIENTATION_HORIZONTAL, 0)
} else {
    hbox := gtk.hbox(false, 0)
}

def window = gtk.window(gtk.GTK_WINDOW_TOPLEVEL)
window.title := "Enter your name"

def entry = gtk.entry
def button = gtk.button
button.label := "Print"
entry.text := ""

entry.connect("activate", {
    print "Hi, {entry.text}!"
    gtk.main_quit
})
button.on "clicked" do {
    print "Hello, {entry.text}!"
}
hbox.add(entry)
hbox.add(button)

window.add(hbox)

window.connect("destroy", { gtk.main_quit })

window.show_all

gtk.main

// GTK+ 3 drawing example (not compatible with GTK+ 2)
def gtk = platform.gtk

if (gtk.GTK_MAJOR_VERSION != 3) then {
    print "Error: This example is only compatible with GTK+ 3."
    print "drawing2.grace is the GTK+ 2 version of the drawing sample."
    platform.sys.exit(1)
}

def window = gtk.window(gtk.GTK_WINDOW_TOPLEVEL)
window.title := "Hi!"

window.set_default_size(400, 300)
def button = gtk.button
button.label := "Cycle"

def vbox = gtk.box(gtk.GTK_ORIENTATION_VERTICAL, 6)

def da = gtk.drawing_area
da.set_size_request(400, 300)
vbox.add(da)
vbox.add(button)
window.add(vbox)
window.on "destroy" do { gtk.main_quit }

da.app_paintable := true

def colours = [
    [0, 1, 0],
    [0, 0, 0.5],
    [0, 0, 0]
]
button.on "clicked" do {
    def tmp = colours[1]
    colours[1] := colours[2]
    colours[2] := colours[3]
    colours[3] := tmp
    da.queue_draw
}

da.on "draw" do { c->
    c.set_source_rgb(colours[1][1], colours[1][2], colours[1][3])
    c.rectangle(10, 10, 100, 100)
    c.fill
    c.set_source_rgb(colours[2][1], colours[2][2], colours[2][3])
    c.rectangle(60, 60, 100, 100)
    c.fill
    c.set_source_rgb(colours[3][1], colours[3][2], colours[3][3])
    c.rectangle(100, 100, 100, 100)
    c.fill
}

window.show_all

gtk.main

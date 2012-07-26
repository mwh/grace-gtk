// GTK+ 2 drawing example (not compatible with GTK+ 3)
def gtk = platform.gtk
def gdk = platform.gdk

if (gtk.GTK_MAJOR_VERSION != 2) then {
    print "Error: This example is only compatible with GTK+ 2."
    print "drawing.grace is the GTK+ 3 version of the drawing sample."
    platform.sys.exit(1)
}

def window = gtk.window(gtk.GTK_WINDOW_TOPLEVEL)
window.title := "Simple drawing demo"

def button = gtk.button
button.label := "Cycle"

def vbox = gtk.vbox(true, 6)

def da = gtk.drawing_area
da.set_size_request(400, 300)
vbox.add(da)
vbox.add(button)
window.add(vbox)
window.add_events(platform.gdk.GDK_BUTTON_PRESS_MASK)
window.add_events(platform.gdk.GDK_BUTTON1_MOTION_MASK)
window.on "destroy" do { gtk.main_quit }

da.app_paintable := true

// Helper to simplify the code below
method rectangleAt(x', y')sized(w', h')coloured(r', g', b') {
    object {
        def x is public, readable = x'
        def y is public, readable = y'
        def w is public, readable = w'
        def h is public, readable = h'
        def r is public, readable = r'
        def g is public, readable = g'
        def b is public, readable = b'
    }
}
def rectangles = [rectangleAt(20, 20)sized(50, 50)coloured(1, 0, 0)]

var curR := 1
var curG := 0
var curB := 0
button.on "clicked" do {
    def tmp = curR
    curR := curB
    curB := curG
    curG := tmp
}

da.on "expose-event" do {
    def c = gdk.cairo(da.window)
    for (rectangles) do {rect->
        c.set_source_rgb(rect.r, rect.g, rect.b)
        c.rectangle(rect.x, rect.y, rect.w, rect.h)
        c.fill
    }
}

window.on "motion-notify-event" do {e->
    rectangles.push(rectangleAt(e.x, e.y)sized(10, 10)coloured(curR, curG, curB))
    da.queue_draw
}

window.show_all

gtk.main

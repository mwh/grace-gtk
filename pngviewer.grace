import "gtk" as gtk
import "gdk" as gdk
import "cairo" as cairo
import "sys" as sys
import "io" as io

var filename := "test.png"
var index := 2
if (sys.argv.size > 1) then {
    filename := sys.argv.at(2)
}
if (!io.exists(filename)) then {
    io.error.write("{sys.argv[1]}: Error: no such file '{filename}'. Use "
        ++ "`{sys.argv[1]} FILENAME`.\n")
    sys.exit(1)
}

def window = gtk.window(gtk.GTK_WINDOW_TOPLEVEL)
window.title := "Image viewer"

window.add_events(gdk.GDK_BUTTON_PRESS_MASK)
window.add_events(gdk.GDK_BUTTON1_MOTION_MASK)
window.resizable := false

def da = gtk.drawing_area
window.add(da)
window.on "destroy" do { gtk.main_quit }
def accelgroup = gtk.accel_group
accelgroup.accel_connect(gdk.GDK_KEY_Escape, { gtk.main_quit })
window.add_accel_group(accelgroup)

da.app_paintable := true

var surface
var scale := 1
def maxHeight = gdk.screen_get_default.height * 0.9
def maxWidth = gdk.screen_get_default.width * 0.9
method setUpImage {
    surface := cairo.image_surface_create_from_png(filename)
    if ((surface.width * surface.height) == 0) then {
        io.error.write("{sys.argv[1]}: Error: '{filename}' is not a PNG image.\n")
        sys.exit(1)
    }
    var width := surface.width
    var height := surface.height
    scale := 1
    if (width > maxWidth) then {
        scale := maxWidth / width
        height := height * scale
        width := maxWidth
    }
    if (height > maxHeight) then {
        scale := maxHeight / surface.height
        width := surface.width * scale
        height := maxHeight
    }
    da.set_size_request(width, height)
    window.title := "Image viewer - {filename} ({surface.width}x{surface.height}: {(scale*100).truncate}%) - {index - 1}/{sys.argv.size-1}"
    def fn = filename
    da.queue_draw
}
setUpImage
if (gtk.GTK_MAJOR_VERSION == 3) then {
    // For GTK 3, use "draw"
    da.on "draw" do { c ->
        c.scale(scale, scale)
        c.set_source_surface(surface, 0, 0)
        c.paint
    }
} else {
    // For GTK 2, use "expose-event" and make your own Cairo context
    da.on "expose-event" do {
        def c = gdk.cairo(da.window)
        c.scale(scale, scale)
        c.set_source_surface(surface, 0, 0)
        c.paint
    }
}
accelgroup.accel_connect(gdk.GDK_KEY_space, {
    index := index + 1
    if (index > sys.argv.size) then {
        index := 2
    }
    filename := sys.argv.at(index)
    setUpImage
})
accelgroup.accel_connect(gdk.GDK_KEY_BackSpace, {
    index := index - 1
    if (index < 2) then {
        index := sys.argv.size
    }
    filename := sys.argv.at(index)
    setUpImage
})


window.show_all

gtk.main


import "gtk" as gtk
import "gdk" as gdk
import "sys" as sys
import "mgcollections" as collections
import "trigonometry" as trig

class colour.r(r')g(g')b(b') {
    def r is readable = r'
    def g is readable = g'
    def b is readable = b'
}
def black = colour.r 0 g 0 b 0
def blue = colour.r 0 g 0 b 1
def green = colour.r 0 g 1 b 0
def red = colour.r 1 g 0 b 0

var x
var y
var started := false
var maxActionsDrawn := -1

def actions = collections.list.new
var da
var turtleAngle := 0

def PI = 3.14159
method modifyXY(dist, angle) {
    def y' = trig.cos(angle / 180 * PI) * dist
    def x' = trig.sin(angle / 180 * PI) * dist
    y := y - y'
    x := x + x'
}

method drawTurtle(c, angle) {
    def triangleSize = 30
    c.set_source_rgb(0, 0.5, 0)
    c.line_width := 3
    c.move_to(x, y)
    c.line_to(x - trig.cos((angle - 60) / 180 * PI) * triangleSize,
              y - trig.sin((angle - 60) / 180 * PI) * triangleSize)
    c.line_to(x + trig.cos((angle + 60) / 180 * PI) * triangleSize,
              y + trig.sin((angle + 60) / 180 * PI) * triangleSize)
    c.line_to(x, y)
    c.fill
}
method move(dist, angle, lineCol, lineWidth) {
    actions.push {c->
        c.set_source_rgb(lineCol.r, lineCol.g, lineCol.b)
        c.line_width := lineWidth
        c.move_to(x, y)
        modifyXY(dist, angle)
        c.line_to(x, y)
        c.stroke
        turtleAngle := angle
    }
}

method start {
    if (started) then {
        return true
    }
    started := true
    if (gtk.GTK_MAJOR_VERSION != 2) then {
        print "Error: This example is only compatible with GTK+ 2."
        sys.exit(1)
    }

    def window = gtk.window(gtk.GTK_WINDOW_TOPLEVEL)
    window.title := "Turtle"

    //window.set_default_size(400, 300)

    def vbox = gtk.vbox(false, 6)
    da := gtk.drawing_area
    da.set_size_request(400, 300)
    x := 100
    y := 250
    vbox.add(da)
    def but = gtk.button
    but.label := "Step"
    vbox.add(but)
    window.add(vbox)
    window.on "destroy" do { gtk.main_quit }
    def accelgroup = gtk.accel_group
    accelgroup.accel_connect(gdk.GDK_KEY_Escape, { gtk.main_quit })
    window.add_accel_group(accelgroup)

    da.app_paintable := true

    da.on "expose-event" do {
        def c = gdk.cairo(da.window)
        var i := 0
        for (actions) do {a->
            if ((maxActionsDrawn < 0) || (i < maxActionsDrawn)) then {
                a.apply(c)
            }
            i := i + 1
        }
        drawTurtle(c, turtleAngle)
    }

    window.on "motion-notify-event" do {e->
        da.queue_draw
    }

    but.on "clicked" do {
        x := 100
        y := 250
        turtleAngle := 0
        maxActionsDrawn := maxActionsDrawn + 1
        da.queue_draw
    }



    window.show_all

    gtk.main
}

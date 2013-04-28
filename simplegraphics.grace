import "gtk" as gtk
import "gdk" as gdk
import "sys" as sys
import "mgcollections" as collections

if (gtk.GTK_MAJOR_VERSION != 3) then {
    print "Error: This example is only compatible with GTK+ 3."
    sys.exit(1)
}

def window = gtk.window(gtk.GTK_WINDOW_TOPLEVEL)
window.title := "Simple graphics"
window.on "destroy" do { gtk.main_quit }
window.set_default_size(500, 250)

def da = gtk.drawing_area
da.set_size_request(500, 250)
window.add(da)

def instructions = collections.list.new
da.on "draw" do { c->
    for (instructions) do {inst->
        inst.apply(c)
    }
}

def Colour = object {
    method r(r')g(g')b(b') {
        object {
            def r is readable = r' / 255
            def g is readable = g' / 255
            def b is readable = b' / 255
            method asString {
                "rgb({r'}, {g'}, {b'})"
            }
        }
    }
    method zr(r')g(g')b(b') {
        return Colour.r(r' * 255)g(g' * 255)b(b' * 255)
    }
    method h(h')s(s')l(l') {
        def s = s' / 100
        def l = l' / 100
        var h := h'
        if (h > 360) then {
            h := h - 360
        }
        print "hsl({h}, {s}, {l})"
        var tmp := (2 * l - 1)
        if (tmp < 0) then { tmp := -tmp }
        def c = (1 - tmp) * s
        def h' = h / 60
        tmp := h'
        while {tmp >= 2} do {
            tmp := tmp - 2
        }
        tmp := tmp - 1
        if (tmp < 0) then { tmp := -tmp }
        def x = c * (1 - tmp)
        def m = l - c / 2
        print "c {c} h' {h'} x {x} m {m}"
        if (h' < 1) then {
            return Colour.zr(c + m)g(x + m)b(0 + m)
        }
        if (h' < 2) then {
            return Colour.zr(x + m)g(c + m)b(0 + m)
        }
        if (h' < 3) then {
            return Colour.zr(0 + m)g(c + m)b(x + m)
        }
        if (h' < 4) then {
            return Colour.zr(0 + m)g(x + m)b(c + m)
        }
        if (h' < 5) then {
            return Colour.zr(x + m)g(0 + m)b(c + m)
        }
        if (h' < 6) then {
            return Colour.zr(c + m)g(0 + m)b(x + m)
        }
        return Colour.r 0 g 0 b 0
    }
}
def Color = Colour

def Pi = 3.141592653589793

def white = Colour.r 255 g 255 b 255
def black = Colour.r 0 g 0 b 0

method fillRect(x, y, w, h)with(col) {
    instructions.push { ctx ->
        ctx.set_source_rgb(col.r, col.g, col.b)
        ctx.rectangle(0, 0, 500, 250)
        ctx.fill
    }
}

var ctx

method fillCircle(x,y)radius(radius)with(col) {
    instructions.push { ctx ->
        ctx.set_source_rgb(col.r, col.g, col.b)
        ctx.move_to(x,y)
        ctx.arc(x, y, radius, 0, Pi * 2, true)
        ctx.fill
    }
}

method drawRect(x, y, w, h)in(col) {
    instructions.push { ctx ->
        ctx.set_source_rgb(col.r, col.g, col.b)
        ctx.rectangle(x, y, w, h)
        ctx.stroke
    }
}

method drawLineFrom(x,y)to(x', y')in(col) {
    instructions.push { ctx ->
        ctx.set_source_rgb(col.r, col.g, col.b)
        ctx.move_to(x,y)
        ctx.line_to(x', y')
        ctx.stroke
    }
}

method drawSectorAt(x,y)radius(radius)from(angle1)to(angle2)in(col) {
    instructions.push { ctx ->
        ctx.set_source_rgb(col.r, col.g, col.b)
        ctx.move_to(x, y)
        ctx.arc(x, y, radius, angle1, angle2)
        ctx.fill
    }
}
method drawArcAround(x,y) radius(radius) width(width) from(angle1) to(angle2) in(col) {
    instructions.push { ctx ->
        ctx.set_source_rgb(col.r, col.g, col.b)
        ctx.arc(x, y, radius, angle1, angle2)
        ctx.arc_negative(x, y, radius - width, angle2, angle1)
        ctx.fill
    }
}

method write(s) at(x,y) in(col) {
    instructions.push { ctx ->
        ctx.set_source_rgb(col.r, col.g, col.b)
        ctx.move_to(x, y)
        ctx.show_text(s)
        ctx.fill
    }
}
method write(s) at(x,y) size(size) in(col) {
    instructions.push { ctx ->
        ctx.font_size := size
        ctx.set_source_rgb(col.r, col.g, col.b)
        ctx.move_to(x, y)
        ctx.show_text(s)
        ctx.fill
    }
}

fillRect(0, 0, 500, 250)with(black)

method end {
    window.show_all
    gtk.main
}

PYTHON_VERSION=3
GTK_VERSION=3.0
INCLUDE_DIR=/usr/include
HEADER_LOCATION=$(INCLUDE_DIR)/gtk-$(GTK_VERSION)
MINIGRACE_HEADERS=../minigrace
CAIRO_INCLUDE_DIR=$(INCLUDE_DIR)

PYTHON=python$(PYTHON_VERSION)

include Makefile.conf
include $(MINIGRACE_HEADERS)/Makefile.conf

all: gtk.gso gdk.gso cairo.gso
gtk.c: gwrap.py Makefile.conf
	$(PYTHON) gwrap.py $(HEADER_LOCATION)/gtk/gtk.h > gtk.c

gtk.gso: gtk.c
	gcc -Wall -o gtk.gso -I$(MINIGRACE_HEADERS) `pkg-config --cflags gtk+-$(GTK_VERSION)` $(UNICODE_LDFLAGS) -fPIC -shared gtk.c `pkg-config --libs gtk+-$(GTK_VERSION)`

gdk.c: gwrap.py Makefile.conf
	$(PYTHON) gwrap.py $(HEADER_LOCATION)/gdk/gdk.h $(HEADER_LOCATION)/gdk/gdkkeysyms.h > gdk.c

gdk.gso: gdk.c
	gcc -Wall -o gdk.gso -I$(MINIGRACE_HEADERS) `pkg-config --cflags gtk+-$(GTK_VERSION)` $(UNICODE_LDFLAGS) -fPIC -shared gdk.c `pkg-config --libs gtk+-$(GTK_VERSION)`

cairo.c: gwrap.py Makefile.conf
	$(PYTHON) gwrap.py $(CAIRO_INCLUDE_DIR)/cairo/cairo.h > cairo.c

cairo.gso: cairo.c
	gcc -Wall -o cairo.gso -I$(MINIGRACE_HEADERS) `pkg-config --cflags gtk+-$(GTK_VERSION)` $(UNICODE_LDFLAGS) -fPIC -shared cairo.c `pkg-config --libs gtk+-$(GTK_VERSION)`

clean:
	rm -f gtk.gso gtk.c
	rm -f gdk.gso gdk.c
	rm -f cairo.gso cairo.c
	rm -f helloworld helloworld.c helloworld.gcn helloworld.gct
	rm -f drawing drawing.c drawing.gcn drawing.gct
	rm -f drawing2 drawing2.c drawing2.gcn drawing2.gct
	rm -f greet greet.c greet.gcn greet.gct
	rm -f simpleeditor simpleeditor.c simpleeditor.gcn simpleeditor.gct
	rm -f pngviewer pngviewer.c pngviewer.gcn pngviewer.gct

.PHONY: clean all

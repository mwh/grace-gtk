PYTHON_VERSION=3
GTK_VERSION=3.0
INCLUDE_DIR=/usr/include
HEADER_LOCATION=$(INCLUDE_DIR)/gtk-$(GTK_VERSION)
MINIGRACE_HEADERS=../minigrace

PYTHON=python$(PYTHON_VERSION)

all: gtk.gso gdk.gso cairo.gso
gtk.c: gwrap.py
	$(PYTHON) gwrap.py $(HEADER_LOCATION)/gtk/gtk.h > gtk.c

gtk.gso: gtk.c
	gcc -o gtk.gso -I$(MINIGRACE_HEADERS) `pkg-config --cflags gtk+-$(GTK_VERSION)` `pkg-config --libs gtk+-$(GTK_VERSION)` -fPIC -shared gtk.c

gdk.c: gwrap.py
	$(PYTHON) gwrap.py $(HEADER_LOCATION)/gdk/gdk.h $(HEADER_LOCATION)/gdk/gdkkeysyms.h > gdk.c

gdk.gso: gdk.c
	gcc -o gdk.gso -I$(MINIGRACE_HEADERS) `pkg-config --cflags gtk+-$(GTK_VERSION)` `pkg-config --libs gtk+-$(GTK_VERSION)` -fPIC -shared gdk.c

cairo.c: gwrap.py
	$(PYTHON) gwrap.py $(INCLUDE_DIR)/cairo/cairo.h > cairo.c

cairo.gso: cairo.c
	gcc -o cairo.gso -I$(MINIGRACE_HEADERS) `pkg-config --cflags gtk+-$(GTK_VERSION)` `pkg-config --libs gtk+-$(GTK_VERSION)` -fPIC -shared cairo.c

clean:
	rm -f gtk.gso gtk.c
	rm -f gdk.gso gdk.c
	rm -f cairo.gso cairo.c
	rm -f helloworld helloworld.c helloworld.gcn
	rm -f drawing drawing.c drawing.gcn
	rm -f drawing2 drawing2.c drawing2.gcn
	rm -f greet greet.c greet.gcn

.PHONY: clean all

PYTHON_VERSION=3
GTK_VERSION=3.0
INCLUDE_DIR=/usr/include
HEADER_LOCATION=$(INCLUDE_DIR)/gtk-$(GTK_VERSION)
MINIGRACE_HEADERS=../minigrace

PYTHON=python$(PYTHON_VERSION)

all: gtk.gso
gtk.c: gtkwrap.py
	$(PYTHON) gtkwrap.py $(HEADER_LOCATION)/gtk/gtk.h > gtk.c

gtk.gso: gtk.c
	gcc -o gtk.gso -I$(MINIGRACE_HEADERS) `pkg-config --cflags gtk+-$(GTK_VERSION)` `pkg-config --libs gtk+-$(GTK_VERSION)` -fPIC -shared gtk.c

clean:
	rm -f gtk.gso gtk.c
	rm -f helloworld helloworld.c helloworld.gcn

.PHONY: clean all

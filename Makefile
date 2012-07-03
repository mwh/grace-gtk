GTK_VERSION=3.0
all: gtk.gso
gtk.c: gtkwrap.py
	python gtkwrap.py /usr/include/gtk-$(GTK_VERSION)/gtk.h > gtk.c

gtk.gso: gtk.c
	gcc -o gtk.gso `pkg-config --cflags gtk+-$(GTK_VERSION)` `pkg-config --libs gtk+-$(GTK_VERSION)` -fPIC -shared gtk.c


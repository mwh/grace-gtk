#!/usr/bin/python3
# grace-gtk - GTK+ bindings for Grace
# Copyright (C) 2012 Michael Homer
# This is free software with ABSOLUTELY NO WARRANTY.
# See the GNU GPL 3 for details.

import sys
import re
import itertools
import os.path

class func(object):
    def __init__(self, name, returns, params):
        self.name = name
        self.returns = returns
        params = params.replace('\t', ' ')
        self.params = list(filter(lambda x: x != '',
                                  map(str.strip, params.split(','))))

methods = {}
enums = []
classes = {}
constructors = []
usedconstructors = []
modulemethods = []
classallocators = set()

if len(sys.argv) < 2:
    sys.stderr.write("Usage: " + sys.argv[0] + ' <path-to-gtk.h>\n')
    sys.stderr.write("Generates a glue module for GTK+ and Grace.\n")
    sys.stderr.write("Copyright (C) 2012 Michael Homer\n")
    sys.stderr.write("This is free software with ABSOLUTELY NO WARRANTY.\n")
    exit(0)

basedir = os.path.dirname(os.path.dirname(sys.argv[1])) + '/'
mod = os.path.basename(sys.argv[1]).replace('.h', '')
MOD = mod.upper()

kinds = set([
    'void', 'GtkWidget*', 'const gchar *', 'const gchar*', 'gboolean',
    'GtkWidget *', 'cairo_t *', 'GdkWindow *', 'cairo_public void',
    'GtkOrientation', 'GtkAccelGroup*', 'GtkTextBuffer *', 'GtkTextIter *',
    'gchar *', 'gint', 'cairo_public cairo_surface_t *',
    'cairo_public int', 'GdkScreen *', 'GtkTextMark*'
])

included = set(['gtk/gtkaccelmap.h', 'gtk/gtkaboutdialog.h',
                'gtk/gtkscalebutton.h', 'gtk/gtktreeitem.h',
                'gtk/gtktext.h', 'gtk/gtktree.h'])

def stripcomments(s):
    return re.sub(r'/\*.+?\*/', '', s, 0, re.DOTALL)

def include_file(path):
    if path not in included:
        included.add(path)
        if os.path.exists(basedir + path):
            process_file(basedir + path)

def define_constant(con):
    enums.append(MOD + '_' + con)

def process_file(fn):
    logical_lines = []
    with open(fn) as fp:
        data = fp.read()
    data = stripcomments(data)
    logical_lines = data.split(";")
    for inc in re.findall('#include <(.+?)>', data):
        include_file(inc)
    for con in re.findall('#define ' + MOD + r'_([^() ]+?)\s+\(?[0-9a-fx]+\)?$', data,
                         re.MULTILINE):
        define_constant(con)
    for enm in re.findall(r'typedef enum.+?;', data, re.DOTALL):
        m = re.match('[^{]*\\{([^}]+)\\}', stripcomments(enm))
        if m is not None:
            enums.extend(list(map(str.strip,
                            map(lambda x: x.partition('=')[0],
                                map(stripcomments,
                                        re.sub('#.*', '',m.group(1)).split(
                                            ','))))))
    for line in logical_lines:
        if '#if' in line:
            line = re.sub('#.*', '', line)
        line = line.replace('\n', ' ').strip()
        line = re.sub(' +\*', ' *', line)
        if line.startswith('GDK_AVAILABLE_IN_'):
            line = line.partition(' ')[2]
        for k in kinds:
            if line.startswith(k) and '(' in line:
                name = line[len(k):].strip().split(' ', 1)[0]
                if '\t' in name:
                    name = name.partition('\t')[0]
                if '(' in name:
                    name = name.partition('(')[0]
                if not name:
                    continue
                if name.startswith('_'):
                    continue
                if not name.startswith(mod + '_'):
                    continue
                if (name == 'gtk_widget_destroyed'
                    or name == 'gtk_rc_set_default_files'
                    or name == 'gtk_icon_theme_set_search_path'
                    or name == 'gdk_device_free_history'
                    or name == 'gtk_false' or name == 'gtk_true'):
                    continue
                args = line.split('(', 1)[1].split(')', 1)[0]
                methods[name] = func(name, k, args)

process_file(sys.argv[1])

for f in sys.argv[2:]:
    include_file(f[len(basedir):])

class FailedCoerce(Exception):
    pass

tmp_count = 0
def coerce2gtk(dest, src, pre, post):
    global tmp_count
    if '*' in dest:
        dest = dest.replace('\t', ' ')
        dest = re.sub(' +', ' ', dest.rpartition('*')[0].strip()) + ' *'
    else:
        dest = dest.rpartition(' ')[0].strip()
    if dest == 'const gchar *' or dest == 'const gchar*':
        return '(const gchar *)grcstring(' + src + ')'
    elif dest == 'const char *' or dest == 'const char*':
        return '(const gchar *)grcstring(' + src + ')'
    elif dest == 'gboolean':
        return '(gboolean)istrue(' + src + ')'
    elif dest.endswith('Type'):
        return 'integerfromAny(' + src + ')'
    elif dest == 'GtkWidget *' or dest == 'GtkWidget*':
        return '((struct GraceGtkWidget*)' + src + ')->widget'
    elif dest == 'cairo_t *':
        return '((struct GraceCairoT*)' + src + ')->value'
    elif dest == 'GdkWindow *':
        return '(GdkWindow *)(((struct GraceGtkWidget*)' + src + ')->widget)'
    elif dest == 'gint' or dest == 'guint':
        return 'integerfromAny(' + src + ')'
    elif dest == 'double':
        return '(*(double*)' + src + '->data)'
    elif dest == 'GtkOrientation':
        return 'integerfromAny(' + src + ')'
    elif dest == 'GtkTextTag *':
        return '(GtkTextTag *)(((struct GraceGtkWidget*)' + src + ')->widget)'
    elif dest == 'GtkTextMark*' or dest == 'const GtkTextMark*':
        return '(GtkTextMark *)(((struct GraceGtkWidget*)' + src + ')->widget)'
    elif dest == 'GtkTextIter *' or dest == 'const GtkTextIter *':
        return '(GtkTextIter *)(((struct GraceGtkWidget*)' + src + ')->widget)'
    elif dest == 'GtkAccelGroup *':
        return '(GtkAccelGroup *)(((struct GraceGtkWidget*)' + src + ')->widget)'
    elif dest == 'GdkScreen *':
        return '(GdkScreen *)(((struct GraceGtkWidget*)' + src + ')->widget)'
    elif dest == 'cairo_surface_t *':
        return '(cairo_surface_t *)(((struct GraceGtkWidget*)' + src + ')->widget)'
    elif dest == 'GtkAdjustment *':
        return 'NULL'
    elif dest == 'gint *':
        pre.append("Object tmp_obj_" + str(tmp_count) + ";")
        pre.append("int parts_" + str(tmp_count) + "[] = {0};")
        pre.append("gint tmp_gint_" + str(tmp_count)
                   + " = integerfromAny(callmethod(" + src + ', "value", 1, '
                   + 'parts_' + str(tmp_count) + ', &tmp_obj_'
                   + str(tmp_count) + '));')
        post.append('tmp_obj_' + str(tmp_count) + ' = alloc_Float64(tmp_gint_'
                   + str(tmp_count) + ');')
        post.append('parts_' + str(tmp_count) + '[0] = 1;')
        post.append('callmethod(' + src + ', "value:=", 1, parts_'
                    + str(tmp_count) + ', &tmp_obj_' + str(tmp_count) + ');')
        ret = '&tmp_gint_' + str(tmp_count)
        tmp_count = tmp_count + 1
        return ret
    else:
        raise FailedCoerce(dest)
        return '/*unknown: ' + dest + '*/ NULL'

def doconstructor(k, m):
    cls = k[4:-4]
    if MOD + cls not in classallocators:
        return
    casts = []
    try:
        casts = list(map(lambda x: coerce2gtk(x[0], 'argv[' + str(x[1]) +
                                              ']', [], []),
                    zip(m.params, itertools.count())))
    except FailedCoerce as e:
        if m.params[0] != 'void':
            print("// Failed constructor " + k + ": could not coerce "
                  + e.args[0])
            return
    print("Object grace_" + k + "(Object self, int argc, int *argcv,")
    print("    Object *argv, int flags) {")
    if casts and list(filter(lambda x: x != 'NULL', casts)):
        print('    if (argc < 1 || argcv[0] < ' + str(len(casts)) + ')')
        print('        gracedie("' + k[4:-4] + ' requires ' + str(len(casts))
              + ' arguments, got %i. Signature: ' + k[4:-4] + '('
              + ', '.join(m.params) + ').", argcv[0]);')
        print("    GtkWidget *w = " + k + "(" + ','.join(casts) + ');')
    elif casts:
        # All parameters are passed as nulls - don't enforce a size
        print("    GtkWidget *w = " + k + "(" + ','.join(casts) + ');')
    else:
        print("    GtkWidget *w = (GtkWidget *)" + k + "();")
    print("""
    Object o = alloc_obj(sizeof(struct GraceGtkWidget) - sizeof(struct Object),
         alloc_class_""" + MOD + cls + """());
    struct GraceGtkWidget *ggw = (struct GraceGtkWidget *)o;
    ggw->widget = w;
    return o;""")
    print("}")
    usedconstructors.append(k)

print("""
// This file is generated by the grace-gtk wrapper. Modifications
// should be made to the wrapper script, not this file.
// grace-gtk was written by Michael Homer and is available from
// <https://github.com/mwh/grace-gtk>.
// This is free software with ABSOLUTELY NO WARRANTY.
""")
print("#include \"gracelib.h\"")
print("#include <gtk/gtk.h>")
print("#include <gdk/gdk.h>")
for f in sys.argv[2:]:
    print("#include <" + f[len(basedir):] + ">")
print("""
#include <stdlib.h>
#include <string.h>
extern Object none;

struct GraceGtkWidget {
    int32_t flags;
    ClassData class;
    GtkWidget *widget;
};
struct GraceCairoT {
    int32_t flags;
    ClassData class;
    cairo_t *value;
};
struct GraceGdkEvent {
    int32_t flags;
    ClassData class;
    GdkEvent *value;
};

ClassData alloc_class_CAIROcairo();

Object Object_asString(Object, int nparts, int *argcv,
        Object*, int flags);
Object Object_Equals(Object, int, int*,
        Object*, int flags);
Object Object_NotEquals(Object, int, int*,
        Object*, int);

Object alloc_GtkWidget(GtkWidget *w);
Object alloc_GtkTextBuffer(GtkTextBuffer *buf);
Object alloc_GtkTextMark(GtkTextMark *mark);
Object grace_gtk_text_buffer_create_tag(Object self, int argc, int *argcv,
    Object *argv, int flags);
static void grace_gtk_callback_block0(GtkWidget *widget, gpointer block) {
    callmethod((Object)block, "apply", 0, NULL, NULL);
}
Object alloc_CairoT(cairo_t *);
Object alloc_CairoSurfaceT(cairo_surface_t *);
Object alloc_GdkEvent(GdkEvent *);
Object alloc_GdkScreen(GdkScreen *);
static void grace_gtk_callback_block1(GtkWidget *widget, cairo_t *tmp1,
      gpointer block) {
    gc_pause();
    Object ct = alloc_CairoT(tmp1);
    int i[] = {1};
    callmethod((Object)block, "apply", 1, i, &ct);
    gc_unpause();
}
static void grace_gtk_callback_block1_GdkEvent(GtkWidget *widget,
      GdkEvent *tmp1, gpointer block) {
    gc_pause();
    Object ct = alloc_GdkEvent(tmp1);
    int i[] = {1};
    callmethod((Object)block, "apply", 1, i, &ct);
    gc_unpause();
}
static void grace_gtk_callback_block1_CairoContext(GtkWidget *widget, cairo_t *tmp1,
      gpointer block) {
    gc_pause();
    Object ct = alloc_CairoT(tmp1);
    int i[] = {1};
    callmethod((Object)block, "apply", 1, i, &ct);
    gc_unpause();
}
static void grace_gtk_callback_block1_gchararray(GtkWidget *widget, gchar *tmp1,
      gpointer block) {
    gc_pause();
    Object ct = alloc_String(tmp1);
    int i[] = {1};
    callmethod((Object)block, "apply", 1, i, &ct);
    gc_unpause();
}
static Object grace_g_signal_connect(Object self, int argc, int *argcv,
      Object *argv, int flags) {
    struct GraceGtkWidget *w = (struct GraceGtkWidget *)self;
    char *c = grcstring(argv[0]);
    GType tp = G_OBJECT_TYPE(w->widget);
    guint sig = g_signal_lookup(c, tp);
    GSignalQuery query;
    g_signal_query(sig, &query);
    gc_root(argv[1]);
    if (query.n_params == 0) {
        g_signal_connect(w->widget, c,
          G_CALLBACK(grace_gtk_callback_block0), argv[1]);
    } else if (query.n_params == 1) {
        const gchar *s = g_type_name(query.param_types[0]);
        if (strcmp(s, "CairoContext") == 0) {
            g_signal_connect(w->widget, c,
                G_CALLBACK(grace_gtk_callback_block1_CairoContext), argv[1]);
        } else if (strcmp(s, "GdkEvent") == 0) {
            g_signal_connect(w->widget, c,
                G_CALLBACK(grace_gtk_callback_block1_GdkEvent), argv[1]);
        } else if (strcmp(s, "gchararray") == 0) {
            g_signal_connect(w->widget, c,
                G_CALLBACK(grace_gtk_callback_block1_gchararray), argv[1]);
        } else {
            g_signal_connect(w->widget, c,
                G_CALLBACK(grace_gtk_callback_block1), argv[1]);
        }
    }
    return self;
}
static void grace_gclosure_callback(Object block) {
    callmethod(block, "apply", 0, NULL, NULL);
}
static GClosure *grace_gclosure(Object block) {
    GClosure *closure = g_cclosure_new_swap(G_CALLBACK(grace_gclosure_callback),
        block, NULL);
    return closure;
}
static Object grace_gtk_accel_group_connect(Object self, int argc, int *argcv,
      Object *argv, int flags) {
    struct GraceGtkWidget *w = (struct GraceGtkWidget *)self;
    GtkAccelGroup *ag = (GtkAccelGroup *)w->widget;
    gc_root(argv[1]);
    guint key = integerfromAny(argv[0]);
    gtk_accel_group_connect(ag, key, 0, 0, grace_gclosure(argv[1]));
    return self;
}
ClassData GraceCairoT;
Object alloc_CairoT(cairo_t *val) {
    if (!GraceCairoT) {
        GraceCairoT = alloc_class("CairoT", 2);
    }
    Object o = alloc_obj(sizeof(struct GraceCairoT) - sizeof(struct Object),
        alloc_class_CAIROcairo());
    struct GraceCairoT *t = (struct GraceCairoT *)o;
    t->value = val;
    return o;
}
ClassData GraceGdkEvent;
Object grace_GdkEvent_keyval(Object self, int argc, int *argcv, Object *argv,
    int flags) {
    struct GraceGdkEvent *s = (struct GraceGdkEvent *)self;
    return alloc_Float64(((GdkEventKey *)s->value)->keyval);
}
Object grace_GdkEvent_x(Object self, int argc, int *argcv, Object *argv,
    int flags) {
    struct GraceGdkEvent *s = (struct GraceGdkEvent *)self;
    return alloc_Float64((int)((GdkEventButton *)s->value)->x);
}
Object grace_GdkEvent_y(Object self, int argc, int *argcv, Object *argv,
    int flags) {
    struct GraceGdkEvent *s = (struct GraceGdkEvent *)self;
    return alloc_Float64((int)((GdkEventButton *)s->value)->y);
}
Object alloc_GdkEvent(GdkEvent *val) {
    if (!GraceGdkEvent) {
        GraceGdkEvent = alloc_class("GdkEvent", 3);
        add_Method(GraceGdkEvent, "keyval", &grace_GdkEvent_keyval);
        add_Method(GraceGdkEvent, "x", &grace_GdkEvent_x);
        add_Method(GraceGdkEvent, "y", &grace_GdkEvent_y);
    }
    Object o = alloc_obj(sizeof(struct GraceGdkEvent) - sizeof(struct Object),
        GraceGdkEvent);
    struct GraceGdkEvent *t = (struct GraceGdkEvent *)o;
    t->value = val;
    return o;
}
static Object grace_g_object_set(Object self, int argc, int *argcv,
      Object *argv, int flags) {
    struct GraceGtkWidget *w = (struct GraceGtkWidget *)self;
    char *c = grcstring(argv[0]);
    GObjectClass *cls = G_OBJECT_GET_CLASS(w->widget);
    GParamSpec *spec = g_object_class_find_property(cls, c);
    const gchar *s = g_type_name(spec->value_type);
    if (strcmp(s, "gboolean") == 0) {
        g_object_set(w->widget, c, (gboolean)istrue(argv[1]), NULL);
    } else if (strcmp(s, "gchararray") == 0) {
        fprintf(stderr, "trying to set gchararray to: %s\\n",
            grcstring(argv[1]));
        g_object_set(w->widget, c, grcstring(argv[1]), NULL);
    } else {
        fprintf(stderr, "unknown property type name in gobject_set_property: %s\\n", s);
    }
    return self;
}
""")

def coercereturn(m, s, post=[]):
    ret = 'none'
    if (m.returns == 'const gchar *' or m.returns == 'const gchar*' or
            m.returns == 'gchar *'):
        ret = "alloc_String(" + s + ")"
    elif m.returns == 'cairo_t *':
        ret = "alloc_CairoT(" + s + ")"
    elif m.returns == 'cairo_public cairo_surface_t *':
        ret = "alloc_CairoSurfaceT(" + s + ")"
    elif m.returns == 'GtkWidget *':
        ret = "alloc_GtkWidget((GtkWidget *)(" + s + "))"
    elif m.returns == 'GdkWindow *':
        ret = "alloc_GtkWidget((GtkWidget *)(" + s + "))"
    elif m.returns == 'GtkTextBuffer *':
        ret = "alloc_GtkTextBuffer((GtkTextBuffer *)(" + s + "))"
    elif m.returns == 'GtkTextMark*':
        ret = "alloc_GtkTextMark((GtkTextMark *)(" + s + "))"
    elif m.returns == 'GdkScreen *':
        ret = "alloc_GdkScreen((GdkScreen *)(" + s + "))"
    elif m.returns == 'gboolean':
        ret = "alloc_Boolean(" + s + ")"
    elif m.returns == 'gint' or m.returns == 'cairo_public int':
        ret = "alloc_Float64(" + s + ")"
    elif m.returns == 'void':
        print("    " + s + ";")
        pass
    else:
        print("    // Don't understand how to return '" + m.returns + "'.")
        print("    " + s + ";")
    if post:
        print("    Object retval = " + ret + ";")
        for x in post:
            print("    " + x)
        ret = "retval;"
    print("    return " + ret + ";")

def classof(k):
    cls = ''
    if k.startswith('gtk_accel_group_'):
        cls = 'accel_group'
    elif k.startswith('gtk_drawing_area_'):
        cls = 'drawing_area'
    elif k.startswith('gtk_text_view_'):
        cls = 'text_view'
    elif k.startswith('gtk_text_buffer_'):
        cls = 'text_buffer'
    elif k.startswith('gtk_text_mark_'):
        cls = 'text_mark'
    elif k.startswith('gtk_text_iter_'):
        cls = 'text_iter'
    elif k.startswith('gtk_text_tag_'):
        cls = 'text_tag'
    elif k.startswith('gtk_scrolled_window_'):
        cls = 'scrolled_window'
    elif k.startswith('cairo_image_surface_create'):
        # Hacky way to switch some cairo_* methods to be found
        # on the module object itself.
        return '*modulemethod'
    elif k.startswith('cairo_image_surface_'):
        cls = 'image_surface'
    elif k.startswith('cairo_'):
        cls = 'cairo'
    else:
        cls = k.split('_')[1]
    if cls not in classes:
        classes[cls] = []
    return cls

for k, m in methods.items():
    if '*' in m.params[0]:
        selftype = ''.join(m.params[0].rpartition('*')[0:2])
    else:
        selftype = m.params[0]
    if k.endswith('_new'):
        constructors.append(k)
        classof(k)
        continue
    if classof(k) == 'free':
        continue
    elif selftype != 'void' and not selftype.endswith('*'):
        continue
    cls = classof(k)
    if cls == '*modulemethod':
        m.params[0:0] = ['']
    pre = []
    post = []
    try:
        casts = list(map(lambda x: coerce2gtk(x[0], 'argv[' + str(x[1]) +
                                              ']', pre, post),
                    zip(m.params[1:], itertools.count())))
    except FailedCoerce as e:
        print("// Failed " + k + ": could not coerce " + e.args[0])
        print("// " + str(m.params))
        continue
    print("Object grace_" + k + "(Object self, int argc, int *argcv, "
          + "Object *argv, int flags) {")
    for x in pre:
        print("  " + x)
    if selftype == 'void' and m.returns == 'gint':
        coercereturn(m, "  " + k + "()", post)
    elif selftype == 'void':
        coercereturn(m, "  " + k + "(" + ','.join(casts) + ')')
    elif cls == '*modulemethod':
        coercereturn(m, "  " + k + "(" + ','.join(casts) + ')', post)
    else:
        if selftype == 'cairo_t *':
            print("    cairo_t *s = ((struct GraceCairoT*)self)->value;")
        else:
            print("  {} s = ({})(((struct GraceGtkWidget *)self)->widget);".format(selftype, selftype))
        if casts:
            print('    if (argc < 1 || argcv[0] < ' + str(len(casts)) + ')')
            print('        gracedie("' + mod + ' method requires '
                  + str(len(casts))
                  + ' arguments, got %i. Signature: ' + k + '('
                  + ', '.join(m.params[1:]) + ').", argcv[0]);')
            coercereturn(m, "  " + k + "(s, " + ','.join(casts) + ')', post)
        else:
            coercereturn(m, "  " + k + "(s)", post)
    print("}")
    if cls == '*modulemethod':
        modulemethods.append(k)
    else:
        classes[cls].append(k)

for cls in classes:
    if cls != 'widget' and cls != 'container':
        if 'widget' in classes:
            classes[cls].extend(classes['widget'])
        if 'container' in classes:
            classes[cls].extend(classes['container'])
    if cls == 'vbox' or cls == 'hbox':
        classes[cls].extend(classes['box'])
    print("ClassData alloc_class_" + MOD + cls + "();")
    print("Object grace_" + MOD + "_as_" + cls + "(Object self,"
          + "int argc, int *argcv, Object *argv, int flags) {")
    print("""    GtkWidget *w = ((struct GraceGtkWidget *)self)->widget;
    Object o = alloc_obj(sizeof(struct GraceGtkWidget)- sizeof(struct Object),
         alloc_class_""" + MOD + cls + """());
    struct GraceGtkWidget *ggw = (struct GraceGtkWidget *)o;
    ggw->widget = w;
    return o;
}""")
    classes[cls].append(MOD + '_as')

print("static ClassData AsClass;")
print("Object grace_" + MOD + "_as(Object self, int argc, int *argcv, "
      + "Object *argv, int flags) {")
print('''
    if (!AsClass) {
        AsClass = alloc_class("'''+MOD+'''-as", '''+str(len(classes))+ ');')
for cls in classes:
    print('        add_Method(AsClass, "' + cls
          + '", &grace_' + MOD + '_as_' + cls + ');')
print('''
    }
    Object o = alloc_obj(sizeof(struct GraceGtkWidget) - sizeof(struct Object),
        AsClass);
    struct GraceGtkWidget *w = (struct GraceGtkWidget *)o;
    w->widget = ((struct GraceGtkWidget *)self)->widget;
    return o;
}''')

if 'free' in classes:
    del classes['free']
if 'text_buffer' in classes:
    classes['text_buffer'].append('gtk_text_buffer_create_tag')
for cls in classes:
    classallocators.add(MOD + cls)
    print("ClassData " + MOD + "" + cls + ";")
    print("ClassData alloc_class_" + MOD + "" + cls + "() {")
    print("  if (" + MOD + "" + cls + ") return " + MOD + "" + cls + ";")
    print("  " + MOD + "{} = alloc_class(\"{}\", {});".format(cls, cls,
                                                      7+len(classes[cls])))
    print("  gc_root((Object)" + MOD + "" + cls + ");")
    print("""add_Method(""" + MOD + """""" + cls + """, "==", &Object_Equals);
    add_Method(""" + MOD + """""" + cls + """, "!=", &Object_NotEquals);
    add_Method(""" + MOD + """""" + cls + """, "asString", &Object_asString);
    add_Method(""" + MOD + """""" + cls + """, "on()do", &grace_g_signal_connect);
    add_Method(""" + MOD + """""" + cls + """, "gobject_property_set", &grace_g_object_set);
    add_Method(""" + MOD + """""" + cls + """, "connect", &grace_g_signal_connect);
    add_Method(""" + MOD + """""" + cls + """, "accel_connect", &grace_gtk_accel_group_connect);""")
    for k in classes[cls]:
        gnm = k.split('_', 2)[-1]
        if cls == 'cairo':
            gnm = k.split('_', 1)[-1]
        elif cls == 'image_surface':
            gnm = k.split('_', 3)[-1]
        elif k.startswith("gtk_" + cls):
            gnm = k[len(cls)+5:]
        if gnm.startswith('get_') and len(methods[k].params) == 1:
            gnm = gnm[4:]
        elif gnm.startswith('set_') and len(methods[k].params) == 2:
            gnm = gnm[4:] + ":="
        print("  add_Method({}{}, \"{}\", &grace_{});".format(MOD, cls, 
            gnm, k))
    print("  return " + MOD + cls + ";")
    print("}")

for con in constructors:
    doconstructor(con, methods[con])

for x in enums:
    print("Object grace_" + mod + "_" + x
          + "(Object self, int argc, int *argcv,")
    print("    Object *args, int flags) {")
    print("    return alloc_Float64(" + x + ");")
    print("}")

if mod == 'gdk':
    print("""
Object grace_gdk_cairo_create(Object self, int nparts, int *argcv,
          Object *argv, int flags) {
    struct GraceGtkWidget *w = (struct GraceGtkWidget *)argv[0];
    return alloc_CairoT(gdk_cairo_create((GdkWindow *)(w->widget)));
}
Object alloc_GdkScreen(GdkScreen *screen) {
    Object o = alloc_obj(sizeof(struct GraceGtkWidget) - sizeof(struct Object),
         alloc_class_GDKscreen());
    struct GraceGtkWidget *ggw = (struct GraceGtkWidget *)o;
    ggw->widget = (GtkWidget *)screen;
    return o;
}
""")
elif mod == 'gtk':
    print("""
Object alloc_GtkWidget(GtkWidget *widget) {
    Object o = alloc_obj(sizeof(struct GraceGtkWidget) - sizeof(struct Object),
      alloc_class_GTKwidget());
    struct GraceGtkWidget *w = (struct GraceGtkWidget *)o;
    w->widget = widget;
    return o;
}
Object alloc_GtkTextBuffer(GtkTextBuffer *buf) {
    Object o = alloc_obj(sizeof(struct GraceGtkWidget) - sizeof(struct Object),
         alloc_class_GTKtext_buffer());
    struct GraceGtkWidget *ggw = (struct GraceGtkWidget *)o;
    ggw->widget = (GtkWidget *)buf;
    return o;
}
Object alloc_GtkTextMark(GtkTextMark *mark) {
    Object o = alloc_obj(sizeof(struct GraceGtkWidget) - sizeof(struct Object),
         alloc_class_GTKtext_mark());
    struct GraceGtkWidget *ggw = (struct GraceGtkWidget *)o;
    ggw->widget = (GtkWidget *)mark;
    return o;
}
Object grace_gtk_text_iter_new(Object self, int argc, int *argcv,
    Object *argv, int flags) {
    GtkTextIter *iter = malloc(sizeof(GtkTextIter));
    Object o = alloc_obj(sizeof(struct GraceGtkWidget) - sizeof(struct Object),
         alloc_class_GTKtext_iter());
    struct GraceGtkWidget *ggw = (struct GraceGtkWidget *)o;
    ggw->widget = (GtkWidget *)iter;
    return o;
}
Object grace_gtk_text_buffer_create_tag(Object self, int argc, int *argcv,
    Object *argv, int flags) {
    struct GraceGtkWidget *w = (struct GraceGtkWidget *)self;
    char *tn = grcstring(argv[0]);
    char *c = grcstring(argv[1]);
    GtkTextTag *tag = gtk_text_tag_new(NULL);
    GObjectClass *cls = G_OBJECT_GET_CLASS(tag);
    GParamSpec *spec = g_object_class_find_property(cls, c);
    const gchar *s = g_type_name(spec->value_type);
    if (strcmp(s, "gboolean") == 0) {
        tag = gtk_text_buffer_create_tag((GtkTextBuffer *)w->widget,
          tn, c, (gboolean)istrue(argv[2]), NULL);
    } else if (strcmp(s, "gchararray") == 0) {
        tag = gtk_text_buffer_create_tag((GtkTextBuffer *)w->widget,
          tn, c, grcstring(argv[2]), NULL);
    } else {
        fprintf(stderr, "unknown property type name in create_tag: %s\\n", s);
    }
    Object o = alloc_obj(sizeof(struct GraceGtkWidget) - sizeof(struct Object),
         alloc_class_GTKtext_tag());
    struct GraceGtkWidget *ggw = (struct GraceGtkWidget *)o;
    ggw->widget = (GtkWidget *)tag;
    return o;
}
""")
elif mod == 'cairo':
    print("""
Object alloc_CairoSurfaceT(cairo_surface_t *c) {
    Object o = alloc_obj(sizeof(struct GraceGtkWidget) - sizeof(struct Object),
         alloc_class_CAIROimage_surface());
    struct GraceGtkWidget *ggw = (struct GraceGtkWidget *)o;
    ggw->widget = (GtkWidget *)c;
    return o;
}
""")

gtk_size = len(classes) + len(enums) + 3
print("""
Object """ + mod + """module;
Object module_""" + mod + """_init() {
    if (""" + mod + """module)
        return """ + mod + """module;
    int n = 0;
    gtk_init(&n, NULL);""")
if mod == 'gtk':
    print("""dlmodule("gdk");
dlmodule("cairo");""")
print("""
    ClassData c = alloc_class("Module<""" + mod + """>", """
      + str(gtk_size) + ");")
for x in enums:
    print("    add_Method(c, \"" + x + "\", &grace_" + mod + "_" + x + ");")
for x in usedconstructors:
    cls = x[4:-4]
    print("    add_Method(c, \"" + cls + "\", &grace_" + x + ");")
for x in modulemethods:
    print("    add_Method(c, \"" + x[len(mod)+1:] + "\", &grace_" + x + ");")
if mod == 'gtk':
    print("    add_Method(c, \"main\", &grace_gtk_main);")
    print("    add_Method(c, \"main_quit\", &grace_gtk_main_quit);")
    print("    add_Method(c, \"connect\", &grace_g_signal_connect);")
    print("    add_Method(c, \"text_iter\", &grace_gtk_text_iter_new);")
elif mod == 'gdk':
    print("    add_Method(c, \"cairo\", &grace_gdk_cairo_create);")
    print("    add_Method(c, \"screen_get_default\", &grace_gdk_screen_get_default);")
print("    " + mod + "module = alloc_obj(sizeof(Object), c);")
print("    return " + mod + "module;")
print("}")

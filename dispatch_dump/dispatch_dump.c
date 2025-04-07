/* dispatch_dump: A quick hack to dump the gi_dispa data (the Glk API
   description) out as a text or XML file.

   Link this with cheapglk, and run:

   ./dispatch_dump -q --xml > dispatch_dump.xml

   This program is in the public domain.
*/

#include "glk.h"
#include "glkstart.h" /* This comes with the Glk library. */
#include "gi_dispa.h"

#include <string.h>
#include <stdio.h>

static int usexml = FALSE;

glkunix_argumentlist_t glkunix_arguments[] = {
    { "--xml", glkunix_arg_NoValue, 
      "--xml: generate XML output rather than flat text" },
    { NULL, glkunix_arg_End, NULL }
};

int glkunix_startup_code(glkunix_startup_t *data)
{
    int ix;
    for (ix=0; ix<data->argc; ix++) {
        if (!strcmp(data->argv[ix], "--xml"))
            usexml = TRUE;
    }
    return TRUE;
}

static char *xml_encode(char *str) {
    static char buf[256];
    char *bx, *cx;

    cx = buf;
    for (bx=str; *bx; bx++) {
        if (*bx == '&') {
            *cx++ = '&';
            *cx++ = 'a';
            *cx++ = 'm';
            *cx++ = 'p';
            *cx++ = ';';
        }
        else if (*bx == '<') {
            *cx++ = '&';
            *cx++ = 'l';
            *cx++ = 't';
            *cx++ = ';';
        }
        else if (*bx == '>') {
            *cx++ = '&';
            *cx++ = 'g';
            *cx++ = 't';
            *cx++ = ';';
        }
        else {
            *cx++ = *bx;
        }
    }

    *cx = '\0';
    return buf;
}

void glk_main(void)
{
    winid_t mainwin;
    int count, ix;
    char buf[256];

    mainwin = glk_window_open(NULL, 0, 0, wintype_TextBuffer, 0);
    if (!mainwin)
        return;
    glk_set_window(mainwin);

    if (usexml) {
        glui32 vers = glk_gestalt(gestalt_Version, 0);
        sprintf(buf, "<glkapi version=\"%d.%d.%d\">\n",
            (vers >> 16) & 0xFFFF, (vers >> 8) & 0xFF, (vers & 0xFF));
        glk_put_string(buf);
    }

    count = gidispatch_count_classes();
    if (usexml)
        sprintf(buf, "  <classes count=\"%d\">\n", count);
    else
        sprintf(buf, "* classes %d\n", count);
    glk_put_string(buf);
    for (ix=0; ix<count; ix++) {
        gidispatch_intconst_t *constant = gidispatch_get_class(ix);
        if (usexml)
            sprintf(buf, "    <class name=\"%s\" value=\"%ld\" />\n", constant->name, (long)constant->val);
        else
            sprintf(buf, "%s %ld\n", constant->name, (long)constant->val);
        glk_put_string(buf);
    }
    if (usexml)
        glk_put_string("  </classes>\n");
    glk_put_string("\n");

    count = gidispatch_count_intconst();
    if (usexml)
        sprintf(buf, "  <constants count=\"%d\">\n", count);
    else
        sprintf(buf, "* constants %d\n", count);
    glk_put_string(buf);
    for (ix=0; ix<count; ix++) {
        gidispatch_intconst_t *constant = gidispatch_get_intconst(ix);
        if (usexml)
            sprintf(buf, "    <constant name=\"%s\" value=\"%ld\" />\n", constant->name, (long)constant->val);
        else
            sprintf(buf, "%s %ld\n", constant->name, (long)constant->val);
        glk_put_string(buf);
    }
    if (usexml)
        glk_put_string("  </constants>\n");
    glk_put_string("\n");

    count = gidispatch_count_functions();
    if (usexml)
        sprintf(buf, "  <functions count=\"%d\">\n", count);
    else
        sprintf(buf, "* functions %d\n", count);
    glk_put_string(buf);
    for (ix=0; ix<count; ix++) {
        gidispatch_function_t *func = gidispatch_get_function(ix);
        char *proto = gidispatch_prototype(func->id);
        if (!proto)
            proto = "_";
        if (usexml)
            proto = xml_encode(proto);
        if (usexml)
            sprintf(buf, "    <function id=\"%ld\" name=\"%s\" proto=\"%s\" />\n", (long)func->id, func->name, proto);
        else
            sprintf(buf, "%ld %s %s\n", (long)func->id, func->name, proto);
        glk_put_string(buf);
    }
    if (usexml)
        glk_put_string("  </functions>\n");
    glk_put_string("\n");

    if (usexml)
        glk_put_string("</glkapi>\n");
}

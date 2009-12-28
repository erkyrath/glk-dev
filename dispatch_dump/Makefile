# Unix Makefile for dispatch_dump.

# To use this, you must set three variables. GLKINCLUDEDIR must be the 
# directory containing glk.h, glkstart.h, and the Make.library file.
# GLKLIBDIR must be the directory containing the library.a file.
# And GLKMAKEFILE must be the name of the Make.library file. Two
# sets of values appear below; uncomment one of them and change the
# directories appropriately.

GLKINCLUDEDIR = ../cheapglk
GLKLIBDIR = ../cheapglk
GLKMAKEFILE = Make.cheapglk

# Pick a C compiler.
#CC = cc
CC = gcc

OPTIONS = -g -Wall -Wmissing-prototypes -Wstrict-prototypes -Wno-unused -DOS_UNIX

include $(GLKINCLUDEDIR)/$(GLKMAKEFILE)

CFLAGS = $(OPTIONS) -I$(GLKINCLUDEDIR)
LIBS = -L$(GLKLIBDIR) $(GLKLIB) $(LINKLIBS) 

OBJS = dispatch_dump.o

all: dispatch_dump

dispatch_dump: $(OBJS)
	$(CC) $(OPTIONS) -o dispatch_dump $(OBJS) $(LIBS)


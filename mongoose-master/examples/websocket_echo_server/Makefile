# Copyright (c) 2014 Cesanta Software
# All rights reserved

PROG = websocket_echo_server_3
UTIL = /home/dell/bin/ctp/test7
CTP = /home/dell/bin/ctp
CFLAGS = -W -Wall -I../.. -pthread -g -O0 $(CFLAGS_EXTRA)
CXXFLAGS = -W -g -Wall -std=c++11 -I../.. -I$(CTP) -I$(UTIL) -pthread -g -O0 $(CFLAGS_EXTRA)
SOURCES = $(PROG).c ../../mongoose.c $(UTIL)/util.cpp

$(PROG): $(SOURCES)
	$(CXX) -o $(PROG) $(SOURCES) $(CXXFLAGS)

clean:
	rm -rf $(PROG) *.exe *.dSYM *.obj *.exp .*o *.lib

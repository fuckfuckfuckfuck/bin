CTPDIR = /opt/6.3.0_20140811_traderapi_linux64
## /opt/v6.3.0_20140521_traderapi_linux/v6.3.0_20140521_traderapi_linux64

LOG4CPLUS = /home/dell/bin/log4cplus/112
CTPSETTING = .
## //**TODO  VPATH = $(CTP):$(CTPSETTING)
MONGOOSE = /home/dell/bin/mongoose-master
BOOST = /opt/boost_1_56_0


PROG = main_0
CFLAGS = -W -Wall -I../.. -pthread -g -O0 $(CFLAGS_EXTRA)
## CXXFLAGS = -g -O2 -Wall -I$(LOG4CPLUS)/include -I$(CTP) -I$(CTPSETTING) -I$(MONGOOSE) -fdiagnostics-show-caret -Wextra -pedantic -Wstrict-aliasing -Wstrict-overflow -Woverloaded-virtual -Wold-style-cast -Wc++0x-compat -Wc++11compat -Wundef -Wshadow -Wformat -Wsuggest-attribute=format -Wsuggest-attribute=format -Wsuggest-attribute noreturn -Wno-variadic-macros -fvisibility=hidden -pthread
## -I$(LOG4CPLUS)/include 

## CXXFLAGS = -g -std=c++11 -pthread -O2 -I$(CTP) -I$(CTPSETTING) -I$(BOOST) -I$(LOG4CPLUS)/include -Wextra -pedantic -Wstrict-aliasing -Wstrict-overflow -Woverloaded-virtual -Wold-style-cast -Wc++0x-compat -Wundef -Wshadow -Wformat -Wno-variadic-macros -fvisibility=hidden 

CXXFLAGS = -g -I$(LOG4CPLUS)/include 

LDFLAGS="-Wl,-rpath /home/dell/bin/log4cplus/112/lib"

## CXXFLAGS = -g -Wall -I$(CTP) -I$(CTPSETTING) -I$(LOG4CPLUS)
## SOURCES = $(CTPSETTING)QuoteSpi201410.cpp $(PROG).c $(MONGOOSE)/mongoose.c $(LOG4CPLUS)/lib/liblog4cplus.so
## SOURCES = $(CTPSETTING)/main.cpp $(CTPSETTING)/QuoteSpi.cpp $(CTPSETTING)/util.cpp $(CTPSETTING)/twinbuffer.cpp $(CTPSETTING)/msgque.cpp $(MONGOOSE)/mongoose.c $(CTP)/thostmduserapi.so $(LOG4CPLUS)/lib/liblog4cplus.so 

## SOURCES = $(CTPSETTING)/main.cpp $(CTPSETTING)/QuoteSpi.cpp $(CTPSETTING)/util.cpp $(CTPSETTING)/twinbuffer.cpp $(CTPSETTING)/msgque.cpp $(MONGOOSE)/mongoose.c $(CTP)/thostmduserapi.so  

## SOURCES = $(CTPSETTING)/main_1.cpp $(CTPSETTING)/util.cpp $(CTP)/thostmduserapi.so $(CTP)/thosttraderapi.so $(LOG4CPLUS)/lib/liblog4cplus.so 

## SOURCES = $(CTPSETTING)/$(PROG).cpp $(CTPSETTING)/TraderSpi.cpp  $(CTPDIR)/thosttraderapi.so 
## SOURCES = $(CTPSETTING)/$(PROG).cpp $(CTPSETTING)/libtrader_test.so
SOURCES = $(CTPSETTING)/$(PROG).cpp $(LOG4CPLUS)/lib/liblog4cplus.so

all: $(PROG)

run: $(PROG)
	./$(PROG)

$(PROG): $(SOURCES) Makefile
	$(CXX) $(CXXFLAGS) -o $(PROG) $(SOURCES)

libtrader_test.so: $(CTPSETTING)/TraderSpi.cpp
	$(CXX) -g -fPIC -shared -o libtrader_test.so $(CTPSETTING)/TraderSpi.cpp -I$(CTPDIR) -I$(CTPSETTING) -L$(CTPDIR) -lthosttraderapi 

win:
	wine cl $(SOURCES) /MD /nologo /DNDEBUG /O1 /I../.. /Fe$(PROG).exe
	wine $(PROG).exe

clean:
	rm -rf $(PROG) *.exe *.dSYM *.obj *.exp .*o *.lib *.gc*


#include "log4cplus/logger.h"
#include "log4cplus/socketappender.h"
//#include "log4cplus/helpers/loglevel.h"
#include "log4cplus/tstring.h"
#include "log4cplus/helpers/socket.h"
//#include "log4cplus/thread/threads.h"
#include "log4cplus/helpers/sleep.h"
#include "log4cplus/spi/loggingevent.h"
#include "log4cplus/loggingmacros.h"
#include "log4cplus/consoleappender.h"
#include "log4cplus/configurator.h"
//#include "iomanip"
#include <stdlib.h>
#include <string.h>
#include <iostream>

using namespace std;
using namespace log4cplus;
using namespace log4cplus::helpers;

int
main(int argc, char **argv)
{
  // socket server.
    log4cplus::initialize ();
    BasicConfigurator config;
    config.configure();
    log4cplus::helpers::sleep(1);

    // 
    unsigned int port = 9998;//8080;//9998
    ServerSocket serverSocket(port);
    Socket clientsocket = serverSocket.accept();
    
    // read 1st int from socket into buffer.

    while (true) {
      SocketBuffer msgSizeBuffer(sizeof(unsigned int));
      if (!clientsocket.read(msgSizeBuffer)) { //< read from socket into buffer
	return 1;
      }     
      unsigned int msgSize = msgSizeBuffer.readInt(); //< read length of msg.
      cerr<<"msgSize: "<<msgSize<<endl;      
      // read msg
      SocketBuffer buffer(msgSize);
      //      buffer(msgSize);
      if (!clientsocket.read(buffer)) {
	return 2;
      }   

      spi::InternalLoggingEvent event (readFromBuffer(buffer));
      
      Logger logger = Logger::getInstance( event.getLoggerName());
      logger.setLogLevel(TRACE_LOG_LEVEL);
      logger.callAppenders(event);
      //    SharedObjectPtr<Appender> append_0(new ConsoleAppender());
      //    append_0->setName(LOG4CPLUS_TEXT("First"));
    }

    return 0;
}



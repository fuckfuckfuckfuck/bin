// Copyright (c) 2013-2014 Cesanta Software Limited
// $Date: 2014-09-09 17:07:55 UTC $

#include <string.h>
#include <time.h>
#include "mongoose.h"
#include "util.h"

static void push_message(struct mg_server *server, time_t current_time,std::queue<mktDepth>& qmd) {
  struct mg_connection *c;
  char t_buff[100];
  //  char stuff[50];  
  //  int len = sprintf(buf, "%lu", (unsigned long) current_time);

  char* tmp = ctime (&current_time);
  struct tm * timeinfo;
  timeinfo = localtime(&current_time);
  //  Cstring tmp_time = tmp.Format("%H:%M:%S");
  char tmp_time[10];
  strftime(tmp_time, 10, "%H:%M:%S", timeinfo);
  int i = 0;

  mktDepth tmp0(qmd.front());    
  int len = sprintf(t_buff,"%8i %6s %7.1f %8s %8s\n",tmp0.seq_num,(tmp0.depthMktData).TradingDay,(tmp0.depthMktData).LastPrice,(tmp0.depthMktData).UpdateTime,tmp_time);
  int sz = qmd.size();
  char buf[sz][len+1];//**
  printf("sz:%i, len:%i .\n", sz, len);
 
  if (!qmd.empty()) {
    while (!qmd.empty()) {
      mktDepth tmp1(qmd.front());
      int _len = sprintf(buf[i],"%8i %6s %7.1f %8s %8s\n",tmp1.seq_num,(tmp1.depthMktData).TradingDay,(tmp1.depthMktData).LastPrice,(tmp1.depthMktData).UpdateTime,tmp_time);
      //  printf("%i\n", _len);
      ++i;    
      qmd.pop();
    }
    
    // Iterate over all connections, and push current time message to websocket ones.
    for (c = mg_next(server, NULL); c != NULL; c = mg_next(server, c)) {
      if (c->is_websocket) {
	for (int i=0;i!=sz;++i) 
	  mg_websocket_write(c, 1, buf[i], len);
      }
    }
  }
  memset(buf,0,len*i);
  
}


static int send_reply(struct mg_connection *conn) {
  if (conn->is_websocket) {
    // This handler is called for each incoming websocket frame, one or more
    // times for connection lifetime.
    // Echo websocket data back to the client.
    mg_websocket_write(conn, 1, conn->content, conn->content_len);
    return conn->content_len == 4 && !memcmp(conn->content, "exit", 4) ?
      MG_FALSE : MG_TRUE;
  } else {
    mg_send_file(conn, "index.html", NULL);
    return MG_MORE;
  }
}

static int ev_handler(struct mg_connection *conn, enum mg_event ev) {
  switch (ev) {
    case MG_AUTH: return MG_TRUE;
    case MG_REQUEST: return send_reply(conn);
    default: return MG_FALSE;
  }
}


int main(void) {
  std::queue<mktDepth> qmd;
  std::queue<mktDepth> qmd1;
  addScanedMktDepthData("test0.txt",qmd);

  struct mg_server *server = mg_create_server(NULL, ev_handler);
  time_t current_timer = 0, last_timer = time(NULL);

  mg_set_option(server, "listening_port", "8081");

  printf("Started on port %s\n", mg_get_option(server, "listening_port"));
  for (;;) {
    mg_poll_server(server, 100);
    current_timer = time(NULL);
    if (current_timer - last_timer > 0) {
      qmd1 = qmd;
      last_timer = current_timer;
      push_message(server, current_timer, qmd1);
    }
  }

  mg_destroy_server(&server);
  return 0;
}

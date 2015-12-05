// Copyright (c) 2013-2014 Cesanta Software Limited
// $Date: 2014-09-09 17:07:55 UTC $

#include <string.h>
#include <time.h>
#include <signal.h>
#include <stdlib.h>
#include "mongoose.h"
#include <time.h>
#include <unistd.h>

static int cnt;
static int s_signal_received = 0;
static int s_signal_thread = 0;
static struct mg_server *s_server = NULL;

// Data associated with each websocket connection
struct conn_data {
  int room;
};

static void signal_handler(int sig_num) {
  signal(sig_num, signal_handler);  // Reinstantiate signal handler
  s_signal_received = sig_num;
}

static int sse_push(struct mg_connection *conn, enum mg_event ev) {
  if (ev == MG_POLL && conn->is_websocket && NULL != conn->uri) {
    //    mg_websocket_printf(conn, WEBSOCKET_OPCODE_TEXT, "data: %s\r\n\r\n", (const char *) conn->callback_param);
    //    struct mg_connection *c;
    struct conn_data *d = (struct conn_data *) conn->connection_param;
    //
    printf("content %s ; d.room: %i", conn->content, d->room);
    if (conn->content_len == 5 && !memcmp(conn->content, "msg ", 4) &&d->room != 0 && d->room != '?') {
      //      for (c = mg_next(s_server, NULL); c != NULL; c = mg_next(s_server, c)) { 
      //      struct conn_data *d2 = (struct conn_data *) c->connection_param;
      //      if (!c->is_websocket || d2->room != d->room) continue;
      mg_websocket_printf(conn , WEBSOCKET_OPCODE_TEXT, "data: %s\r\n\r\n", (const char *) d);
    }
  }
  return MG_TRUE;
}

static void *sse_pusher_thread_func(void *param) {
  while (s_signal_received == 0) {
    printf("s_signal_thread is %i.\n",s_signal_thread);
    if (s_signal_thread == 1)
      mg_wakeup_server_ex(s_server, sse_push, "%lu %s",
			  (unsigned long) time(NULL), (const char *) param);
    sleep(3);
  }
  return NULL;
}


static void handle_websocket_message(struct mg_connection *conn) {

  mg_websocket_printf(conn, WEBSOCKET_OPCODE_TEXT, "msg tired %i", cnt);
    
}

static int ev_handler(struct mg_connection *conn, enum mg_event ev) {
  switch (ev) {
    case MG_REQUEST:
      if (conn->is_websocket) {
	//	mg_printf_data(conn, "%i\n", "WEBSOCKT");
	printf("//%i REQ_WS\n",++cnt);
	handle_websocket_message(conn);
        return MG_TRUE;
      } else {
	printf("//%i REQ_sendfile\n",++cnt);
	//        mg_send_file(conn, "index.html", NULL);  // Return MG_MORE after!
	mg_printf_data(conn, "request uri is %i\n", conn->uri);

	// following can be improved 
	if (s_signal_thread != 1)
	  s_signal_thread = 1;
	
        return MG_TRUE;
      }
    case MG_WS_CONNECT:
      // New websocket connection. Send connection ID back to the client.
      printf("//%i WS_CONN\n",++cnt);
      conn->connection_param = calloc(1, sizeof(struct conn_data));
      mg_websocket_printf(conn, WEBSOCKET_OPCODE_TEXT, "id %p", conn);
      return MG_FALSE;
    case MG_CLOSE:
      printf("//%i CLOSE\n",++cnt);
      free(conn->connection_param);
      return MG_TRUE;
    case MG_AUTH:
      printf("//%i AUTH\n",++cnt);
      return MG_TRUE;
    default:
      //      cout<<"//"<<++cnt<<" DEFAULT:";
      printf("//%i DEFAULT\n",++cnt);
      return MG_FALSE;
  }
}

int main(void) {
  s_server = mg_create_server(NULL, ev_handler);
  mg_set_option(s_server, "listening_port", "8080");

  signal(SIGTERM, signal_handler);
  signal(SIGINT, signal_handler);
  cnt = 0;

  //  mg_start_thread(sse_pusher_thread_func, (void *) "sse_pusher_thread_2");
  mg_start_thread(sse_pusher_thread_func, (void *) "fuk_thread");

  printf("Started on port %s\n", mg_get_option(s_server, "listening_port"));
  while (s_signal_received == 0) {
    printf("1st:  \n");
    mg_poll_server(s_server, 1000);
    printf("2nd:  \n");
  }
  mg_destroy_server(&s_server);
  return 0;
}

#include "common.h"

#include <byteswap.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/types.h>
#include <string.h>

#define PACKET_OUT_OF_ORDER_THRESHOLD   10000

double   rate		   = 195312.5;
unsigned subbands	   = 61;
unsigned samples_per_frame = 16;
unsigned bits_per_sample   = 16;

char	 name[64];
unsigned message_size;
int	 sk;
unsigned packets_received, missed, out_of_order, errors, bad_timestamps;
unsigned clock_speed;
unsigned long long expected_time;
unsigned long long rec_sequence_nr = 0;
char *socket_arg;

char *output_file_name() {
  char *rv = malloc(sizeof(char) * (2 + strlen(socket_arg) + 4 + 1));
#if defined HOST_C
  strcat(rv, "C");
#else
  strcat(rv, "B");
#endif
  strcat(rv, "_");
  strcat(rv, socket_arg);
  strcat(rv, ".txt");
  return rv;
}

void clear_output_file() {
  char *name = output_file_name();
  FILE *f = fopen(name, "w");
  fclose(f);
  free(name);
}

int record_traffic_starvation() {
  if (rec_sequence_nr == 0) {
    return;
  }

  char *name = output_file_name();
  FILE *f = fopen(name, "ab+");
  int rv = fprintf(f, "%llu\n", rec_sequence_nr);
  fclose(f);
  free(name);

  rec_sequence_nr = 0;
  return rv;
}

int receive_packet()
{
  char packet[9000];
  size_t bytes_received;
  struct timeval time_start_read;
  gettimeofday(&time_start_read, 0);

  for (bytes_received = 0; bytes_received < message_size;) {
    ssize_t retval = read(sk, packet + bytes_received, message_size - bytes_received);

    if (retval < 0) {
      ++ errors;
      perror("read");
      sleep(1);
    } else if (retval == 0) {
      return 0;
    } else {
      bytes_received += retval;
    }
  }

  struct timeval time_done_read;
  gettimeofday(&time_done_read, 0);

  ++ packets_received;

#if defined __BIG_ENDIAN__
  unsigned long long sequence_number = __bswap_64(* (unsigned long long *) (packet));
  unsigned seconds  = __bswap_32(* (int *) (packet +  8));
  unsigned fraction = __bswap_32(* (int *) (packet + 12));
#else
  unsigned long long sequence_number = * (unsigned long long *) (packet);
  unsigned seconds  = * (int *) (packet +  8);
  unsigned fraction = * (int *) (packet + 12);
#endif

  unsigned long long start_read = time_start_read.tv_sec * 1000000ULL + time_start_read.tv_usec;
  unsigned long long done_read = time_done_read.tv_sec * 1000000ULL + time_done_read.tv_usec;

  if (((done_read - start_read) / 1e6) >= 1.8) {
    record_traffic_starvation();
  }

  if (seconds == 0xFFFFFFFF) {
    ++ bad_timestamps;
  } else {
    unsigned long long time = ((unsigned long long) seconds * clock_speed + 512) / 1024 + fraction;

    if (expected_time != time && expected_time != 0)
      missed += (time - expected_time) / samples_per_frame;

    if (time < expected_time)
      ++ out_of_order;

    expected_time = time + samples_per_frame;
  }

  if (rec_sequence_nr == 0) {
    rec_sequence_nr = sequence_number;
  } else {
    #if defined HOST_C
     // Assign smaller one, unless overflow has occurred
      if (sequence_number < rec_sequence_nr) {
        unsigned long long diff = rec_sequence_nr - sequence_number;
        if (diff < PACKET_OUT_OF_ORDER_THRESHOLD) {
          rec_sequence_nr = sequence_number;
        }
      }
    #else
      if (sequence_number > rec_sequence_nr) {
        unsigned long long diff = sequence_number - rec_sequence_nr;
        if (diff < PACKET_OUT_OF_ORDER_THRESHOLD) {
          rec_sequence_nr = sequence_number;
        }
      } else if (sequence_number < rec_sequence_nr) {
        unsigned long long diff = rec_sequence_nr - sequence_number;
        if (diff > PACKET_OUT_OF_ORDER_THRESHOLD) {
          rec_sequence_nr = sequence_number; // Overflow
        }
      }
    #endif
  }

  return 1;
}


void parse_args(int argc, char **argv)
{
  if (argc == 1) {
    fprintf(stderr, "usage: %s [-f frequency (default 195312.5)] [-s subbands (default 61)] [-t times_per_frame (default 16)] [udp:ip:port | tcp:ip:port | file:name | null: | - ] ... \n", argv[0]);
    exit(1);
  }

  int arg;

  for (arg = 1; arg < argc && argv[arg][0] == '-'; arg ++)
    switch (argv[arg][1]) {
      case 'a': set_affinity(argument(&arg, argv));
		break;

      case 'b': bits_per_sample = atoi(argument(&arg, argv));
		break;

      case 'f': rate = atof(argument(&arg, argv));
		break;

      case 'r': set_real_time_priority();
		break;

      case 's': subbands = atoi(argument(&arg, argv));
		break;

      case 't': samples_per_frame = atoi(argument(&arg, argv));
		break;

      default : fprintf(stderr, "unrecognized option '%c'\n", argv[arg][1]);
		exit(1);
    }

  if (arg == argc)
    exit(0);

  enum proto proto;
  socket_arg = strchr(argv[arg] + 4, ':') + 1; // first 4 chars are 'udp:'
  sk = create_fd(argv[arg], 0, &proto, name, sizeof name);
}


void print_message()
{
  fprintf(stderr, "received %u packets from %s", packets_received, name);

  if (missed > 0)
    fprintf(stderr, ", missed = %u", missed);

  if (out_of_order > 0)
    fprintf(stderr, ", out of order = %u", out_of_order);

  if (errors > 0)
    fprintf(stderr, ", read errors = %u", errors);

  if (bad_timestamps > 0)
    fprintf(stderr, ", bad timestamps = %u", bad_timestamps);

  fputc('\n', stderr);

  packets_received = missed = out_of_order = errors = bad_timestamps = 0;
}


void print_machine_message() 
{
  fprintf(stderr, "%u %u %u %u %u\n", packets_received, missed, out_of_order, errors, bad_timestamps);

  packets_received = missed = out_of_order = errors = bad_timestamps = 0;
}

int main(int argc, char **argv)
{
  if_BGP_set_default_affinity();
  setvbuf(stderr, 0, _IOLBF, 0);
  parse_args(argc, argv);
  clear_output_file();

  message_size = 16 + samples_per_frame * subbands * bits_per_sample / 2;
  clock_speed  = (unsigned) (1024 * rate);

  time_t last_time;

  while (receive_packet()) {
    time_t current_wtime = time(0);

    if (current_wtime != last_time) {
      last_time = current_wtime;
      /* print_message(); */
      print_machine_message();
    }
  }

  print_machine_message();
  /* print_message(); */
  return 0;
}

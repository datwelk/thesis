## Usage

#### Traffic redirection: latency
Node A:
<pre>
$ gcc -pthread common.c generator.c -o generator -lrt
$ ./generator -s 10 udp:10.0.0.2:50000 
</pre>
Node C:
<pre>
$ python controller.py -n 1000
</pre>

#### Traffic redirection: packet loss
Node B:
<pre>
$ gcc analyzer.c common.c -o analyzer
$ ./analyzer -s 10 udp:10.0.0.2:50000
</pre>
Node C: 
<pre>
$ gcc -DHOST_C analyzer.c common.c -o analyzer
$ ./analyzer -s 10 udp:10.0.0.2:50000
</pre>
Node A:
<pre>
$ gcc -pthread common.c generator.c -o generator -lrt
$ ./generator -s 10 udp:10.0.0.2:50000 
</pre>
Node C4:
<pre>
$ java -jar target/floodlight.jar
</pre>
Node C1:
<pre>
$ python controller.py -n 1001
</pre>
Substitute `analyzer.c` with `analyzer_multistream.c` or `analyzer_close_up.c` or `analyzer_second_lowest.c` to obtain different results (see paper).
#### Traffic duplication
Use either of `passthrough` or `duplicate` methods within the `start` method of `controller.py` to conduct experiments with the respective flow: either simply connect A to B, or duplicate to C and D as well. (Comment the one out that's not needed)
Node A:
<pre>
$ gcc -pthread common.c generator.c -o generator -lrt
$ gcc -shared -lrt -fPIC -I/usr/include/python2.7 -lpython2.7 -o cutils.so cutils.c
$ python server.py
</pre>
Node B:
<pre>
$ gcc analyzer.c common.c -o analyzer
./analyzer -s 10 udp:10.0.0.2:50000
</pre>
Node C4:
<pre>
$ java -jar target/floodlight.jar
</pre>
Node C1:
<pre>
$ python controller.py -n 1001
</pre>
For multistream tests, make sure to use sockets 50000-50006 when launching the analyzer instances on B.

## Usage

#### Traffic duplication
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

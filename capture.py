import mjpegc
import time

import sys
sys.path.append("../brb/src/")
import brb

client = mjpegc.MJPEGClient("http://camera2/videostream.cgi")

buf = brb.BRBWriter("/tmp/camera2/", 1000 * 1024 * 1024, 10)

while True:
    data = client.frame()
    print len(data)
    buf.write(time.time(), data)

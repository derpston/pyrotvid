import sys
sys.path.append("../brb/src/")
import brb
import time

buf = brb.BRBReader("/mnt/omg/camera/", 100 * 1024 * 1024, 5)
print buf

for index, (ts, frame) in enumerate(buf):
   print ts, len(frame),
   print time.ctime(ts)
   open("frames/frame-%d.jpg" % index, "w").write(frame)


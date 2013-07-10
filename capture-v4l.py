import v4l2capture
import sys
import select
import Image
import StringIO
import time

import sys
sys.path.append("../brb/src/")
import brb

buf = brb.BRBWriter("/var/tmp/camera/", 1000 * 1024 * 1024, 10)

video = v4l2capture.Video_device(sys.argv[1])

# Suggest an image size to the device. The device may choose and
# return another size if it doesn't support the suggested one.
size_x, size_y = video.set_format(320, 240)
#size_x, size_y = video.set_format(640, 480)

# Create a buffer to store image data in. This must be done before
# calling 'start' if v4l2capture is compiled with libv4l2. Otherwise
# raises IOError.
video.create_buffers(1)

# Send the buffer to the device. Some devices require this to be done
# before calling 'start'.
video.queue_all_buffers()

# Start the device. This lights the LED if it's a camera that has one.
video.start()

count = 0

while True:
   print "waiting for frame",
   select.select((video,), (), ())

   image_data = video.read_and_queue()

   print "%d bytes" % len(image_data)

   image = Image.fromstring("RGB", (size_x, size_y), image_data)
   jpg_fh = StringIO.StringIO()
   image.save(jpg_fh, "jpeg")

   buf.write(time.time(), jpg_fh.getvalue())

   count += 1
   time.sleep(0.1)



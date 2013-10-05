import web
import json

import sys
sys.path.append("../brb/src/")
import brb

# gif export
import images2gif
import PIL
import StringIO

videos = []

buf = brb.BRBReader("/mnt/omg/camera/", 100 * 1024 * 1024, 0x1e)

for blockid, size, first, last in buf._blocks():
   # Start and end timestamps.
   videos.append({'block': blockid, 'start': first[2], 'end': last[2], 'size': size})

urls = (
    '/', 'index',
    '/video/', 'video',
    '/video/([0-9]+)/([0-9]+.[0-9]+)', 'frame',
    '/gif/([0-9]+)/([0-9]+.[0-9]+)/([0-9]+)/([0-9]+.[0-9]+)', 'gif'
)

app = web.application(urls, globals())

class index:
    def GET(self):
        return open("index.html").read()

class video:
    def GET(self):
        result = []
        for video in videos:
            result.append({'start': video['start'], 'end': video['end'], 'size': video['size']})
        return json.dumps(result)

cached_frame = None

class frame:
    def HEAD(self, video, timestamp_wanted):
        getdata = web.input()
        global cached_frame
        video = int(video)
        timestamp_wanted = float(timestamp_wanted)

        direction = getdata.get("direction", "next")

        if direction == "next":
            direction = 1
        elif direction == "prev":
            direction = -1

        (timestamp, data) = buf.readblock(video, timestamp_wanted, direction = direction)
        cached_frame = (video, timestamp, data)
        url = "/video/%d/%f" % (video, timestamp)
        web.header("Location", url)
        web.header("X-timestamp", timestamp)
        
    def GET(self, video, timestamp_wanted):
        global cached_frame
        video = int(video)
        timestamp_wanted = float(timestamp_wanted)

        web.header("Content-Type", "image/jpeg")

        try:
            cached_video, cached_timestamp, cached_data = cached_frame
            assert cached_video == video
            assert cached_timestamp == timestamp_wanted
            data = cached_data
        except (TypeError, AssertionError), ex:
            (timestamp, data) = buf.readblock(video, timestamp_wanted)

            if timestamp_wanted != timestamp:
                web.ctx.status = "404 Not Found"
                return "404 Not Found"

        return data


class gif:
    def GET(self, start_video, start_timestamp, end_video, end_timestamp):
        assert start_video == end_video, "Crossing segments not supported, sorey."
        start_video = int(start_video)
        start_timestamp = float(start_timestamp)
        end_video = int(end_video)
        end_timestamp = float(end_timestamp)

        frames = []
        closest_timestamp, _ = buf.readblock(start_video, start_timestamp)
        for block, offset, timestamp, data in buf._iter(start_video):
            if block == start_video and timestamp > start_timestamp and timestamp < end_timestamp:
                img = PIL.Image.open(StringIO.StringIO(data))
                frames.append(img)
      
        print "Building gif with %d frames." % len(frames)
        images2gif.writeGif("exported.gif", frames, duration = 0.1)
        return open("exported.gif").read()

if __name__ == "__main__":
    app.run()



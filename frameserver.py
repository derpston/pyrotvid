import web
import json

import sys
sys.path.append("../brb/src/")
import brb

videos = []

buf = brb.BRBReader("/mnt/omg/camera/", 100 * 1024 * 1024, 0x1b)

for blockid, size, first, last in buf._blocks():
   # Start and end timestamps.
   videos.append({'block': blockid, 'start': first[2], 'end': last[2], 'size': size})

urls = (
    '/', 'index',
    '/video/', 'video',
    '/video/([0-9]+)/([0-9]+.[0-9]+)', 'frame'
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
        global cached_frame
        video = int(video)
        timestamp_wanted = float(timestamp_wanted)

        (timestamp, data) = buf.readblock(video, timestamp_wanted)
        cached_frame = (video, timestamp, data)
        url = "/video/%d/%f" % (video, timestamp)
        web.header("Location", url)
        
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

if __name__ == "__main__":
    app.run()



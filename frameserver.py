import web
import json

import sys
sys.path.append("../brb/src/")
import brb

videos = []

buf = brb.BRBReader(sys.argv[1], 100 * 1024 * 1024, 5)

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

class frame:
    def GET(self, video, timestamp_wanted):
        video = int(video)
        timestamp_wanted = float(timestamp_wanted)
        (timestamp, data) = buf.readblock(video, timestamp_wanted)
        web.header("Content-Type", "image/jpeg")
        web.header("X-Timestamp", timestamp)
        return data

if __name__ == "__main__":
    app.run()



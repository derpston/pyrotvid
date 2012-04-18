import web
import json

import sys
sys.path.append("../brb/src/")
import brb

videos = []

buf = brb.BRBReader("/tmp/camera2/", 100 * 1024 * 1024, 10)
#buf.read(1333326353.8913672)
start = buf.read(0)[0]
end = buf.read(2**32)[0]
print start, end

videos.append({'reader': buf, 'start': start, 'end': end})

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
            result.append({'start': video['start'], 'end': video['end']})
        return json.dumps(result)

class frame:
    def GET(self, video, timestamp_wanted):
        video = int(video)
        timestamp_wanted = float(timestamp_wanted)
        (timestamp, data) = videos[video]['reader'].read(timestamp_wanted)
        web.header("Content-Type", "image/jpeg")
        web.header("X-Timestamp", timestamp)
        return data

if __name__ == "__main__":
    app.run()



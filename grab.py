import requests
import yt_dlp

urls = open('./about.html', 'r').read().split('\n')
titles = []
ydl_opts = {"quiet": True, "no_warnings": True, "cookiesfrombrowser": ("firefox",),}
ydl = yt_dlp.YoutubeDL(ydl_opts)

for idx, i in enumerate(urls):
    if 'https' in i and i[-1] == ',': 
        yt = i.split('\"')[1]
        try:
            title = ydl.extract_info(yt, download=False, process=False).get("title")
            print(yt, title)
            if title in titles: print(f"[!] dupe {yt=}")
            titles.append(title)
        except Exception as e:
            print(yt, e)
            pass

print(titles)

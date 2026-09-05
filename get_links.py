import urllib.request
import urllib.parse
import re
import json

def get_video_links():
    links = []
    for ep in range(1, 25):
        query = f"Muse India [Hindi Dub] I Was Reincarnated as the 7th Prince - Episode {ep:02d}"
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            html = urllib.request.urlopen(req).read().decode('utf-8')
            # Find all video IDs
            video_ids = re.findall(r"watch\?v=(\S{11})", html)
            if video_ids:
                video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                links.append(f"Episode {ep:02d}: {video_url}")
                print(f"Found Ep {ep:02d}: {video_url}")
            else:
                links.append(f"Episode {ep:02d}: Not found")
                print(f"Ep {ep:02d} not found")
        except Exception as e:
            print(f"Error for Ep {ep:02d}: {e}")
            
    with open("yt copy links.txt.txt", "w", encoding="utf-8") as f:
        for link in links:
            f.write(link + "\n")
            
if __name__ == "__main__":
    get_video_links()

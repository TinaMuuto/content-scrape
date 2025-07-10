import requests

API_TOKEN = "M2AVWCF-BNJ4RVN-N06J4AV-30BR8RF"

def get_screenshot(url):
    api_url = "https://shot.screenshotapi.net/screenshot"
    params = {
        "token": API_TOKEN,
        "url": url,
        "output": "image",
        "file_type": "png",
        "wait_for_event": "load",
        "width": 1280,
        "height": 900
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        filename = url.replace("https://", "").replace("http://", "").replace("/", "_").replace("?", "_") + ".png"
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    else:
        print("Screenshot API error:", response.status_code, response.text)
        return None

"""
OPTIONAL: bakes natural (neural) character voices into space_junk_episode.html.
After this, the voices sound the same on every computer and the
"Play & record video" button records them too.

  pip install edge-tts
  python make_voices.py

Needs an internet connection. Run it again after you edit any line.
"""
import asyncio, base64, json, re, sys, tempfile, os
from pathlib import Path

try:
    import edge_tts
except ImportError:
    sys.exit("Please run:  pip install edge-tts")

HTML = Path(__file__).with_name("space_junk_episode.html")

# voice, speed, pitch for each character (list more with:  edge-tts --list-voices)
VOICES = {
    "narrator": ("en-US-AvaNeural", "-8%", "+0Hz"),      # warm, friendly teacher
    "spark":    ("en-US-AnaNeural", "+6%", "+0Hz"),
    "moony":    ("en-GB-LibbyNeural", "-6%", "+8Hz"),
    "marsy":    ("en-AU-NatashaNeural", "+6%", "+18Hz"),
    "sib1":     ("en-US-GuyNeural", "+12%", "+12Hz"),
    "sib2":     ("en-US-ChristopherNeural", "+12%", "+6Hz"),
    "sib3":     ("en-US-AriaNeural", "+12%", "+12Hz"),
    "sci1":     ("en-US-AndrewNeural", "-3%", "+0Hz"),   # calm, clever, human
    "sci2":     ("en-US-EmmaNeural", "-3%", "+0Hz"),
    "sci3":     ("en-GB-RyanNeural", "-3%", "+0Hz"),
    "craft":    ("en-US-RogerNeural", "+0%", "-8Hz"),
    "craft1":   ("en-US-SteffanNeural", "+8%", "+0Hz"),
    "craft2":   ("en-IE-EmilyNeural", "+10%", "+0Hz"),
    "craft3":   ("en-CA-LiamNeural", "+4%", "+0Hz"),
    "astro":    ("en-US-BrianNeural", "+6%", "+0Hz"),
    "scis":     ("en-US-AndrewNeural", "+0%", "+0Hz"),
    "both":     ("en-AU-NatashaNeural", "+6%", "+18Hz"),
    "all":      ("en-US-AnaNeural", "+0%", "+0Hz"),
}


def mp3_duration(data):
    # edge-tts makes 48 kbit/s mono MP3 by default
    return round(len(data) * 8 / 48000, 2)


async def main():
    html = HTML.read_text(encoding="utf-8")
    m = re.search(r"const LINES = (\[.*?\n\]);", html, re.S)
    lines = json.loads(m.group(1))
    audio = {}
    for i, l in enumerate(lines, 1):
        voice, rate, pitch = VOICES.get(l["who"], VOICES["narrator"])
        text = l.get("say") or l["text"]
        print(f"[{i}/{len(lines)}] {l['who']}: {text[:60]}")
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "a.mp3")
            await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(f)
            data = Path(f).read_bytes()
        audio[l["id"]] = {"text": l["text"], "dur": mp3_duration(data), "b64": base64.b64encode(data).decode()}
    block = "/*AUDIO*/const AUDIO=" + json.dumps(audio) + ";/*END_AUDIO*/"
    html = re.sub(r"/\*AUDIO\*/.*?/\*END_AUDIO\*/", lambda _: block, html, flags=re.S)
    HTML.write_text(html, encoding="utf-8")
    print("Done! Natural voices are now built into", HTML.name)

asyncio.run(main())

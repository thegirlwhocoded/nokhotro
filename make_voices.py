"""
OPTIONAL: bakes natural (neural) character voices into index.html.
After this, the voices sound the same in every browser and the
"Play & record video" button records them too.

  pip3 install edge-tts
  python3 make_voices.py

Needs an internet connection. Run it again after you edit any line.
"""
import asyncio, base64, json, re, sys, tempfile, os
from pathlib import Path

try:
    import edge_tts
except ImportError:
    sys.exit("Please run:  pip3 install edge-tts")

HERE = Path(__file__).resolve().parent
os.chdir(HERE)
# finds the episode file even if your browser renamed it, e.g. "index (2).html"
found = [p for p in HERE.glob("*.html") if "const LINES = [" in p.read_text(encoding="utf-8", errors="ignore")]
if not found:
    sys.exit("Put make_voices.py in the same folder as the episode's .html file, then run it again.")
HTML = max(found, key=lambda p: p.stat().st_mtime)
print("Adding voices to:", HTML.name)

# voice, speed, pitch for each character - same voices as chosen in the Voices panel in Edge
VOICES = {
    "narrator": ("en-US-AvaMultilingualNeural", "-8%", "+0Hz"),
    "sci1":     ("en-US-AndrewMultilingualNeural", "-3%", "+0Hz"),
    "sci2":     ("en-US-EmmaMultilingualNeural", "-3%", "+0Hz"),
    "sci3":     ("en-GB-RyanNeural", "-3%", "+0Hz"),
    "spark":    ("en-US-AnaNeural", "+5%", "+0Hz"),
    "moony":    ("en-IN-NeerjaNeural", "-5%", "+0Hz"),
    "marsy":    ("en-KE-AsiliaNeural", "+5%", "+0Hz"),
    "astro":    ("en-US-BrianMultilingualNeural", "+5%", "+0Hz"),
    "sib1":     ("en-ZA-LeahNeural", "+10%", "+0Hz"),
    "sib2":     ("en-US-ChristopherNeural", "+10%", "+0Hz"),
    "sib3":     ("en-US-AriaNeural", "+10%", "+0Hz"),
    "craft":    ("en-US-RogerNeural", "+0%", "+0Hz"),
    "craft1":   ("en-US-SteffanNeural", "+8%", "+0Hz"),
    "craft2":   ("en-IE-EmilyNeural", "+10%", "+0Hz"),
    "craft3":   ("en-AU-WilliamMultilingualNeural", "+4%", "+0Hz"),
    "scis":     ("en-US-AndrewMultilingualNeural", "+0%", "+0Hz"),
    "both":     ("en-KE-AsiliaNeural", "+5%", "+0Hz"),
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
            try:
                await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(f)
            except Exception:
                print("   (voice", voice, "not available, using en-US-AvaNeural)")
                await edge_tts.Communicate(text, "en-US-AvaNeural", rate=rate).save(f)
            data = Path(f).read_bytes()
        audio[l["id"]] = {"text": l["text"], "dur": mp3_duration(data), "b64": base64.b64encode(data).decode()}
    block = "/*AUDIO*/const AUDIO=" + json.dumps(audio) + ";/*END_AUDIO*/"
    html = re.sub(r"/\*AUDIO\*/.*?/\*END_AUDIO\*/", lambda _: block, html, flags=re.S)
    HTML.write_text(html, encoding="utf-8")
    print("Done! Natural voices are now built into", HTML.name)
    if HTML.name != "index.html":
        print("Tip: rename it to index.html before uploading it to GitHub.")

asyncio.run(main())


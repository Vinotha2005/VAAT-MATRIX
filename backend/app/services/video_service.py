import os
import re
import subprocess
from urllib.parse import quote_plus
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict

try:
    import spacy
except Exception:
    spacy = None

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

STOP_WORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "have", "been", "will",
    "about", "their", "these", "those", "what", "when", "where", "which", "while", "than",
    "can", "also", "your", "using", "used", "more", "through", "study", "chapter",
    "topic", "topics", "pdf", "document", "lesson", "lecture", "file", "dummy", "sample"
}

_SPACY_NLP = None


def _get_spacy_nlp():
    global _SPACY_NLP
    if spacy is None:
        return None
    if _SPACY_NLP is not None:
        return _SPACY_NLP
    try:
        _SPACY_NLP = spacy.load("en_core_web_sm")
    except Exception:
        return None
    return _SPACY_NLP


def _extract_keywords(text: str, limit: int = 6) -> List[str]:
    nlp = _get_spacy_nlp()
    if nlp is not None:
        doc = nlp(text)
        candidates: List[str] = []
        for chunk in doc.noun_chunks:
            phrase = " ".join(token.lemma_.lower() for token in chunk if token.is_alpha and not token.is_stop)
            if phrase and phrase not in candidates:
                candidates.append(phrase)
        for ent in doc.ents:
            phrase = ent.text.lower().strip()
            if phrase and phrase not in candidates:
                candidates.append(phrase)
        if candidates:
            return candidates[:limit]

    normalized = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    tokens = [token for token in normalized.split() if len(token) > 2]
    filtered = [token for token in tokens if token not in STOP_WORDS]
    counts: Dict[str, int] = {}
    for token in filtered:
        counts[token] = counts.get(token, 0) + 1

    phrase_counts: Dict[str, int] = {}
    for idx in range(len(filtered) - 1):
        phrase = f"{filtered[idx]} {filtered[idx + 1]}"
        phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

    ranked_phrases = [phrase for phrase, _ in sorted(phrase_counts.items(), key=lambda item: (-item[1], item[0]))]
    ranked_words = [token for token, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]

    results: List[str] = []
    for phrase in ranked_phrases:
        if phrase not in results:
            results.append(phrase)
        if len(results) >= limit:
            return results

    for word in ranked_words:
        if word not in results:
            results.append(word)
        if len(results) >= limit:
            break

    return results


def _build_youtube_search_url(keywords: List[str]) -> str:
    query = " ".join(keywords[:4])
    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"


def recommend_youtube_videos(text: str, limit: int = 3) -> List[Dict[str, str]]:
    """Return a short list of YouTube search links based on the main topics in the text."""
    keywords = _extract_keywords(text)
    if not keywords:
        return [{
            "title": "Study topic videos",
            "url": "https://www.youtube.com/results?search_query=study+topic+explained",
            "reason": "A good starting point for general revision videos.",
        }]

    recommendations = []
    for idx, keyword in enumerate(keywords):
        if idx >= limit:
            break
        query = _build_youtube_search_url(keywords[: idx + 1])
        title_prefix = keyword.title()
        if idx == 0 and any(term.startswith("python") for term in keywords):
            title_prefix = "Python"
        elif idx == 0 and any(term.startswith("machine learning") for term in keywords):
            title_prefix = "Machine Learning"
        recommendations.append({
            "title": f"{title_prefix} explained",
            "url": query,
            "reason": f"Matches the main topic term '{keyword}' from the document.",
        })

    if not recommendations:
        recommendations = [{
            "title": "Study topic videos",
            "url": "https://www.youtube.com/results?search_query=study+topic+explained",
            "reason": "A good starting point for general revision videos.",
        }]

    return recommendations


def _load_font(size: int = 48):
    possible = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for p in possible:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_slide_images(text: str, out_dir: str, width: int = 1280, height: int = 720) -> List[str]:
    """
    Splits text into paragraphs and generates PNG slides for each paragraph.
    Returns list of slide file paths.
    """
    os.makedirs(out_dir, exist_ok=True)
    paras = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not paras:
        paras = [text[:1000]]
    font_title = _load_font(56)
    font_body = _load_font(36)
    slide_paths = []
    for idx, p in enumerate(paras, start=1):
        img = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        # title: first line or first 60 chars
        title = p.split('\n')[0][:80]
        draw.text((60, 60), title, font=font_title, fill=(10, 25, 47))
        # body: wrap text
        body = '\n'.join(_wrap_text(p, font_body, width - 120))
        draw.text((60, 160), body, font=font_body, fill=(30, 30, 30))
        out_path = os.path.join(out_dir, f"slide_{idx:03}.png")
        img.save(out_path)
        slide_paths.append(out_path)
    return slide_paths


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    words = text.split()
    lines = []
    cur = []
    # use ImageDraw to measure text width for compatibility with Pillow versions
    dummy_img = Image.new('RGB', (10, 10))
    draw = ImageDraw.Draw(dummy_img)
    for w in words:
        cur.append(w)
        test = ' '.join(cur)
        try:
            size = draw.textlength(test, font=font)
        except Exception:
            bbox = draw.textbbox((0, 0), test, font=font)
            size = bbox[2] - bbox[0]
        if size > max_width:
            # back out
            cur.pop()
            lines.append(' '.join(cur))
            cur = [w]
    if cur:
        lines.append(' '.join(cur))
    return lines


def _get_audio_duration(audio_path: str) -> float:
    # prefer local ffprobe if downloaded in tools/ffmpeg/bin
    tools_dir = os.path.join(os.path.dirname(__file__), "..", "..", "tools", "ffmpeg", "bin")
    ffprobe_bin = os.path.join(tools_dir, "ffprobe.exe") if os.name == 'nt' else os.path.join(tools_dir, "ffprobe")
    probe_cmd = ffprobe_bin if os.path.exists(ffprobe_bin) else "ffprobe"
    cmd = [probe_cmd, "-v", "error", "-show_entries", "format=duration", "-of",
           "default=noprint_wrappers=1:nokey=1", audio_path]
    out = subprocess.check_output(cmd).decode().strip()
    try:
        return float(out)
    except Exception:
        return 0.0


def create_video_from_slides(slide_paths: List[str], audio_path: str, srt_path: str, output_path: str) -> str:
    """
    Compose slides into a single MP4 synced to audio duration and burn subtitles.
    """
    if not slide_paths:
        raise ValueError("No slides provided")
    duration = _get_audio_duration(audio_path) or 10.0
    per_slide = max(1.0, duration / len(slide_paths))
    tmp_videos = []
    for idx, slide in enumerate(slide_paths, start=1):
        tmp = f"{slide}.mp4"
        # prefer local ffmpeg binary if present
        tools_dir = os.path.join(os.path.dirname(__file__), "..", "..", "tools", "ffmpeg", "bin")
        ffmpeg_bin = os.path.join(tools_dir, "ffmpeg.exe") if os.name == 'nt' else os.path.join(tools_dir, "ffmpeg")
        ffmpeg_cmd = ffmpeg_bin if os.path.exists(ffmpeg_bin) else "ffmpeg"
        cmd = [
            ffmpeg_cmd, "-y", "-loop", "1", "-i", slide,
            "-c:v", "libx264", "-t", str(per_slide), "-pix_fmt", "yuv420p",
            "-vf", f"scale=1280:720,format=yuv420p", tmp
        ]
        subprocess.check_call(cmd)
        tmp_videos.append(tmp)
    # create concat list
    list_file = os.path.join(os.path.dirname(output_path), "concat_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for v in tmp_videos:
            f.write(f"file '{os.path.abspath(v)}'\n")
    concat_video = os.path.join(os.path.dirname(output_path), "concat.mp4")
    cmd_concat = [ffmpeg_cmd, "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", concat_video]
    subprocess.check_call(cmd_concat)
    # add audio and subtitles
    cmd_final = [
        ffmpeg_cmd, "-y", "-i", concat_video, "-i", audio_path,
        "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
        "-vf", f"subtitles={srt_path}", "-shortest", output_path
    ]
    subprocess.check_call(cmd_final)
    # cleanup tmp
    try:
        os.remove(list_file)
        os.remove(concat_video)
        for v in tmp_videos:
            os.remove(v)
    except Exception:
        pass
    return output_path

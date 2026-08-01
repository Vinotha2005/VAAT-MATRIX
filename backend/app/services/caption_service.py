from typing import List


def generate_srt_from_text(text: str, wpm: int = 130) -> str:
    """
    Very simple srt generator: splits text into chunks based on words-per-minute and assigns timestamps sequentially.
    """
    words = text.split()
    words_per_chunk = int(wpm * 5 / 60) or 20
    chunks = [" ".join(words[i:i+words_per_chunk]) for i in range(0, len(words), words_per_chunk)]
    srt_lines = []
    current_seconds = 0
    for idx, ch in enumerate(chunks, start=1):
        start = current_seconds
        duration = max(3, int(len(ch.split()) / (wpm/60)))
        end = start + duration
        def sec_to_ts(s):
            h = s // 3600
            m = (s % 3600) // 60
            s2 = s % 60
            return f"{h:02}:{m:02}:{s2:02},000"
        srt_lines.append(str(idx))
        srt_lines.append(f"{sec_to_ts(start)} --> {sec_to_ts(end)}")
        srt_lines.append(ch)
        srt_lines.append("")
        current_seconds = end
    return "\n".join(srt_lines)

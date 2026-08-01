from app.services.ai_service import summarize_text
from app.services.video_service import recommend_youtube_videos


def test_recommends_youtube_links_for_topic_text():
    recommendations = recommend_youtube_videos("This lesson explains Python variables, loops, and functions")

    assert recommendations
    assert any(item["title"].lower().startswith("python") for item in recommendations)
    assert recommendations[0]["url"].startswith("https://www.youtube.com/")


def test_summarizes_pdf_text_into_short_summary():
    summary = summarize_text("Artificial intelligence is transforming healthcare by improving diagnosis, treatment planning, and patient monitoring.")

    assert summary["summary"].strip()
    assert len(summary["summary"].split()) >= 10
    assert not summary["summary"].endswith("...")

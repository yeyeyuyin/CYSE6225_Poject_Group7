"""Seeds a few sample videos so the frontend has something to show while the
team builds. Run after create_tables.py, from the backend/ dir with venv active:

    python3 scripts/seed_data.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import video as video_model

SAMPLE_VIDEOS = [
    {
        "title": "Big Buck Bunny",
        "description": "A giant rabbit deals with three bullying rodents. Open-source animated short, great for testing embeds.",
        "tags": ["Comedy"],
        "sources": [
            {"name": "Source A - YouTube", "url": "https://www.youtube.com/watch?v=YE7VzlLtp-4"},
        ],
        "thumbnail_url": "https://placehold.co/400x225?text=Big+Buck+Bunny",
    },
    {
        "title": "Sintel",
        "description": "A lone girl fights to save a baby dragon in this Blender Foundation short film.",
        "tags": ["Drama", "Sci-Fi"],
        "sources": [
            {"name": "Source A - YouTube", "url": "https://www.youtube.com/watch?v=eRsGyueVLvQ"},
            {"name": "Source B - Vimeo", "url": "https://vimeo.com/95322361"},
        ],
        "thumbnail_url": "https://placehold.co/400x225?text=Sintel",
    },
    {
        "title": "Tears of Steel",
        "description": "A group of warriors and scientists gather to stage a crucial event in a war against robots.",
        "tags": ["Sci-Fi", "Action"],
        "sources": [
            {"name": "Source A - YouTube", "url": "https://www.youtube.com/watch?v=R6MlUcmOul8"},
        ],
        "thumbnail_url": "https://placehold.co/400x225?text=Tears+of+Steel",
    },
]


def main():
    for v in SAMPLE_VIDEOS:
        created = video_model.create_video(
            title=v["title"],
            description=v["description"],
            tags=v["tags"],
            sources=v["sources"],
            thumbnail_url=v["thumbnail_url"],
        )
        print(f"Created: {created['title']} ({created['video_id']})")


if __name__ == "__main__":
    main()

import anvil.server
import requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

YOUTUBE_API_KEY = 'AIzaSyAhj_M7HmHGlsEU8WK-NmOAKbGbhxs_ua8'  # TODO: Move to secrets

@anvil.server.callable
def search_youtube_videos(query, max_results=10):
    """Search YouTube for videos matching the query."""
    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'key': YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    videos = []
    for item in data.get('items', []):
        videos.append({
            'id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'thumbnail': item['snippet']['thumbnails']['medium']['url'],
            'channel': item['snippet']['channelTitle'],
            'published_at': item['snippet']['publishedAt']
        })
    return videos

@anvil.server.callable
def get_video_details_and_transcript(video_id, language='en'):
    """Fetch video details and transcript."""
    # Fetch video details
    url = 'https://www.googleapis.com/youtube/v3/videos'
    params = {
        'part': 'snippet,contentDetails',
        'id': video_id,
        'key': YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if not data.get('items'):
        raise Exception('Video not found')
    video = data['items'][0]
    details = {
        'video_id': video_id,
        'title': video['snippet']['title'],
        'channel': video['snippet']['channelTitle'],
        'description': video['snippet']['description'],
        'embed_url': f"https://www.youtube.com/embed/{video_id}",
        'duration': video['contentDetails']['duration']
    }
    # Fetch transcript
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[language, 'en'])
        transcript = ' '.join([entry['text'] for entry in transcript_data])
        timestamps = [entry['start'] for entry in transcript_data for _ in entry['text'].split()]
    except (TranscriptsDisabled, NoTranscriptFound):
        transcript = "No transcript available for this video."
        timestamps = []
    except Exception as e:
        transcript = f"Transcript error: {e}"
        timestamps = []
    return {'details': details, 'transcript': transcript, 'timestamps': timestamps}

def normalize_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

@anvil.server.callable
def compare_transcriptions(user_transcription, actual_transcript):
    """Compare user transcription to actual transcript and return stats/results."""
    user_words = normalize_text(user_transcription).split()
    actual_words = normalize_text(actual_transcript).split()
    correct = sum(1 for u, a in zip(user_words, actual_words) if u == a)
    total = len(actual_words)
    accuracy = (correct / total * 100) if total else 0
    # Simple diff: mark correct/incorrect words
    diff = []
    for i, word in enumerate(user_words):
        if i < len(actual_words) and word == actual_words[i]:
            diff.append({'word': word, 'correct': True})
        else:
            diff.append({'word': word, 'correct': False})
    return {
        'total_words': total,
        'user_words': len(user_words),
        'correct_words': correct,
        'accuracy': accuracy,
        'diff': diff
    } 
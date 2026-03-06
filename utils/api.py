import requests
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import (
    BATCH_API, TOPIC_API, VIDEO_API, ALL_BATCHES_API,
    MAX_WORKERS, TIMEOUT, MAX_RETRIES, RETRY_DELAY
)

logger = logging.getLogger(__name__)

# Session for reuse
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def fetch_json(url, retries=MAX_RETRIES):
    """Fetch JSON from URL"""
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=TIMEOUT)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                time.sleep(RETRY_DELAY * (attempt + 1) * 2)
            else:
                time.sleep(RETRY_DELAY)
        except:
            time.sleep(RETRY_DELAY)
    return None

def get_video_url(video_id):
    """Get video URL from ID"""
    try:
        data = fetch_json(VIDEO_API.format(video_id))
        if data:
            if "file_url" in data:
                return data["file_url"]
            if "data" in data and isinstance(data["data"], dict):
                if "link" in data["data"]:
                    return data["data"]["link"].get("file_url")
        return None
    except:
        return None

def get_batch_info(batch_id):
    """Get batch information"""
    return fetch_json(BATCH_API.format(batch_id))

def get_topic_details(batch_id, topic_id):
    """Get topic details"""
    return fetch_json(TOPIC_API.format(batch_id, topic_id))

def get_all_batches():
    """Get all batches"""
    return fetch_json(ALL_BATCHES_API)

def validate_batch(batch_id):
    """Validate batch ID"""
    return get_batch_info(batch_id) is not None

def process_topic(batch_id, topic):
    """Process a single topic"""
    results = []
    try:
        topic_id = topic.get("id") or topic.get("topicId")
        topic_name = topic.get("topicName") or topic.get("name") or "Unknown"
        
        if not topic_id:
            return results
        
        data = get_topic_details(batch_id, topic_id)
        if not data:
            return results
        
        # Videos
        for cls in data.get("classes", []):
            video_id = cls.get("video_url")
            if video_id:
                url = get_video_url(video_id)
                if url:
                    results.append({
                        "type": "drm" if url.endswith('.mpd') else "video",
                        "topic": topic_name,
                        "title": cls.get("title", ""),
                        "url": url,
                        "line": f"[{topic_name}] {cls.get('title', '')}: {url}"
                    })
        
        # PDFs
        for note in data.get("notes", []):
            url = note.get("view_url") or note.get("download_url")
            if url and url.endswith('.pdf'):
                results.append({
                    "type": "pdf",
                    "topic": topic_name,
                    "title": note.get("title", ""),
                    "url": url,
                    "line": f"[{topic_name}] PDF - {note.get('title', '')}: {url}"
                })
        
        return results
    except:
        return results

def extract_batch(batch_id, progress_callback=None):
    """Extract entire batch"""
    start = time.time()
    
    batch = get_batch_info(batch_id)
    if not batch:
        return None
    
    name = batch.get("batch_name") or batch.get("name") or f"Batch_{batch_id}"
    topics = batch.get("topics", [])
    
    all_items = []
    videos = pdfs = drm = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_topic, batch_id, t) for t in topics]
        completed = 0
        total = len(topics)
        
        for future in as_completed(futures):
            completed += 1
            items = future.result()
            all_items.extend(items)
            
            for item in items:
                if item['type'] == 'video':
                    videos += 1
                elif item['type'] == 'pdf':
                    pdfs += 1
                else:
                    drm += 1
            
            if progress_callback and total > 0:
                percent = (completed / total) * 100
                bar = '█' * int(percent/5) + '░' * (20 - int(percent/5))
                progress_callback(
                    f"Progress: {bar} {percent:.1f}%\n"
                    f"Videos: {videos} | PDFs: {pdfs}"
                )
    
    return {
        'name': name,
        'total': len(all_items),
        'videos': videos,
        'pdfs': pdfs,
        'drm': drm,
        'time': time.time() - start,
        'items': [i['line'] for i in all_items]
    }

def test_api_connection():
    """Test API connection"""
    try:
        r = session.get(ALL_BATCHES_API, timeout=5)
        return r.status_code == 200
    except:
        return False

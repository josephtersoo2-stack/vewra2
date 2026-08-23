import json
import logging
import re
import requests
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def fetch_gemini_models(api_key: str) -> List[Dict[str, Any]]:
    """
    Dynamically queries Google Gemini API for available generation models.
    No hardcoded models.
    """
    from apps.core.vault import decrypt_secret

    if not api_key:
        raise ValueError("Gemini API key is required to fetch models.")

    clean_key = decrypt_secret(api_key).strip() if api_key.startswith('enc:') else api_key.strip()

    url = f"{GEMINI_BASE_URL}/models?key={clean_key}"
    response = requests.get(url, timeout=12)

    if response.status_code != 200:
        error_msg = response.text
        try:
            err_json = response.json()
            error_msg = err_json.get('error', {}).get('message', error_msg)
        except Exception:
            pass
        raise RuntimeError(f"Gemini API error ({response.status_code}): {error_msg}")

    data = response.json()
    models_raw = data.get('models', [])

    parsed_models = []
    for m in models_raw:
        methods = m.get('supportedGenerationMethods', [])
        # Only return models that support generateContent
        if 'generateContent' in methods:
            model_id = m.get('name', '')
            if model_id.startswith('models/'):
                model_id = model_id[len('models/'):]

            parsed_models.append({
                'id': model_id,
                'name': m.get('displayName', model_id),
                'description': m.get('description', ''),
                'input_token_limit': m.get('inputTokenLimit', 0),
            })

    # Sort with flash / 2.0 / 2.5 / 1.5 at the top
    parsed_models.sort(key=lambda x: ('flash' in x['id'].lower() or '2.5' in x['id'].lower() or '2.0' in x['id'].lower()), reverse=True)
    return parsed_models


def generate_keywords_gemini(
    api_key: str,
    model: str,
    video_data: Dict[str, Any],
    system_prompt: str
) -> List[Dict[str, Any]]:
    """
    Calls Google Gemini to generate 8 categorized high-precision
    search queries with ranking guarantee notes.
    """
    from apps.core.vault import decrypt_secret

    if not api_key:
        raise ValueError("Gemini API key is missing. Please configure your Gemini API key.")

    clean_key = decrypt_secret(api_key).strip() if api_key.startswith('enc:') else api_key.strip()
    model_name = model.strip() if model else "gemini-2.5-flash"
    if model_name.startswith("models/"):
        model_name = model_name[len("models/"):]

    url = f"{GEMINI_BASE_URL}/models/{model_name}:generateContent?key={clean_key}"

    tags_str = video_data.get('tags_str', '')
    if not tags_str and video_data.get('tags'):
        tags_str = ", ".join([str(t) for t in video_data.get('tags', [])[:10]])

    video_url = video_data.get('url') or video_data.get('video_url') or f"https://www.youtube.com/watch?v={video_data.get('video_id', '')}"

    user_prompt = f"""{system_prompt}

TARGET YOUTUBE VIDEO:
- Video URL: {video_url}
- Video ID: {video_data.get('video_id', '')}
- Title: {video_data.get('title', '')}
- Channel / Creator Name: {video_data.get('channel', video_data.get('author_name', ''))}
- Description: {video_data.get('description', '')[:600]}
- Video Tags / Keywords: {tags_str or 'None'}

Generate exactly 8 categorized search queries with 1-sentence ranking guarantee notes:
1. [Channel Name] + [Core Topic] (Exact creator lookup)
2. [Exact Title Match] (Full video title)
3. [Core Topic] + [Channel Name] (Topical variant)
4. [Specific Tools / Software Mentioned] + [Core Topic] (Toolchain search)
5. [Exact Hook Phrase / Unique Catchphrase] (Verbatim spoken or thumbnail text)
6. [Broad Tutorial Query] + [Channel Name] (Educational intent)
7. [Niche / Case Study Topic] + [Channel Name] (Specific example used in video)
8. [High-Intent User Problem / Solution Query] (Natural conversational search)

Output ONLY a valid JSON array of 8 objects matching this structure:
[
  {{"category": "1. Exact creator lookup", "query": "...", "note": "..."}},
  {{"category": "2. Full video title", "query": "...", "note": "..."}},
  {{"category": "3. Topical variant", "query": "...", "note": "..."}},
  {{"category": "4. Toolchain search", "query": "...", "note": "..."}},
  {{"category": "5. Verbatim spoken or thumbnail hook", "query": "...", "note": "..."}},
  {{"category": "6. Educational intent", "query": "...", "note": "..."}},
  {{"category": "7. Specific case study / example", "query": "...", "note": "..."}},
  {{"category": "8. Natural conversational search", "query": "...", "note": "..."}}
]
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.25,
            "responseMimeType": "application/json"
        }
    }

    response = requests.post(url, json=payload, timeout=20)
    if response.status_code != 200:
        error_msg = response.text
        try:
            err_json = response.json()
            error_msg = err_json.get('error', {}).get('message', error_msg)
        except Exception:
            pass
        raise RuntimeError(f"Gemini generation error ({response.status_code}): {error_msg}")

    data = response.json()
    candidates = data.get('candidates', [])
    if not candidates:
        raise RuntimeError("Gemini returned no candidates.")

    text_content = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
    return _parse_categorized_keywords(text_content, video_data)


def _parse_categorized_keywords(raw_text: str, video_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    title = video_data.get('title', '')
    channel = video_data.get('channel', video_data.get('author_name', ''))

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list) and len(parsed) > 0:
            result = []
            for i, item in enumerate(parsed):
                if isinstance(item, dict):
                    q = str(item.get('query', '')).strip().strip('"\'')
                    cat = str(item.get('category', f"Category {i+1}")).strip()
                    note = str(item.get('note', '')).strip()
                    if q:
                        result.append({
                            'category': cat,
                            'query': q,
                            'note': note or f"Direct match for {cat}",
                        })
                elif isinstance(item, str) and item.strip():
                    result.append({
                        'category': f"Query {i+1}",
                        'query': item.strip().strip('"\''),
                        'note': f"High-precision search phrase for {channel or title}",
                    })
            if result:
                return result
    except Exception as e:
        logger.warning(f"Failed to parse JSON array from Gemini: {e}, raw text: {cleaned[:200]}")

    # Fallback line parsing
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    extracted = []
    for line in lines:
        cleaned_line = re.sub(r'^[\d\.\-\*\•\)\s]+', '', line).strip().strip('"\'')
        note_match = re.search(r'\((.*?)\)$', cleaned_line)
        note = note_match.group(1).strip() if note_match else ""
        query = re.sub(r'\(.*?\)$', '', cleaned_line).strip().strip('"\'')
        if len(query) > 3:
            extracted.append({
                'category': f"Query {len(extracted)+1}",
                'query': query,
                'note': note or f"Optimized rank query for {channel or title}",
            })

    if extracted:
        return extracted[:8]

    return [
        {'category': '1. Exact creator lookup', 'query': f"{channel} {title}" if channel else title, 'note': 'Exact creator lookup'},
        {'category': '2. Full video title', 'query': title, 'note': 'Full exact title match'},
    ]

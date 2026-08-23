import json
import logging
import re
import requests
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def fetch_openrouter_models(api_key: str = "") -> List[Dict[str, Any]]:
    """
    Dynamically queries OpenRouter API for available models.
    Supports querying both with an active API key or public model list.
    """
    from apps.core.vault import decrypt_secret

    url = f"{OPENROUTER_BASE_URL}/models"
    headers = {
        "HTTP-Referer": "https://vewra.app",
        "X-Title": "Vewra Video Tasks",
    }

    if api_key and api_key.strip():
        clean_key = decrypt_secret(api_key).strip() if api_key.startswith('enc:') else api_key.strip()
        headers["Authorization"] = f"Bearer {clean_key}"

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            error_msg = response.text
            try:
                err_json = response.json()
                error_msg = err_json.get('error', {}).get('message', error_msg)
            except Exception:
                pass
            raise RuntimeError(f"OpenRouter API error ({response.status_code}): {error_msg}")

        data = response.json()
        models_raw = data.get('data', [])

        parsed_models = []
        for m in models_raw:
            model_id = m.get('id', '')
            if model_id:
                parsed_models.append({
                    'id': model_id,
                    'name': m.get('name', model_id),
                    'description': m.get('description', ''),
                    'context_length': m.get('context_length', 0),
                    'pricing': m.get('pricing', {}),
                })

        # Sort popular / fast / free models to the top
        def _sort_weight(item):
            mid = item['id'].lower()
            if ':free' in mid or 'free' in mid:
                return 4
            if 'flash' in mid or 'mini' in mid:
                return 3
            if 'gemini' in mid or 'llama' in mid or 'claude' in mid or 'gpt-4o' in mid or 'deepseek' in mid or 'mistral' in mid:
                return 2
            return 1

        parsed_models.sort(key=_sort_weight, reverse=True)
        return parsed_models

    except Exception as e:
        logger.error(f"Error fetching OpenRouter models: {e}")
        raise RuntimeError(f"Could not connect to OpenRouter: {e}")


def generate_keywords_openrouter(
    api_key: str,
    model: str,
    video_data: Dict[str, Any],
    system_prompt: str
) -> List[Dict[str, Any]]:
    """
    Calls OpenRouter chat completions API to generate 8 categorized high-precision
    search queries with ranking guarantee notes.
    """
    from apps.core.vault import decrypt_secret

    if not api_key:
        raise ValueError("OpenRouter API key is missing. Please configure your OpenRouter API key.")

    clean_key = decrypt_secret(api_key).strip() if api_key.startswith('enc:') else api_key.strip()
    model_name = model.strip() if model else "google/gemini-2.5-flash"

    url = f"{OPENROUTER_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {clean_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://vewra.app",
        "X-Title": "Vewra Video Tasks",
    }

    tags_str = video_data.get('tags_str', '')
    if not tags_str and video_data.get('tags'):
        tags_str = ", ".join([str(t) for t in video_data.get('tags', [])[:10]])

    video_url = video_data.get('url') or video_data.get('video_url') or f"https://www.youtube.com/watch?v={video_data.get('video_id', '')}"

    user_prompt = f"""Analyze this YouTube video:
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
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.25,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    if response.status_code != 200:
        error_msg = response.text
        try:
            err_json = response.json()
            error_msg = err_json.get('error', {}).get('message', error_msg)
        except Exception:
            pass
        raise RuntimeError(f"OpenRouter generation error ({response.status_code}): {error_msg}")

    data = response.json()
    choices = data.get('choices', [])
    if not choices:
        raise RuntimeError("OpenRouter returned no choices.")

    content = choices[0].get('message', {}).get('content', '')
    return _parse_categorized_keywords(content, video_data)


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
        logger.warning(f"Failed to parse JSON array from OpenRouter: {e}, raw text: {cleaned[:200]}")

    # Fallback regex / line parsing
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

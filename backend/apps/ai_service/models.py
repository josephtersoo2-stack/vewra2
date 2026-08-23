import os
from django.db import models

DEFAULT_SYSTEM_PROMPT = """You are a YouTube SEO and Search Retrieval Specialist.

When provided a YouTube video URL, title, channel name, and metadata details, analyze the video's title, creator name, description, visual cues, unique tools/workflows, and core topic.

Generate exactly 8 high-precision YouTube search queries that will rank this specific video on the first page (#1 to #3) of YouTube search results.

Categorize and format the queries as follows:
1. [Channel Name] + [Core Topic] (Exact creator lookup)
2. [Exact Title Match] (Full video title)
3. [Core Topic] + [Channel Name] (Topical variant)
4. [Specific Tools / Software Mentioned] + [Core Topic] (Toolchain search)
5. [Exact Hook Phrase / Unique Catchphrase] (Verbatim spoken or thumbnail text)
6. [Broad Tutorial Query] + [Channel Name] (Educational intent)
7. [Niche / Case Study Topic] + [Channel Name] (Specific example used in video)
8. [High-Intent User Problem / Solution Query] (Natural conversational search)

Under each search query, include a 1-sentence note in parentheses explaining why that query guarantees a top-ranking match.

Output format: Return ONLY a valid JSON array of 8 objects with "category", "query", and "note" keys:
[
  {
    "category": "1. Exact creator lookup",
    "query": "...",
    "note": "..."
  },
  ...
]
"""

class AISettings(models.Model):
    PROVIDER_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('openrouter', 'OpenRouter'),
    ]

    active_provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='openrouter',
        help_text="Active LLM provider for generating video keywords."
    )
    gemini_api_key = models.CharField(
        max_length=255,
        blank=True,
        help_text="Google Gemini API Key (or set GEMINI_API_KEY environment variable)."
    )
    openrouter_api_key = models.CharField(
        max_length=255,
        blank=True,
        help_text="OpenRouter API Key (or set OPENROUTER_API_KEY environment variable)."
    )
    selected_model = models.CharField(
        max_length=150,
        blank=True,
        help_text="Dynamic Model ID chosen from the live provider model list (e.g. google/gemini-2.5-flash or meta-llama/llama-3.3-70b-instruct)."
    )
    custom_system_prompt = models.TextField(
        default=DEFAULT_SYSTEM_PROMPT,
        blank=True,
        help_text="Prompt instructions sent to the LLM for keyword extraction."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Enable/disable AI keyword generation."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Keyword Settings"
        verbose_name_plural = "AI Keyword Settings"

    def __str__(self):
        return f"AI Settings ({self.get_active_provider_display()} - {self.selected_model or 'Default Model'})"

    def save(self, *args, **kwargs):
        from apps.core.vault import encrypt_secret
        if self.gemini_api_key and not self.gemini_api_key.startswith('enc:'):
            self.gemini_api_key = encrypt_secret(self.gemini_api_key)
        if self.openrouter_api_key and not self.openrouter_api_key.startswith('enc:'):
            self.openrouter_api_key = encrypt_secret(self.openrouter_api_key)
        super().save(*args, **kwargs)

    def get_effective_gemini_key(self) -> str:
        from apps.core.vault import decrypt_secret
        key = self.gemini_api_key or os.environ.get('GEMINI_API_KEY', '')
        return decrypt_secret(key).strip()

    def get_effective_openrouter_key(self) -> str:
        from apps.core.vault import decrypt_secret
        key = self.openrouter_api_key or os.environ.get('OPENROUTER_API_KEY', '')
        return decrypt_secret(key).strip()

    @classmethod
    def get_settings(cls) -> 'AISettings':
        settings, _ = cls.objects.get_or_create(id=1)
        return settings

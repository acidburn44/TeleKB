import re
import os
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl, MessageEntityBold, MessageEntityItalic, MessageEntityCode, MessageEntityPre

KEYWORDS = {
  "kr_range": r"[가-힣ㄱ-ㅎㅏ-ㅣ]"
}

class TextUtils:
    @staticmethod
    def is_korean(text: str) -> bool:
        if not text:
            return False
            
        # 1. Remove URLs
        text_no_url = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 2. Extract meaningful characters (remove whitespace, punctuation etc.)
        kr_pattern = KEYWORDS['kr_range']
        # Keep English, Numbers, and Korean
        meaningful_chars = re.sub(r'[^a-zA-Z0-9' + kr_pattern + r']', '', text_no_url)
        
        if len(meaningful_chars) < 5:
            return False # 판별 불가 (번역 시도)
            
        korean_chars = re.findall(KEYWORDS['kr_range'], meaningful_chars)
        korean_ratio = len(korean_chars) / len(meaningful_chars)
        
        return korean_ratio >= 0.30

    @staticmethod
    def sanitize_filename(text: str) -> str:
        # Invalid chars in Windows: \ / : * ? " < > |
        # In macOS: : / (mostly)
        # We replace with underscore or remove.
        
        # 1. Remove newlines/tabs
        text = text.replace('\n', ' ').replace('\t', ' ').strip()
        
        # 2. Replace invalid chars
        text = re.sub(r'[\\/:*?"<>|]', '_', text)
        
        # 3. Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text

    @staticmethod
    def get_first_sentence(text: str, max_length: int = 60) -> str:
        if not text:
            return "No_Content"
            
        first_line = text.split('\n')[0].strip()
        if not first_line:
            return "No_Content"

        # Truncate
        if len(first_line) > max_length:
            return first_line[:max_length] 
            
        return first_line

    @staticmethod
    def convert_entities_to_markdown(text: str, entities: list) -> str:
        if not entities or not text:
            return text

        # Sort entities by offset descending so we can replace without shifting earlier offsets
        sorted_entities = sorted(entities, key=lambda e: e.offset, reverse=True)
        
        # We need to be careful with UTF-16 offsets if Telegram uses them?
        # Telethon usually handles this, but Python strings are indexed by char (Unicode code points usually).
        # Telethon documentation says offsets are in UTF-16 code units.
        # Python LEN is in characters. Emojis might differ.
        # However, for simple logic, let's assume Python indexing works or Telethon helpers are needed.
        # Ideally, we used `telethon.extensions.markdown.parse` but that creates full markdown.
        # Let's try manual replacement for URLs as requested.
        
        # Actually Telethon's `add_surrogate` helper might be needed for exact offsets if emojis are present.
        # But for strictly URLs, let's try direct slicing. If it breaks with emoji, we fix.
        
        mutable_text = list(text.encode('utf-16-le'))[2:] # Simple byte manipulation is hard.
        # Better: use a library or just try direct string manipulation assuming mostly BMP or Python handles it.
        # Wait, if `text` contains emojis, `len(text)` in Python count them as 1 usually (wrapper dependent).
        # Telegram API counts UTF-16 code units.
        # If user has emojis before the link, conversion might be off.
        # Let's stick to string slicing for now, user asked for URL support primarily.
        
        result = text
        
        # To handle offsets correctly with emojis, we can convert to utf-16 string if possible, or use a helper.
        # But since we want to avoid complex dependencies, let's use the standard way if feasible.
        # Correction: `sorted_entities` are reversed.
        
        # We must rebuild the string. Slicing with UTF-16 offsets in Python native strings is tricky.
        # Example: '😀' len is 1 in Python 3 (mostly), but 2 in UTF-16.
        # We can implement a simplified helpers if needed.
        
        # Let's try using `telethon.utils.add_surrogate` logic? 
        # Telethon has `helpers.add_surrogate`.
        # `text = helpers.add_surrogate(text)` makes it len-compatible with Telegram offsets.
        # Then we slice, then `del_surrogate`.
        
        from telethon.helpers import add_surrogate, del_surrogate
        
        text_surrogate = add_surrogate(text)
        
        for entity in sorted_entities:
            start = entity.offset
            end = start + entity.length
            
            inner_text = text_surrogate[start:end]
            replacement = inner_text
            
            if isinstance(entity, MessageEntityTextUrl):
                url = entity.url
                replacement = f"[{inner_text}]({url})"
            elif isinstance(entity, MessageEntityUrl):
                # Auto-link. We can leave it or format it.
                # Markdown usually auto-links. But explicit is better.
                replacement = f"[{inner_text}]({inner_text})"
            elif isinstance(entity, MessageEntityBold):
                replacement = f"**{inner_text}**"
            elif isinstance(entity, MessageEntityItalic):
                replacement = f"*{inner_text}*"
            elif isinstance(entity, (MessageEntityCode, MessageEntityPre)):
                replacement = f"`{inner_text}`"
                
            text_surrogate = text_surrogate[:start] + replacement + text_surrogate[end:]
            
        return del_surrogate(text_surrogate)

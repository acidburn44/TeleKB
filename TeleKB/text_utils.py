import re
import os
import copy
from telethon import helpers
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl, MessageEntityBold, MessageEntityItalic, MessageEntityCode, MessageEntityPre
from telethon.extensions.markdown import unparse

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
        try:
            # Preprocess entities: split Bold/Italic entities containing newlines
            text_surrogate = helpers.add_surrogate(text)
            processed_entities = []
            
            for entity in entities:
                if isinstance(entity, (MessageEntityBold, MessageEntityItalic)):
                    offset = entity.offset
                    length = entity.length
                    sub_text = text_surrogate[offset : offset + length]
                    
                    if '\n' in sub_text or '\r' in sub_text:
                        # Split by newlines and create separate entities
                        i = 0
                        while i < len(sub_text):
                            while i < len(sub_text) and sub_text[i] in ('\r', '\n'):
                                i += 1
                            if i >= len(sub_text):
                                break
                            
                            start_idx = i
                            while i < len(sub_text) and sub_text[i] not in ('\r', '\n'):
                                i += 1
                            end_idx = i
                            
                            segment = sub_text[start_idx:end_idx]
                            stripped = segment.strip()
                            if stripped:
                                leading_spaces = len(segment) - len(segment.lstrip())
                                cloned = copy.copy(entity)
                                cloned.offset = offset + start_idx + leading_spaces
                                cloned.length = len(stripped)
                                processed_entities.append(cloned)
                    else:
                        # Strip leading/trailing spaces for non-newline entities too
                        segment = sub_text
                        stripped = segment.strip()
                        if stripped:
                            leading_spaces = len(segment) - len(segment.lstrip())
                            cloned = copy.copy(entity)
                            cloned.offset = offset + leading_spaces
                            cloned.length = len(stripped)
                            processed_entities.append(cloned)
                else:
                    processed_entities.append(entity)
                    
            return unparse(text, processed_entities)
        except Exception as e:
            print(f"Error converting entities to markdown: {e}")
            return text

import os
import datetime
from .text_utils import TextUtils

class FileManager:
    @staticmethod
    def save_markdown(channel_name: str, message_text: str, translated_text: str, 
                      message_id: int, message_date: datetime.datetime, 
                      output_dir: str, is_korean_skipped: bool = False,
                      image_paths: list = None) -> str:
        
        # 1. Prepare filename
        first_sentence = TextUtils.get_first_sentence(message_text)
        sanitized_channel = TextUtils.sanitize_filename(channel_name)[:30] # Max 30
        sanitized_sentence = TextUtils.sanitize_filename(first_sentence)[:60] # Max 60
        date_str = message_date.strftime("%Y%m%d")
        
        filename = f"{sanitized_channel}_{sanitized_sentence}_{date_str}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Handle duplicates? Spec doesn't say what if filename exists.
        # But messages are unique by ID. If filename collision, we might overwrite or append.
        # Let's just append _1, _2 if exists to be safe, though not explicitly required by spec, 
        # but 6.1 says "중복 방지...". Wait, "중복 방지 기록을 DB에 남긴다".
        # If filename collision happens for DIFFERENT messages (same first sentence), we should probably not overwrite.
        
        base_name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filepath):
            filepath = os.path.join(output_dir, f"{base_name}_{counter}{ext}")
            counter += 1
            
        # 2. Prepare content
        content = f"# {channel_name}\n\n"
        # Convert to local time if timezone aware, else assume local?
        # Telethon dates are usually UTC.
        if message_date.tzinfo:
            local_date = message_date.astimezone()
        else:
            local_date = message_date
            
        content += f"**Time:** {local_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"**Message ID:** {message_id}\n\n"
        content += "---\n\n"
        content += "## Original Text\n\n"
        content += f"{message_text}\n\n"
        content += "---\n\n"
        content += "## Korean Translation\n\n"
        
        if is_korean_skipped:
            content += "> 번역 생략: 원문이 한국어로 판단됨\n"
        else:
            content += f"{translated_text}\n"

        if image_paths:
            content += "\n---\n\n"
            content += "## Images\n\n"
            for img_path in image_paths:
                # Calculate relative path for markdown
                try:
                    rel_path = os.path.relpath(img_path, output_dir)
                    # Markdown uses forward slashes
                    rel_path = rel_path.replace(os.sep, '/')
                    content += f"![Image]({rel_path})\n\n"
                except ValueError:
                    # If paths are on different drives, relpath fails on Windows
                    # Fallback to absolute or just ignore?
                    # Ideally we put images in subfolder of output_dir so it should be fine.
                    content += f"![Image]({img_path})\n\n"
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        return filepath

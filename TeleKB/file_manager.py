import os
import datetime
from .text_utils import TextUtils

class FileManager:
    @staticmethod
    def get_target_directory_name(message_date: datetime.datetime) -> str:
        if message_date.tzinfo:
            local_date = message_date.astimezone()
        else:
            local_date = message_date
        return local_date.strftime("%Y-%m")

    @staticmethod
    def save_markdown(channel_name: str, message_text: str, translated_text: str, 
                      message_id: int, message_date: datetime.datetime, 
                      output_dir: str, is_korean_skipped: bool = False,
                      image_paths: list = None) -> str:
        
        # 1. Prepare filename & directory
        folder_name = FileManager.get_target_directory_name(message_date)
        target_dir = os.path.join(output_dir, folder_name)
        os.makedirs(target_dir, exist_ok=True)
        
        # Use local date for filename suffix too
        if message_date.tzinfo:
            local_date = message_date.astimezone()
        else:
            local_date = message_date
            
        sanitized_channel = TextUtils.sanitize_filename(channel_name)[:30] # Max 30
        date_str = local_date.strftime("%Y%m%d")
        
        filename = f"{sanitized_channel}_{date_str}.md"
        filepath = os.path.join(target_dir, filename)
        
        # 2. Prepare content
        content = ""
        
        # Add separator if file exists and is not empty
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            content += "\n---\n\n"
            
        content += f"## Message ID: {message_id}\n"
        content += f"**Time:** {local_date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        content += "### Original Text\n\n"
        content += f"{message_text}\n\n"
        
        content += "### Korean Translation\n\n"
        
        if is_korean_skipped:
            content += "> 번역 생략: 원문이 한국어로 판단됨\n"
        else:
            content += f"{translated_text}\n"

        if image_paths:
            content += "\n### Images\n\n"
            for img_path in image_paths:
                # Calculate relative path for markdown
                try:
                    rel_path = os.path.relpath(img_path, target_dir)
                    # Markdown uses forward slashes
                    rel_path = rel_path.replace(os.sep, '/')
                    content += f"![Image]({rel_path})\n\n"
                except ValueError:
                    # If paths are on different drives, relpath fails on Windows
                    # Fallback to absolute or just ignore?
                    # Ideally we put images in subfolder of output_dir so it should be fine.
                    content += f"![Image]({img_path})\n\n"
            
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content)
            
        return filepath

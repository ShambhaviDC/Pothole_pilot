import os
import re

file_path = r'E:\pothole\potholes\templates\potholes\community_feed.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original content around line 24:\n{content[content.find('severity_filter'):content.find('severity_filter')+50]}")

# Fix severity filter tags with regex to be robust
content = re.sub(r"severity_filter\s*==\s*'(\w+)'", r"severity_filter == '\1'", content)

# Fix order_by tags with regex
content = re.sub(r"order_by\s*==\s*'(\w+)'", r"order_by == '\1'", content)

# Remove any extra spaces inside {% if ... %} if they were added accidentally
# But let's keep it simple first.

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fix applied successfully.")

with open(file_path, 'r', encoding='utf-8') as f:
    new_content = f.read()
print(f"New content around line 24:\n{new_content[new_content.find('severity_filter'):new_content.find('severity_filter')+50]}")

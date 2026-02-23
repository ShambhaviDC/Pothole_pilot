import os

file_path = r'E:\pothole\potholes\templates\potholes\community_feed.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Verify initial state of line 24 (index 23)
print(f"DEBUG: Initial line 24: {repr(lines[23])}")

# Update lines with proper spacing
lines[23] = '                            <option value="Low" {% if severity_filter == \'Low\' %}selected{% endif %}>Low</option>\n'
lines[24] = '                            <option value="Medium" {% if severity_filter == \'Medium\' %}selected{% endif %}>Medium</option>\n'
lines[25] = '                            <option value="High" {% if severity_filter == \'High\' %}selected{% endif %}>High</option>\n'
lines[32] = '                            <option value="recent" {% if order_by == \'recent\' %}selected{% endif %}>Most Recent</option>\n'
lines[33] = '                            <option value="votes" {% if order_by == \'votes\' %}selected{% endif %}>Most Voted</option>\n'

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify final state
with open(file_path, 'r', encoding='utf-8') as f:
    final_lines = f.readlines()
print(f"DEBUG: Final line 24: {repr(final_lines[23])}")
print("Fix applied successfully.")

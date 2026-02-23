import os

target = r'c:\hackth\Pothole_pilot\potholes\templates\potholes\community_feed.html'

with open(target, 'r') as f:
    content = f.readlines()

new_lines = []
for line in content:
    # Fix the multi-line Truth Score badge
    if 'Truth Score: <span class="badge bg-info">{{' in line:
        new_lines.append(line.replace('Truth Score: <span class="badge bg-info">{{', 'Truth Score: <span class="badge bg-info">{{ pothole.user.profile.truth_score }}</span></small>\n'))
        skip_next = True
    elif 'pothole.user.profile.truth_score }}</span></small>' in line:
        continue # skip the leftover line
    else:
        new_lines.append(line)

with open(target, 'w') as f:
    f.writelines(new_lines)

print("CLEANUP SUCCESSFUL")

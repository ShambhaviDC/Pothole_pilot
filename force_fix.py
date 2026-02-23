import os

target = r'c:\hackth\Pothole_pilot\potholes\templates\potholes\community_feed.html'

with open(target, 'r') as f:
    content = f.read()

print(f"Original length: {len(content)}")

# Fix spaces
content = content.replace("severity_filter=='Low'", "severity_filter == 'Low'")
content = content.replace("severity_filter=='Medium'", "severity_filter == 'Medium'")
content = content.replace("severity_filter=='High'", "severity_filter == 'High'")
content = content.replace("order_by=='recent'", "order_by == 'recent'")
content = content.replace("order_by=='votes'", "order_by == 'votes'")

# Fix truth score
content = content.replace("pothole.author_truth_score", "pothole.user.profile.truth_score")

print(f"New length: {len(content)}")

with open(target, 'w') as f:
    f.write(content)

print("FILE WRITTEN SUCCESSFULLY")

# Verify
with open(target, 'r') as f:
    new_c = f.read()
    if "severity_filter == 'Low'" in new_c:
        print("VERIFICATION SUCCESSFUL: Spaces found.")
    else:
        print("VERIFICATION FAILED: Spaces NOT found.")

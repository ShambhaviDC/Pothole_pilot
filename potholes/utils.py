import math
from PIL import Image
import io

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) in meters.
    """
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371000 # Radius of earth in meters. Use 3956 for miles
    return c * r

def get_image_hash(image_file):
    """
    Generates a simple average hash for an image.
    """
    try:
        # Move to the beginning of the file to ensure we read it all
        image_file.seek(0)
        img = Image.open(image_file).convert('L').resize((8, 8), Image.Resampling.LANCZOS)
        pixels = list(img.getdata())
        avg = sum(pixels) / len(pixels)
        bits = "".join(['1' if p > avg else '0' for p in pixels])
        hex_hash = hex(int(bits, 2))[2:].zfill(16)
        # Reset pointer for subsequent reads
        image_file.seek(0)
        return hex_hash
    except Exception as e:
        print(f"Error generating hash: {e}")
        return None

def compare_hashes(hash1, hash2, threshold=10):
    """
    Compares two hexadecimal hashes. 
    threshold is the maximum Hamming distance allowed for a match.
    """
    if not hash1 or not hash2:
        return False
    
    # Convert hex back to integer
    i1 = int(hash1, 16)
    i2 = int(hash2, 16)
    
    # XOR to find differing bits
    diff = i1 ^ i2
    # Count set bits
    distance = bin(diff).count('1')
    
    return distance <= threshold

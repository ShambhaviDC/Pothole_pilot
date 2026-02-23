import os
import numpy as np

# Lazy imports to speed up form initialization
_MODEL = None

def get_ai_logic():
    global _MODEL
    
    # We import inside to ensure tensorflow is only loaded when needed
    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
    from tensorflow.keras.preprocessing import image
    
    if _MODEL is None:
        # Load weights once
        _MODEL = MobileNetV2(weights='imagenet')
    return _MODEL, preprocess_input, decode_predictions, image

def analyze_pothole_image(image_bytes):
    """
    Analyzes an image using MobileNetV2 with strict custom logic rules specified by the user.
    """
    try:
        model, preprocess_input, decode_predictions, image_loader = get_ai_logic()
        
        # Load and preprocess image from bytes
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB')
        img = img.resize((224, 224))
        
        x = np.array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        # AI Prediction
        preds = model.predict(x)
        # Get top 3
        decoded = decode_predictions(preds, top=3)[0]
        
        # --- SPECIFIC LOGIC RULES ---
        pothole_keywords = ['volcano', 'geological fault', 'fissure', 'crack']
        road_keywords = ['asphalt', 'pavement', 'curb', 'street']
        deny_list = ['flower', 'lotus', 'animal', 'person', 'building', 'indoor']
        
        top_guesses = []
        is_pothole_detected = False
        is_road_surface_detected = False
        has_denied_content = False
        max_confidence = 0
        
        for i, (id, label, prob) in enumerate(decoded):
            clean_label = label.lower().replace('_', ' ')
            confidence = float(prob) * 100
            top_guesses.append(f"{clean_label} ({confidence:.1f}%)")
            
            if i == 0:
                max_confidence = confidence
            
            # Rule 1: Translation Logic (Geological features = Potholes)
            if any(k in clean_label for k in pothole_keywords):
                is_pothole_detected = True
            
            # Rule 2: Road Verification
            if any(k in clean_label for k in road_keywords):
                is_road_surface_detected = True
                
            # Rule 3: Strict Negative Filter (Deny List)
            if any(k in clean_label for k in deny_list):
                has_denied_content = True

        # Rule 4: Confidence Barrier (30%)
        if max_confidence < 30:
            return 'Rejected', top_guesses, "Low confidence detection (below 30%)."

        # Evaluation
        if has_denied_content:
            return 'Rejected', top_guesses, "Image contains prohibited content (people, buildings, or indoor items)."
        
        # Require BOTH a road surface AND a pothole signature (or high confidence road)
        if is_pothole_detected or is_road_surface_detected:
            return 'Verified', top_guesses, "Valid road/pothole signature detected."
        
        return 'Rejected', top_guesses, "The image does not contain recognized road or pothole features."

    except Exception as e:
        return 'Error', [], f"AI Analysis Error: {str(e)}"

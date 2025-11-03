from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
import re
from collections import Counter

app = Flask(__name__)

# ============================================================
# PERSUASIVE KEYWORDS DICTIONARY
# These words are categorized by their psychological impact
# ============================================================
PERSUASIVE_KEYWORDS = {
    'urgency': ['now', 'today', 'limited', 'hurry', 'fast', 'quick', 'immediate', 'urgent', 'deadline', 'expires'],
    'scarcity': ['exclusive', 'limited', 'rare', 'unique', 'only', 'last chance', 'running out', 'few left', 'scarce'],
    'authority': ['proven', 'certified', 'expert', 'professional', 'guaranteed', 'official', 'approved', 'trusted', 'verified'],
    'emotional': ['amazing', 'incredible', 'revolutionary', 'breakthrough', 'stunning', 'shocking', 'unbelievable', 'must-have'],
    'fear': ['risk', 'danger', 'warning', 'threat', 'lose', 'missing out', 'regret', 'avoid', 'prevent', 'protect'],
    'social_proof': ['popular', 'trending', 'everyone', 'millions', 'bestselling', 'top-rated', 'recommended', 'favorite']
}

# Flatten all keywords for easier detection
ALL_PERSUASIVE_WORDS = []
for category, words in PERSUASIVE_KEYWORDS.items():
    ALL_PERSUASIVE_WORDS.extend(words)

# ============================================================
# EMOTION DETECTION KEYWORDS (Cognitive Science Mapping)
# ============================================================
EMOTION_KEYWORDS = {
    'joy': ['happy', 'love', 'great', 'wonderful', 'excellent', 'amazing', 'fantastic', 'joy', 'delight', 'pleasure'],
    'fear': ['afraid', 'scary', 'danger', 'risk', 'threat', 'warning', 'worried', 'anxious', 'panic', 'terror'],
    'anger': ['angry', 'hate', 'furious', 'outrage', 'disgust', 'terrible', 'awful', 'worst', 'horrible', 'enraged'],
    'trust': ['trust', 'honest', 'reliable', 'genuine', 'authentic', 'sincere', 'true', 'verified', 'proven', 'guaranteed']
}


def detect_persuasive_keywords(text):
    """
    Detects persuasive keywords in the text using regex.
    Returns a dictionary with category counts and specific words found.
    """
    text_lower = text.lower()
    detected = {'total_count': 0, 'by_category': {}, 'words_found': []}
    
    for category, keywords in PERSUASIVE_KEYWORDS.items():
        category_count = 0
        for keyword in keywords:
            # Use word boundaries to match whole words
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text_lower)
            if matches:
                category_count += len(matches)
                detected['words_found'].extend(matches)
        
        detected['by_category'][category] = category_count
        detected['total_count'] += category_count
    
    return detected


def analyze_emotions(text):
    """
    Maps text to the four emotional axes using TextBlob and keyword detection.
    Returns emotion scores and breakdown.
    """
    blob = TextBlob(text)
    text_lower = text.lower()
    
    emotions = {'joy': 0, 'fear': 0, 'anger': 0, 'trust': 0}
    
    # Count emotion keywords
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text_lower)
            emotions[emotion] += len(matches)
    
    # Use TextBlob's polarity to boost emotion scores
    polarity = blob.sentiment.polarity
    
    if polarity > 0.3:
        emotions['joy'] += 3
        emotions['trust'] += 2
    elif polarity < -0.3:
        emotions['anger'] += 3
        emotions['fear'] += 2
    
    # Normalize to percentages
    total_emotion = sum(emotions.values())
    if total_emotion > 0:
        emotions = {k: round((v / total_emotion) * 100, 1) for k, v in emotions.items()}
    
    return emotions


def calculate_persuasion_score(persuasive_data, sentiment):
    """
    Calculate a persuasion score (0-100) based on:
    - Number of persuasive keywords
    - Sentiment intensity
    - Subjectivity
    """
    keyword_count = persuasive_data['total_count']
    polarity = abs(sentiment['polarity'])  # Absolute value - strong emotion = persuasive
    subjectivity = sentiment['subjectivity']
    
    # Weighted scoring
    keyword_score = min(keyword_count * 8, 50)  # Max 50 points from keywords
    emotion_score = polarity * 25  # Max 25 points from emotion intensity
    subjectivity_score = subjectivity * 25  # Max 25 points from subjectivity
    
    total_score = keyword_score + emotion_score + subjectivity_score
    return min(round(total_score), 100)


def calculate_ethical_score(persuasive_data, emotions, persuasion_score):
    """
    Calculate an ethical transparency score (0-100).
    Lower scores indicate potentially manipulative content.
    High fear/anger + high persuasive keywords = low ethical score
    """
    # Start with a base of 100 (perfectly ethical)
    ethical_score = 100
    
    # Penalize for excessive fear/anger (emotional manipulation)
    fear_anger = emotions.get('fear', 0) + emotions.get('anger', 0)
    ethical_score -= (fear_anger * 0.3)
    
    # Penalize for high persuasive keyword count (manipulation tactics)
    ethical_score -= (persuasive_data['total_count'] * 2)
    
    # Penalize if persuasion score is extremely high (peak manipulation)
    if persuasion_score > 80:
        ethical_score -= 15
    
    return max(round(ethical_score), 0)


def get_ethical_reflection(ethical_score, persuasion_score, emotions):
    """
    Generate a dynamic ethical reflection message based on scores.
    This is the "AI Companion" speaking.
    """
    fear_anger = emotions.get('fear', 0) + emotions.get('anger', 0)
    
    if ethical_score < 40:
        return "Persuasion is an art — but when art forgets honesty, it becomes architecture of deceit. This content sways hearts more than minds, weaponizing emotion rather than inviting reason."
    elif ethical_score < 60:
        return "This message walks the tightrope between influence and manipulation. The intent may be pure, but the methods lean on psychological pressure. Consider: what remains when urgency fades?"
    elif ethical_score < 80:
        return "A balanced approach to persuasion — using emotion and logic in harmony. The message has clear intent, but respects the reader's autonomy to choose freely."
    else:
        return "This content exemplifies ethical communication: informative, respectful, and transparent. It invites consideration without coercion — persuasion at its most honorable."


def get_persuasion_label(score):
    """
    Return the quirky, human-poetic label for persuasion score ranges.
    """
    if score <= 20:
        return "Barely convincing — like a cat selling cucumbers."
    elif score <= 40:
        return "Gentle nudge — informative, not insistent."
    elif score <= 60:
        return "Moderate persuasion — getting your attention."
    elif score <= 80:
        return "Strong pitch — the influencer's secret sauce."
    else:
        return "Peak persuasion — your neurons just signed up."


def highlight_text(text, persuasive_words, emotions):
    """
    Highlight persuasive and emotional keywords in the text.
    Returns HTML with span tags for coloring.
    """
    highlighted = text
    text_lower = text.lower()
    
    # Create a list of all words to highlight with their types
    highlight_map = []
    
    # Add persuasive keywords
    for word in set(persuasive_words):
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        for match in pattern.finditer(text):
            highlight_map.append({
                'start': match.start(),
                'end': match.end(),
                'type': 'persuasive',
                'word': match.group()
            })
    
    # Add emotion keywords
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                highlight_map.append({
                    'start': match.start(),
                    'end': match.end(),
                    'type': emotion,
                    'word': match.group()
                })
    
    # Sort by start position (reverse order for replacement)
    highlight_map.sort(key=lambda x: x['start'], reverse=True)
    
    # Apply highlights
    for item in highlight_map:
        color_class = f"highlight-{item['type']}"
        replacement = f'<span class="{color_class}">{item["word"]}</span>'
        highlighted = highlighted[:item['start']] + replacement + highlighted[item['end']:]
    
    return highlighted


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint.
    Receives text, performs all analyses, returns comprehensive results.
    """
    data = request.json
    text = data.get('text', '')
    
    if not text or len(text.strip()) < 10:
        return jsonify({'error': 'Please provide at least 10 characters of text.'}), 400
    
    # Perform TextBlob sentiment analysis
    blob = TextBlob(text)
    sentiment = {
        'polarity': round(blob.sentiment.polarity, 3),
        'subjectivity': round(blob.sentiment.subjectivity, 3)
    }
    
    # Detect persuasive keywords
    persuasive_data = detect_persuasive_keywords(text)
    
    # Analyze emotions
    emotions = analyze_emotions(text)
    
    # Calculate scores
    persuasion_score = calculate_persuasion_score(persuasive_data, sentiment)
    ethical_score = calculate_ethical_score(persuasive_data, emotions, persuasion_score)
    
    # Get labels and reflections
    persuasion_label = get_persuasion_label(persuasion_score)
    ethical_reflection = get_ethical_reflection(ethical_score, persuasion_score, emotions)
    
    # Highlight text
    highlighted_text = highlight_text(text, persuasive_data['words_found'], emotions)
    
    # Prepare response
    response = {
        'persuasion_score': persuasion_score,
        'persuasion_label': persuasion_label,
        'ethical_score': ethical_score,
        'ethical_reflection': ethical_reflection,
        'sentiment': sentiment,
        'emotions': emotions,
        'persuasive_keywords': {
            'count': persuasive_data['total_count'],
            'by_category': persuasive_data['by_category'],
            'words_found': list(set(persuasive_data['words_found']))[:10]  # Limit to 10 unique words
        },
        'highlighted_text': highlighted_text,
        'original_text': text
    }
    
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, port=5000)

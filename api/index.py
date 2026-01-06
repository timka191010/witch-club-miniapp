from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# Path to store responses
RESPONSES_FILE = 'responses.json'

def load_responses():
    """Load existing responses from file"""
    if os.path.exists(RESPONSES_FILE):
        try:
            with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_responses(responses):
    """Save responses to file"""
    with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """Serve main form page"""
    return render_template('index.html')

@app.route('/api/survey', methods=['POST'])
def survey():
    """Handle survey submission"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Имя обязательно'}), 400
        
        # Create response object
        response = {
            'timestamp': datetime.now().isoformat(),
            'name': data.get('name', '').strip(),
            'birthDate': data.get('birthDate', ''),
            'telegramUsername': data.get('telegramUsername', '').strip(),
            'familyStatus': data.get('familyStatus', ''),
            'children': data.get('children', ''),
            'interests': data.get('interests', '').strip(),
            'topics': data.get('topics', '').strip(),
            'goal': data.get('goal', '').strip(),
            'source': data.get('source', '').strip()
        }
        
        # Load existing responses
        responses = load_responses()
        
        # Add new response
        responses.append(response)
        
        # Save updated responses
        save_responses(responses)
        
        return jsonify({
            'success': True,
            'message': 'Спасибо! Ваша заявка принята.',
            'data': response
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@app.route('/api/responses', methods=['GET'])
def get_responses():
    """Get all responses (for admin dashboard)"""
    try:
        responses = load_responses()
        return jsonify({
            'success': True,
            'count': len(responses),
            'responses': responses
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get survey statistics"""
    try:
        responses = load_responses()
        
        stats = {
            'total': len(responses),
            'familyStatus': {},
            'children': {},
            'sources': {}
        }
        
        for r in responses:
            # Count family status
            status = r.get('familyStatus', 'unknown')
            stats['familyStatus'][status] = stats['familyStatus'].get(status, 0) + 1
            
            # Count children responses
            children = r.get('children', 'unknown')
            stats['children'][children] = stats['children'].get(children, 0) + 1
            
            # Count sources
            source = r.get('source', 'unknown')
            stats['sources'][source] = stats['sources'].get(source, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Witch Club API running'}), 200

if __name__ == '__main__':
    app.run(debug=True)

"""
Simple web interface for the Fash AI Agent with social media integration and user feedback
"""

from flask import Flask, render_template, request, jsonify, session
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from clothing_agent import ClothingAgent
from models.clothing_item import ClothingItem


app = Flask(__name__)
app.secret_key = 'fash-ai-agent-secret-key-2024'

# Initialize the clothing agent
agent = ClothingAgent()


@app.route('/')
def index():
    """Main page with search interface"""
    if 'user_session_id' not in session:
        session['user_session_id'] = str(uuid.uuid4())
    
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """Handle search requests"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        include_social_media = data.get('include_social_media', True)
        user_session_id = session.get('user_session_id')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Perform search
        if include_social_media:
            results = await agent.search_with_social_media(
                query, 
                user_session_id=user_session_id,
                include_trends=True,
                max_results=30
            )
        else:
            results = await agent.search(query)
        
        # Convert results to JSON-serializable format
        items_data = []
        for item in results:
            item_data = {
                'title': item.title,
                'url': item.url,
                'site': item.site,
                'price': item.price,
                'image_url': item.image_url,
                'description': item.description,
                'brand': item.brand,
                'relevance_score': item.relevance_score,
                'preference_score': item.preference_score,
                'is_on_sale': item.is_on_sale,
                'discount_percentage': item.discount_percentage
            }
            items_data.append(item_data)
        
        return jsonify({
            'success': True,
            'results': items_data,
            'count': len(items_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/trending')
def get_trending():
    """Get trending fashion content"""
    try:
        user_session_id = session.get('user_session_id')
        results = await agent.get_trending_fashion(
            user_session_id=user_session_id,
            max_results=20
        )
        
        items_data = []
        for item in results:
            item_data = {
                'title': item.title,
                'url': item.url,
                'site': item.site,
                'image_url': item.image_url,
                'description': item.description,
                'preference_score': item.preference_score
            }
            items_data.append(item_data)
        
        return jsonify({
            'success': True,
            'results': items_data,
            'count': len(items_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/inspiration', methods=['POST'])
def get_inspiration():
    """Get fashion inspiration"""
    try:
        data = request.get_json()
        style_keywords = data.get('keywords', [])
        user_session_id = session.get('user_session_id')
        
        if not style_keywords:
            return jsonify({'error': 'Style keywords are required'}), 400
        
        results = await agent.get_fashion_inspiration(
            style_keywords,
            user_session_id=user_session_id,
            max_results=20
        )
        
        items_data = []
        for item in results:
            item_data = {
                'title': item.title,
                'url': item.url,
                'site': item.site,
                'image_url': item.image_url,
                'description': item.description,
                'preference_score': item.preference_score
            }
            items_data.append(item_data)
        
        return jsonify({
            'success': True,
            'results': items_data,
            'count': len(items_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/feedback', methods=['POST'])
def record_feedback():
    """Record user feedback on an item"""
    try:
        data = request.get_json()
        item_data = data.get('item')
        feedback_type = data.get('feedback_type')  # 'like', 'dislike', 'save'
        search_query = data.get('search_query')
        user_session_id = session.get('user_session_id')
        
        if not item_data or not feedback_type:
            return jsonify({'error': 'Item data and feedback type are required'}), 400
        
        # Create ClothingItem object
        item = ClothingItem(
            title=item_data['title'],
            url=item_data['url'],
            site=item_data['site'],
            price=item_data.get('price'),
            image_url=item_data.get('image_url'),
            description=item_data.get('description'),
            brand=item_data.get('brand'),
            category=item_data.get('category')
        )
        
        # Record feedback
        agent.record_user_feedback(
            item, 
            feedback_type, 
            user_session_id, 
            search_query
        )
        
        return jsonify({
            'success': True,
            'message': f'Feedback recorded: {feedback_type}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/preferences')
def get_preferences():
    """Get user preferences summary"""
    try:
        user_session_id = session.get('user_session_id')
        if not user_session_id:
            return jsonify({'error': 'No user session found'}), 400
        
        preferences = agent.get_user_preferences_summary(user_session_id)
        
        return jsonify({
            'success': True,
            'preferences': preferences
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/recommendations')
def get_recommendations():
    """Get personalized recommendations"""
    try:
        user_session_id = session.get('user_session_id')
        if not user_session_id:
            return jsonify({'error': 'No user session found'}), 400
        
        results = agent.get_recommendations(user_session_id, max_results=20)
        
        items_data = []
        for item in results:
            item_data = {
                'title': item.title,
                'url': item.url,
                'site': item.site,
                'image_url': item.image_url,
                'description': item.description,
                'preference_score': item.preference_score
            }
            items_data.append(item_data)
        
        return jsonify({
            'success': True,
            'results': items_data,
            'count': len(items_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/seasonal/<season>')
def get_seasonal_trends(season):
    """Get seasonal fashion trends"""
    try:
        if season not in ['spring', 'summer', 'fall', 'winter']:
            return jsonify({'error': 'Invalid season'}), 400
        
        user_session_id = session.get('user_session_id')
        results = await agent.get_seasonal_trends(
            season,
            user_session_id=user_session_id,
            max_results=25
        )
        
        items_data = []
        for item in results:
            item_data = {
                'title': item.title,
                'url': item.url,
                'site': item.site,
                'image_url': item.image_url,
                'description': item.description,
                'preference_score': item.preference_score
            }
            items_data.append(item_data)
        
        return jsonify({
            'success': True,
            'results': items_data,
            'count': len(items_data),
            'season': season
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

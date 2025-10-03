# views.py
import json
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ChatSession, ChatMessage

# Your RAG service URL - update this with your team's endpoint
RAG_SERVICE_URL = "http://your-rag-service-url/api/chat"




def index(request):
    return render(request, "index.html")    

def services(request):
    return render(request, "services.html")

def about(request):
    return render(request, "about.html")



def chat(request):
    return render(request, 'chat.html')

@require_http_methods(["GET"])
def get_chat_sessions(request):
    """Get all chat sessions for the sidebar"""
    sessions = ChatSession.objects.all().order_by('-created_at')
    sessions_data = []
    
    for session in sessions:
        sessions_data.append({
            'id': session.id,
            'title': session.title,
            'message_count': session.messages.count(),
            'last_activity': session.updated_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({'sessions': sessions_data})

@require_http_methods(["GET"])
def get_chat_messages(request, session_id):
    """Get messages for a specific chat session"""
    try:
        session = ChatSession.objects.get(id=session_id)
        messages = session.messages.all().order_by('timestamp')
        
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': message.id,
                'content': message.content,
                'is_user': message.is_user,
                'timestamp': message.timestamp.strftime('%H:%M'),
                'thinking_time': message.thinking_time
            })
        
        return JsonResponse({'messages': messages_data})
    
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Chat session not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Send message to RAG service and save response"""
    try:
        data = json.loads(request.body)
        message_content = data.get('message')
        session_id = data.get('session_id')
        
        if not message_content:
            return JsonResponse({'error': 'Message content required'}, status=400)
        
        # Get or create chat session
        if session_id:
            chat_session = ChatSession.objects.get(id=session_id)
        else:
            chat_session = ChatSession.objects.create(
                title=message_content[:50] + "..." if len(message_content) > 50 else message_content
            )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=chat_session,
            content=message_content,
            is_user=True
        )
        
        # Call RAG service
        rag_payload = {
            'message': message_content,
            'session_id': str(chat_session.id)
        }
        
        try:
            # Make request to your RAG service
            response = requests.post(
                RAG_SERVICE_URL,
                json=rag_payload,
                timeout=30
            )
            response.raise_for_status()
            
            rag_response = response.json()
            ai_message_content = rag_response.get('response', 'No response from AI service')
            thinking_time = rag_response.get('thinking_time', 0)
            
        except requests.RequestException as e:
            ai_message_content = "Sorry, I'm having trouble connecting to the AI service. Please try again later."
            thinking_time = 0
            print(f"RAG service error: {e}")
        
        # Save AI response
        ai_message = ChatMessage.objects.create(
            session=chat_session,
            content=ai_message_content,
            is_user=False,
            thinking_time=thinking_time
        )
        
        return JsonResponse({
            'session_id': chat_session.id,
            'user_message': {
                'id': user_message.id,
                'content': user_message.content,
                'timestamp': user_message.timestamp.strftime('%H:%M')
            },
            'ai_message': {
                'id': ai_message.id,
                'content': ai_message.content,
                'timestamp': ai_message.timestamp.strftime('%H:%M'),
                'thinking_time': thinking_time
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_chat_session(request):
    """Create a new chat session"""
    chat_session = ChatSession.objects.create(title="New chat")
    
    return JsonResponse({
        'session_id': chat_session.id,
        'title': chat_session.title
    })
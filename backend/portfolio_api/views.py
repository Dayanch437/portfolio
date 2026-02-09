import os
import uuid
import google.generativeai as genai
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Education, Message, Profile, Project, SkillCategory, ChatSession, ChatMessage
from .serializers import (
    MessageSerializer,
    ProfileSerializer,
    ChatSessionSerializer,
)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


@api_view(["GET"])
def healthcheck(request):
    return Response({"status": "ok"})


@api_view(["GET"])
def profile_detail(request):
    try:
        profile = Profile.objects.prefetch_related(
            "stats", "education", "skills", "projects"
        ).first()
        if not profile:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProfileSerializer(profile, context={"request": request})
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def message_create(request):
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def ai_chat(request):
    """
    AI Chat endpoint using Google Gemini with session management and portfolio context.
    Expected request body: {
        "message": "your question here",
        "session_id": "optional-session-id"
    }
    """
    try:
        if not GEMINI_API_KEY:
            return Response(
                {"error": "Gemini API key not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        message = request.data.get('message', '')
        session_id = request.data.get('session_id', '')
        
        if not message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create session
        if not session_id:
            session_id = str(uuid.uuid4())
            session = ChatSession.objects.create(session_id=session_id)
        else:
            session, created = ChatSession.objects.get_or_create(session_id=session_id)
        
        # Get portfolio context
        profile = Profile.objects.prefetch_related(
            "stats", "education", "skills", "projects"
        ).first()
        
        # Build portfolio context for the AI
        context = ""
        if profile:
            context = f"""You are an AI assistant for {profile.name}'s portfolio website. 

Name: {profile.name}
Role: {profile.role}
Summary: {profile.summary}
Email: {profile.email}
"""
            
            if profile.education.exists():
                context += "\nEducation:\n"
                for edu in profile.education.all():
                    context += f"- {edu.degree} from {edu.institution} ({edu.year})"
                    if edu.gpa:
                        context += f", GPA: {edu.gpa}"
                    context += "\n"
            
            if profile.skills.exists():
                context += "\nSkills:\n"
                for skill in profile.skills.all():
                    context += f"- {skill.name}: {skill.description}\n"
            
            if profile.projects.exists():
                context += "\nProjects:\n"
                for project in profile.projects.all():
                    context += f"- {project.title}: {project.description}\n"
                    context += f"  Technologies: {project.technologies}\n"
            
            context += """\n
Your role is to:
1. Answer questions about the portfolio owner's background, skills, and projects
2. Help visitors understand their experience and capabilities
3. Provide information about their education and work
4. Be friendly, professional, and helpful
5. If asked about something not in the portfolio, politely say you don't have that information

Please provide concise, helpful responses."""
        
        # Get chat history
        chat_history = []
        previous_messages = session.messages.all()[:10]  # Last 10 messages
        
        for msg in previous_messages:
            chat_history.append({
                "role": msg.role,
                "parts": [msg.content]
            })
        
        # Initialize the Gemini model with chat
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Start or continue chat
        if chat_history:
            # Continue existing conversation
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(message)
        else:
            # Start new conversation with context
            chat = model.start_chat()
            response = chat.send_message(f"{context}\n\nUser: {message}")
        
        # Save user message
        ChatMessage.objects.create(
            session=session,
            role="user",
            content=message
        )
        
        # Save assistant response
        ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=response.text
        )
        
        return Response({
            "session_id": session_id,
            "message": message,
            "response": response.text
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
def chat_history(request, session_id):
    """
    Get chat history for a session.
    """
    try:
        session = ChatSession.objects.get(session_id=session_id)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ChatSession.DoesNotExist:
        return Response(
            {"error": "Session not found"},
            status=status.HTTP_404_NOT_FOUND
        )



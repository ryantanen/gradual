from google import genai
import os
from datetime import datetime, timedelta
from .events import get_user_events
from .email import get_user_emails
from logging import getLogger
import json

# Configure logging
logger = getLogger(__name__)

async def generate_ai_response(context: str, query: str):
    """Generate a response from Gemini AI model based on context and query."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = f"""
        {query}

        =============

        {context}
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.candidates[0].content.parts[0].text

async def generate_nodes(current_user):
    """
    Generate a list of nodes based on user's emails and calendar events.
    Returns a simple list of nodes with no complex relationships.
    """
    try:
        # Get existing nodes from user
        existing_nodes = current_user.get("nodes_tmp", [])
        
        # Define the prompt for generating nodes
        prompt = """
        Generate a list of nodes of large life events based on user's emails and calendar events. This structure represents progress over time for a person and the important big events.
        Returns a simple list of nodes with no complex relationships. Each element of the array/list is a json object which has name, long_description, date !!! IMPORTANT DATE MEANS DATE OF EVENT/EMAIL/ACTIVITY/LIFE MOMENT, like when email was sent/event occured!!!, and sequential id (index), placed in cronological order of event date. 
        Name should be 3 words max (24 chars max)

        There will be lots of junk and spam emails/non important emails, ignore them, and try and add about 1-2 per week

        IMPORTANT: You should include all the existing nodes in your output, and add any new nodes based on recent activity. Although feel free to combine nodes (stay <15ish total) Here are the existing nodes:
        """ + json.dumps(existing_nodes, indent=2)

        # Get user's events and emails for the last 30 days
        now = datetime.utcnow()
        start_date = now - timedelta(days=30)
        
        logger.info(f"Fetching data for user: {current_user}")
        
        # Get events
        try:
            events_result = await get_user_events(
                current_user=current_user,
                start_date=start_date,
                limit=100
            )
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            events_result = {"events": []}
        
        # Get emails
        try:
            emails_result = await get_user_emails(
                current_user=current_user,
                limit=100
            )
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            emails_result = {"emails": []}

        # Build context with events
        context = "Recent calendar events:\n"
        if events_result and isinstance(events_result, dict) and "events" in events_result and events_result["events"]:
            for event in events_result["events"]:
                context += f"Event: {event.get('event_name', 'Untitled')}\n"
                context += f"Date: {event.get('datetime_start')}\n"
                context += f"Description: {event.get('description', 'No description')}\n"
                if event.get('location'):
                    context += f"Location: {event['location']}\n"
                if event.get('collaborators'):
                    context += f"Collaborators: {', '.join(event['collaborators'])}\n"
                context += "\n"
        else:
            context += "No recent calendar events found.\n\n"
        
        # Add emails to context
        context += "Recent emails:\n"
        if emails_result and isinstance(emails_result, dict) and "emails" in emails_result and emails_result["emails"]:
            for email in emails_result["emails"]:
                context += f"From: {email.get('sender', 'Unknown')}\n"
                context += f"Subject: {email.get('subject', 'No subject')}\n"
                context += f"Date: {email.get('datetime')}\n"
                context += f"Content: {email.get('content', 'No content')}\n\n"
        else:
            context += "No recent emails found.\n"

        # Generate AI response with the context
        response = await generate_ai_response(context, prompt)
        
        # Parse the response as JSON
        try:
   
            # Find first [ and last ] to extract JSON array
            start_idx = response.find('[')
            end_idx = response.rfind(']')
            if start_idx != -1 and end_idx != -1:
                response = response[start_idx:end_idx + 1]
            print(response)
            nodes = json.loads(response)
           
            if isinstance(nodes, list):
                return nodes
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return []
            
    except Exception as e:
        logger.error(f"Error in generate_nodes: {e}")
        return []

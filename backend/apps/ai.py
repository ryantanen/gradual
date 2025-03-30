from google import genai
import os
from datetime import datetime, timedelta
from .events import get_user_events
from .email import get_user_emails
from .db import nodes, branches, Node, Branch, Source, users
import json
import logging
from bson import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generateAIResponse(context: str, query: str):
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

async def process_ai_response(response: str, user_id: str):
    """Process the AI response and create new nodes/branches in the database"""
    try:
        logger.info(f"Raw AI response: {response}")
        # Parse the AI response
        # Find first and last curly brace to extract JSON
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No valid JSON object found in response")
        response = response[start_idx:end_idx]
        data = json.loads(response)
        
        if data.get("count") == 0:
            logger.info("AI indicated no new nodes needed")
            return {"status": "done", "message": "No new nodes needed"}
        
        # Process new branches
        new_branches = []
        if "branches" in data:
            for branch_data in data["branches"]:
                # Check if branch already exists by name
                existing_branch = await branches.find_one({
                    "name": branch_data["name"],
                    "user_id": user_id
                })
                
                if not existing_branch:
                    branch = Branch(
                        name=branch_data["name"],
                        user_id=user_id
                    )
                    result = await branches.insert_one(branch.model_dump())
                    new_branches.append(str(result.inserted_id))
                    logger.info(f"Created new branch: {branch_data['name']}")
                else:
                    new_branches.append(str(existing_branch["_id"]))
        
        # Process new nodes
        new_nodes = []
        node_relationships = {}  # Maps AI's temporary IDs to MongoDB IDs
        
        if "nodes" in data:
            # First pass: Create all nodes without relationships
            for node_data in data["nodes"]:
                # Convert sources to proper format
                sources = []
                if "sources" in node_data:
                    for source in node_data["sources"]:
                        sources.append(Source(
                            kind=source["kind"],
                            item=source["item"]
                        ).model_dump())
                
                # Create node without relationships
                node = Node(
                    title=node_data.get("title"),
                    description=node_data.get("description"),
                    parents=[],  # Will be updated in second pass
                    children=[],  # Will be updated in second pass
                    sources=sources,
                    branch=node_data.get("branch"),
                    user_id=user_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                result = await nodes.insert_one(node.model_dump())
                node_id = str(result.inserted_id)
                new_nodes.append(node_id)
                
                # Store the relationship mapping
                if "_id" in node_data:
                    node_relationships[node_data["_id"]] = node_id
                
                logger.info(f"Created new node: {node_data.get('title', 'Untitled')}")
            
            # Second pass: Update relationships with MongoDB IDs
            for node_data in data["nodes"]:
                if "_id" in node_data:
                    mongo_id = node_relationships[node_data["_id"]]
                    
                    # Convert parent IDs
                    parents = []
                    for parent_id in node_data.get("parents", []):
                        if parent_id in node_relationships:
                            parents.append(node_relationships[parent_id])
                    
                    # Convert child IDs
                    children = []
                    for child_id in node_data.get("children", []):
                        if child_id in node_relationships:
                            children.append(node_relationships[child_id])
                    
                    # Update node with correct relationships
                    await nodes.update_one(
                        {"_id": ObjectId(mongo_id)},
                        {
                            "$set": {
                                "parents": parents,
                                "children": children
                            }
                        }
                    )
        
        # Process node updates
        if "updates" in data:
            for update_data in data["updates"]:
                node_id = update_data.get("node_id")
                if not node_id:
                    continue
                
                # Convert sources to proper format if present
                update_fields = {}
                if "description" in update_data:
                    update_fields["description"] = update_data["description"]
                if "sources" in update_data:
                    sources = []
                    for source in update_data["sources"]:
                        sources.append(Source(
                            kind=source["kind"],
                            item=source["item"]
                        ).model_dump())
                    update_fields["sources"] = sources
                
                if update_fields:
                    update_fields["updated_at"] = datetime.utcnow()
                    await nodes.update_one(
                        {"_id": ObjectId(node_id)},
                        {"$set": update_fields}
                    )
                    logger.info(f"Updated existing node: {node_id}")
        
        return {
            "status": "success",
            "new_branches": new_branches,
            "new_nodes": new_nodes
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        return {"status": "error", "message": "Invalid AI response format"}
    except Exception as e:
        logger.error(f"Error processing AI response: {e}")
        return {"status": "error", "message": str(e)}

async def generateAINodes(current_user):
    # Get emails and calendar events
    # Prompt LLM to generate nodes in a graph which will be pushed to mongoDB, which represent the
    # big events in ones life based off the data.

    prompt = """
You are a personal diary and note taking assistant. Given Email data and Event data and previous node data,
 generate the next few nodes in a graph of this users life. A node can represent a big accomplisment, a grade, or vacation. 
 Your job is to help these people keep track of all the things they have done, the good and the bad. Nodes can branch off, such as for a vacation, or simmilar event, and these branches can merge back.
 Do not add more than two branches at a time. Here is an example of a graph, you will not be generating the full graph just adding some more as needed. If you believe that no new nodes should be added, then respond with a json of {"status": "Done", "count": 0, "nodes": []}
 
 Otherwise, you will increment the count for each new node added and update the nodes list. Here is the graph example
 {
  "branches": [
    {
      "name": "Main Project",
      "user_id": "user_123",
      "root_node": "node_1"
    },
    {
      "name": "Alternative Approach",
      "user_id": "user_123",
      "root_node": "node_6"
    }
  ],
  "nodes": [
    {
      "_id": "temp_node_1",
      "title": "Introduction",
      "description": "Overview of the project",
      "branch": "branch_main",
      "parents": [],
      "children": ["temp_node_2"],
      "sources": [{ "kind": "pdf", "item": "pdf_001" }],
      "occured_at": "2025-03-20T08:00:00Z",
      "created_at": "2025-03-20T10:15:00Z",
      "root": true
    },
    {
      "_id": "temp_node_2",
      "title": "Problem Statement",
      "description": "Defining the core problem",
      "user_id": "user_123",
      "branch": "branch_main",
      "parents": ["temp_node_1"],
      "children": ["temp_node_3", "temp_node_4"],
      "sources": [{ "kind": "email", "item": "email_002" }],
      "created_at": "2025-03-21T09:30:00Z",
      "updated_at": "2025-03-21T12:00:00Z"
    }
  ],
  "updates": [
    {
      "node_id": "existing_node_id",
      "description": "Updated description with new information",
      "sources": [{ "kind": "email", "item": "new_email_001" }]
    }
  ]
}

Important notes:
1. Use temporary IDs starting with "temp_" for your nodes (e.g., "temp_node_1")
2. Reference these temporary IDs in parents and children arrays
3. The system will convert these temporary IDs to real MongoDB IDs
4. Make sure all referenced IDs exist in your nodes list
5. Branch names should be unique for the user
6. You can update existing nodes by including them in the "updates" array with their existing node_id
7. When updating nodes, only include the fields you want to update (description, sources, etc.)

The descriptions should be much longer in your response, please include as much info as you could gather about these moments in time for the user.
DO NOT MENTION YOURSELF. YOU ARE TALKING TO THE USER IN THE DESCRIPTION.

Now below this should be context on recent emails/events. Begin.
YOUR RESPONSE WILL BE PROCCESSED BY A JSON PARSER. DO NOT INCLUDE ANY OTHER TEXT. USE THE CONTEXT GIVEN! DO NOT USE CODE TO REPSENT, LITEARLY JUST TEXT.
THIS IS IN DEV MODE, TRY AND ALWAYS CREATE ATLEAST ONE NODE
"""

    # Get user's events and emails for the last 30 days
    now = datetime.utcnow()
    start_date = now - timedelta(days=30)
    
    logger.info(f"Fetching data for user: {current_user}")
    logger.info(f"Start date: {start_date}")
    
    # Get events
    try:
        events_result = await get_user_events(
            current_user=current_user,
            start_date=start_date,
            limit=100  # Limit to most recent 100 events
        )
        logger.info(f"Retrieved events: {events_result}")
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        events_result = {"events": []}
    
    # Get emails
    try:
        emails_result = await get_user_emails(
            current_user=current_user,
            limit=100  # Limit to most recent 100 emails
        )
        logger.info(f"Retrieved emails: {emails_result}")
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        emails_result = {"emails": []}

    # Get existing user nodes
    existing_nodes = await nodes.find({"user_id": str(current_user["_id"])}).to_list(None)
    logger.info(f"Retrieved existing nodes: {existing_nodes}")
    
    # Build context string with events
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

    # Add existing nodes to context
    context += "\nExisting life nodes:\n"
    if existing_nodes:
        for node in existing_nodes:
            context += f"Title: {node.get('title', 'Untitled')}\n"
            context += f"Description: {node.get('description', 'No description')}\n"
            context += f"Branch: {node.get('branch', 'Main')}\n"
            if node.get('parents'):
                context += f"Parents: {', '.join(node['parents'])}\n"
            if node.get('children'):
                context += f"Children: {', '.join(node['children'])}\n"
            context += "\n"
    else:
        context += "No existing life nodes found.\n"

    # Generate AI response with the context
    response = await generateAIResponse(prompt, context)
    logger.info(f"Generated AI response: {response}")
    
    # Process the response and create nodes/branches
    result = await process_ai_response(response, str(current_user["_id"]))
    return result

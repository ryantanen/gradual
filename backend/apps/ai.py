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
        
        # First pass: Create all nodes and store their mappings
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
                
                logger.info(f"Created new node: {node_data.get('title', 'Untitled')} with ID: {node_id}")
        
        # Process new branches with the new node IDs
        new_branches = []
        main_branch_id = None
        if "branches" in data:
            for branch_data in data["branches"]:
                # Handle root_node field - must use the MongoDB ID
                root_node_temp_id = branch_data.get("root_node")
                real_root_node_id = None
                
                # If root_node is a temporary ID, use our mapping
                if root_node_temp_id and root_node_temp_id in node_relationships:
                    real_root_node_id = node_relationships[root_node_temp_id]
                    logger.info(f"Mapped temporary root_node ID {root_node_temp_id} to real ID {real_root_node_id}")
                # If no root_node specified or mapping not found, use the first node we created
                elif new_nodes:
                    real_root_node_id = new_nodes[0]
                    logger.info(f"Using first node as root_node: {real_root_node_id}")
                
                # Check if branch already exists by name
                existing_branch = await branches.find_one({
                    "name": branch_data["name"],
                    "user_id": user_id
                })
                
                if not existing_branch:
                    branch = Branch(
                        name=branch_data["name"],
                        user_id=user_id,
                        root_node=real_root_node_id  # Use the real MongoDB ID
                    )
                    result = await branches.insert_one(branch.model_dump())
                    branch_id = str(result.inserted_id)
                    new_branches.append(branch_id)
                    logger.info(f"Created new branch: {branch_data['name']} with root_node: {real_root_node_id}")
                    
                    # Store main branch ID for later use with temp_branch_main references
                    if branch_data["name"] == "branch_main":
                        main_branch_id = branch_id
                        logger.info(f"Stored main branch ID: {main_branch_id}")
                    
                    # Update any nodes that reference this branch by name
                    for node_data in data.get("nodes", []):
                        if node_data.get("branch") == branch_data["name"] and node_data.get("_id") in node_relationships:
                            node_mongo_id = node_relationships[node_data["_id"]]
                            await nodes.update_one(
                                {"_id": ObjectId(node_mongo_id)},
                                {"$set": {"branch": branch_id}}
                            )
                            logger.info(f"Updated node {node_mongo_id} with branch ID: {branch_id}")
                else:
                    branch_id = str(existing_branch["_id"])
                    new_branches.append(branch_id)
                    
                    # Store main branch ID for later use with temp_branch_main references
                    if branch_data["name"] == "branch_main":
                        main_branch_id = branch_id
                        logger.info(f"Stored existing main branch ID: {main_branch_id}")
                    
                    # If an existing branch has no root_node, update it
                    if not existing_branch.get("root_node") and real_root_node_id:
                        await branches.update_one(
                            {"_id": existing_branch["_id"]},
                            {"$set": {"root_node": real_root_node_id}}
                        )
                        logger.info(f"Updated existing branch {branch_id} with root_node: {real_root_node_id}")
        
        # If we didn't find or create a main branch in the response, try to fetch it from DB
        if not main_branch_id:
            main_branch = await branches.find_one({
                "name": "branch_main",
                "user_id": user_id
            })
            if main_branch:
                main_branch_id = str(main_branch["_id"])
                logger.info(f"Found existing main branch ID from database: {main_branch_id}")
        
        # Update any nodes with temp_branch_main reference
        if main_branch_id:
            for node_id in new_nodes:
                node = await nodes.find_one({"_id": ObjectId(node_id)})
                if node and (node.get("branch") == "temp_branch_main" or not node.get("branch")):
                    await nodes.update_one(
                        {"_id": ObjectId(node_id)},
                        {"$set": {"branch": main_branch_id}}
                    )
                    logger.info(f"Updated node {node_id} from temp_branch_main to actual branch ID: {main_branch_id}")
            
            # Second pass: Update relationships with MongoDB IDs
            for node_data in data["nodes"]:
                if "_id" in node_data:
                    mongo_id = node_relationships[node_data["_id"]]
                    
                    # Convert parent IDs
                    parents = []
                    for parent_id in node_data.get("parents", []):
                        # Check if parent is a new node (in node_relationships) or an existing node
                        if parent_id in node_relationships:
                            parent_mongo_id = node_relationships[parent_id]
                            parents.append(parent_mongo_id)
                            # Update the parent node to include this node as a child
                            await nodes.update_one(
                                {"_id": ObjectId(parent_mongo_id)},
                                {"$addToSet": {"children": mongo_id}}
                            )
                        else:
                            # This is an existing node ID, use it directly
                            parents.append(parent_id)
                            # Update the existing parent node to include this node as a child
                            await nodes.update_one(
                                {"_id": ObjectId(parent_id)},
                                {"$addToSet": {"children": mongo_id}}
                            )
                    
                    # Convert child IDs
                    children = []
                    for child_id in node_data.get("children", []):
                        # Check if child is a new node (in node_relationships) or an existing node
                        if child_id in node_relationships:
                            child_mongo_id = node_relationships[child_id]
                            children.append(child_mongo_id)
                            # Update the child node to include this node as a parent
                            await nodes.update_one(
                                {"_id": ObjectId(child_mongo_id)},
                                {"$addToSet": {"parents": mongo_id}}
                            )
                        else:
                            # This is an existing node ID, use it directly
                            children.append(child_id)
                            # Update the existing child node to include this node as a parent
                            await nodes.update_one(
                                {"_id": ObjectId(child_id)},
                                {"$addToSet": {"parents": mongo_id}}
                            )
                    
                    # Update node with correct relationships
                    await nodes.update_one(
                        {"_id": ObjectId(mongo_id)},
                        {
                            "$set": {
                                "parents": parents,
                                "children": children,
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    logger.info(f"Updated relationships for node {mongo_id}: parents={parents}, children={children}")
        
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
        
        # Ensure root nodes are properly marked
        if new_nodes:
            for branch_id in new_branches:
                branch = await branches.find_one({"_id": ObjectId(branch_id)})
                if branch and branch.get("root_node"):
                    await nodes.update_one(
                        {"_id": ObjectId(branch["root_node"])},
                        {"$set": {"root": True}}
                    )
                    logger.info(f"Marked node {branch['root_node']} as root for branch {branch_id}")
        
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
 Your job is to help these people keep track of all the things they have done, the good and the bad. Nodes can branch off, such as for a vacation, or similar event, and these branches can merge back.
 Do not add more than one branch other than 'main' at a time. If you believe that no new nodes should be added, then respond with a json of {"status": "Done", "count": 0, "nodes": []}

CRITICAL REQUIREMENTS FOR NODE RELATIONSHIPS:
1. EVERY node MUST have at least one relationship (parent or child)
2. If a node is a follow-up or related to another node, it MUST be connected
3. Use existing nodes as parents when appropriate
4. Make relationships bidirectional (if A is a parent of B, B must be a child of A)
5. The first node in your response should be connected to the most recent existing node
6. Each subsequent node should be connected to either an existing node or a previously created node in your response

 1. Exactly one root node (no parents)
    2. Exactly one leaf node (no children)
    3. All other nodes have both parents and children
    4. Relationships are bidirectional
    5. Each branch has a valid root_node
    6. VERY IMPORTANT!!! At most 2 parents.
 
IMPORTANT NOTE: When specifying a branch for a node, always use "branch_main" as the branch name, NOT "temp_branch_main".

Here is an example of a graph with proper relationships:
 {
  "branches": [
    {
      "name": "branch_main",
      "user_id": "user_123",
      "root_node": "node_1"
    }
  ],
  "nodes": [
    {
      "_id": "temp_node_1",
      "title": "Introduction",
      "description": "Overview of the project",
      "branch": "branch_main",
      "parents": ["existing_node_123"],
      "children": ["temp_node_2"],
      "occured_at": "2025-03-20T08:00:00Z",
      "created_at": "2025-03-20T10:15:00Z"
    },
    {
      "_id": "temp_node_2",
      "title": "Problem Statement",
      "description": "Defining the core problem",
      "user_id": "user_123",
      "branch": "branch_main",
      "parents": ["temp_node_1"],
      "children": null,
      "created_at": "2025-03-21T09:30:00Z",
      "updated_at": "2025-03-21T12:00:00Z"
    }
  ]
}

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
            context += f"ID: {str(node.get('_id'))}\n"  # Add node ID to context
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

async def validate_and_clean_node_graph(graph_data: dict) -> dict:
    """
    Validates and cleans up a node graph to ensure:
    1. Exactly one root node (no parents)
    2. Exactly one leaf node (no children)
    3. All other nodes have both parents and children
    4. Relationships are bidirectional
    5. Each branch has a valid root_node
    6. At most 2 parents per node
    7. Main branch is always named "branch_main", and its ID should become "branch_main" too. 
    
    Args:
        graph_data: Dictionary containing nodes and their relationships
        
    Returns:
        Cleaned and validated graph data
    """
    try:
        # If no nodes, return the original data
        if not graph_data.get("nodes") or len(graph_data["nodes"]) == 0:
            logger.warning("No nodes found in graph data")
            return graph_data
            
        # Create a mapping of node IDs to node data
        nodes_map = {node["_id"]: node for node in graph_data["nodes"]}
        
        # STEP 1: Ensure we have a main branch named "branch_main"
        main_branch = None
        if "branches" in graph_data:
            # Look for existing main branch
            for branch in graph_data["branches"]:
                if branch.get("name") == "Main Branch" or branch.get("name") == "branch_main":
                    main_branch = branch
                    # Rename to "branch_main" if not already
                    if branch.get("name") != "branch_main":
                        branch["name"] = "branch_main"
                        logger.info(f"Renamed branch {branch['_id']} to 'branch_main'")
                    break
            
            # If no main branch found, create one or rename the first branch
            if not main_branch and graph_data["branches"]:
                main_branch = graph_data["branches"][0]
                main_branch["name"] = "branch_main"
                logger.info(f"Set first branch {main_branch['_id']} as 'branch_main'")
        else:
            # No branches at all, create a placeholder
            graph_data["branches"] = []
        
        # STEP 2: Identify or create a root node (node with no parents)
        root_node = None
        for node in graph_data["nodes"]:
            if node.get("root") is True or not node.get("parents"):
                root_node = node
                node["root"] = True
                node["parents"] = []
                logger.info(f"Found/set root node: {node['_id']}")
                break
                
        # If no root found, make the oldest node the root
        if not root_node and graph_data["nodes"]:
            root_node = graph_data["nodes"][0]
            root_node["root"] = True
            root_node["parents"] = []
            logger.info(f"No root node found, set first node as root: {root_node['_id']}")
        
        # STEP 3: Find/create a leaf node (node with no children)
        leaf_node = None
        for node in graph_data["nodes"]:
            if not node.get("children") and node["_id"] != root_node["_id"]:
                leaf_node = node
                logger.info(f"Found leaf node: {node['_id']}")
                break
                
        # If no leaf found, make the most recent node the leaf
        if not leaf_node and len(graph_data["nodes"]) > 1:
            # Try to find the newest node
            try:
                newest_nodes = sorted(
                    [n for n in graph_data["nodes"] if n["_id"] != root_node["_id"]], 
                    key=lambda x: x.get("created_at", ""),
                    reverse=True
                )
                leaf_node = newest_nodes[0]
                leaf_node["children"] = []
                logger.info(f"Set newest node as leaf: {leaf_node['_id']}")
            except Exception as e:
                logger.error(f"Error finding newest node: {e}")
                # Just use the last node in the list
                for node in graph_data["nodes"]:
                    if node["_id"] != root_node["_id"]:
                        leaf_node = node
                        leaf_node["children"] = []
                        logger.info(f"Set last non-root node as leaf: {leaf_node['_id']}")
                        break
        
        # STEP 4: Ensure every non-root node has at least one parent
        # and every non-leaf node has at least one child
        # Also ensure nodes have at most 2 parents
        for node in graph_data["nodes"]:
            # Ensure parents list exists
            if "parents" not in node:
                node["parents"] = []
                
            # Ensure children list exists
            if "children" not in node:
                node["children"] = []
                
            # Limit to at most 2 parents (except for root which has 0)
            if node["_id"] != root_node["_id"] and len(node.get("parents", [])) > 2:
                # Keep only the first 2 parents
                original_parents = node["parents"].copy()
                node["parents"] = node["parents"][:2]
                logger.info(f"Limited node {node['_id']} to 2 parents, removed: {original_parents[2:]}")
                
            # If not root and has no parents, connect to root
            if node["_id"] != root_node["_id"] and not node["parents"]:
                node["parents"] = [root_node["_id"]]
                if node["_id"] not in root_node["children"]:
                    root_node["children"].append(node["_id"])
                logger.info(f"Connected orphaned node {node['_id']} to root")
                
            # If not leaf and has no children, connect to leaf
            if leaf_node and node["_id"] != leaf_node["_id"] and not node["children"]:
                node["children"] = [leaf_node["_id"]]
                if node["_id"] not in leaf_node["parents"] and len(leaf_node["parents"]) < 2:
                    leaf_node["parents"].append(node["_id"])
                logger.info(f"Connected childless node {node['_id']} to leaf")
                
            # Ensure node belongs to main branch if branch doesn't exist
            if "branch" not in node or not node["branch"]:
                if main_branch:
                    node["branch"] = main_branch["_id"]
                    logger.info(f"Assigned node {node['_id']} to main branch")
        
        # STEP 5: Make sure relationships are bidirectional
        for node in graph_data["nodes"]:
            # For each parent, ensure this node is in their children list
            for parent_id in node["parents"]:
                if parent_id in nodes_map and node["_id"] not in nodes_map[parent_id].get("children", []):
                    nodes_map[parent_id]["children"] = nodes_map[parent_id].get("children", []) + [node["_id"]]
                    logger.info(f"Added bidirectional relationship: {parent_id} -> {node['_id']}")
            
            # For each child, ensure this node is in their parents list
            # but respect the maximum of 2 parents rule
            for child_id in node["children"]:
                if child_id in nodes_map:
                    child_node = nodes_map[child_id]
                    # Only add as parent if the child doesn't already have 2 parents
                    if node["_id"] not in child_node.get("parents", []) and len(child_node.get("parents", [])) < 2:
                        child_node["parents"] = child_node.get("parents", []) + [node["_id"]]
                        logger.info(f"Added bidirectional relationship: {node['_id']} -> {child_id}")
        
        # STEP 6: Create main branch if it doesn't exist and ensure it has a root_node
        if not main_branch:
            # Create a new main branch
            new_branch = {
                "_id": str(ObjectId()),  # Generate a temporary ID for the branch
                "name": "branch_main",
                "user_id": nodes_map[list(nodes_map.keys())[0]]["user_id"] if nodes_map else "unknown"
            }
            graph_data["branches"].append(new_branch)
            main_branch = new_branch
            logger.info("Created new main branch 'branch_main'")
        
        # Ensure main branch has a root_node
        if root_node and main_branch and not main_branch.get("root_node"):
            main_branch["root_node"] = root_node["_id"]
            logger.info(f"Set root_node in main branch to {root_node['_id']}")
            
            # Also set the root node's branch to main branch
            if "branch" not in root_node or not root_node["branch"]:
                root_node["branch"] = main_branch["_id"]
                logger.info(f"Set root node's branch to main branch")
        
        # STEP 7: Update the database with branch changes
        try:
            for branch in graph_data.get("branches", []):
                if branch.get("_id") and "root_node" in branch and branch["root_node"]:
                    # Check if this is a MongoDB ObjectId or a temporary ID
                    if ObjectId.is_valid(branch["_id"]):
                        await branches.update_one(
                            {"_id": ObjectId(branch["_id"])},
                            {"$set": {
                                "root_node": branch["root_node"],
                                "name": branch["name"]
                            }}
                        )
                        logger.info(f"Updated branch {branch['_id']} with root_node {branch['root_node']} and name {branch['name']}")
                    else:
                        # This is a new branch with a temporary ID, need to create it
                        branch_data = {
                            "name": branch["name"],
                            "user_id": branch["user_id"],
                            "root_node": branch["root_node"]
                        }
                        result = await branches.insert_one(branch_data)
                        # Update the ID in our graph data
                        branch["_id"] = str(result.inserted_id)
                        logger.info(f"Created new branch '{branch['name']}' with ID {branch['_id']}")
                        
                        # Update any nodes that reference this branch
                        for node in graph_data["nodes"]:
                            if node.get("branch") == branch.get("_id"):
                                await nodes.update_one(
                                    {"_id": ObjectId(node["_id"])},
                                    {"$set": {"branch": branch["_id"]}}
                                )
        except Exception as e:
            logger.error(f"Error updating branches: {e}")
        
        # Add metadata about changes
        changes = []
        if root_node:
            changes.append(f"Set {root_node['_id']} as root node")
        if leaf_node:
            changes.append(f"Set {leaf_node['_id']} as leaf node")
        if main_branch:
            changes.append(f"Ensured main branch is named 'branch_main'")
            
        graph_data["metadata"] = {
            "root_node": root_node["_id"] if root_node else None,
            "leaf_node": leaf_node["_id"] if leaf_node else None,
            "main_branch": main_branch["_id"] if main_branch else None,
            "changes_made": changes,
            "cleaned_at": datetime.utcnow().isoformat(),
            "total_nodes": len(graph_data["nodes"])
        }
        
        logger.info("Successfully cleaned graph structure")
        return graph_data
        
    except Exception as e:
        logger.error(f"Error cleaning node graph: {e}")
        return graph_data

from .db import users
from .email import sync_emails
from .events import sync_events
from .ai import generate_nodes
from datetime import datetime, timedelta
import logging
from bson.objectid import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_user_data(user_id: str, access_token: str):
    """Sync all data for a specific user"""
    logger.info(f"Starting sync for user {user_id}")
    
    try:
        sync_results = {
            "emails": 0,
            "events": 0,
            "status": "success"
        }
        
        # Sync emails
        try:
            logger.info(f"Starting email sync for user {user_id}")
            # sync_results["emails"] = await sync_emails(access_token, user_id, 100)
            # logger.info(f"Completed email sync: {sync_results['emails']} emails")
        except Exception as e:
            sync_results["status"] = "partial"
            sync_results["email_error"] = str(e)
            logger.error(f"Error syncing emails for user {user_id}: {str(e)}")
        
        # Sync calendar events
        try:
            logger.info(f"Starting event sync for user {user_id}")
            # Get events from previous month to 5 days ahead
            now = datetime.utcnow()
            start_time = (now - timedelta(days=30)).isoformat() + "Z"  # Previous month
            end_time = (now + timedelta(days=5)).isoformat() + "Z"     # 5 days ahead
            sync_results["events"] = await sync_events(access_token, user_id, start_time, end_time)
            logger.info(f"Completed event sync: {sync_results['events']} events")
        except Exception as e:
            sync_results["status"] = "partial"
            sync_results["event_error"] = str(e)
            logger.error(f"Error syncing events for user {user_id}: {str(e)}")
        
        # Generate nodes with AI
        try:
            logger.info(f"Starting AI processing for user {user_id}")
            # Get user document for AI processing
            current_user = await users.find_one({"_id": ObjectId(user_id)})
            if not current_user:
                raise Exception("User not found")
                
            nodes_data = await generate_nodes(current_user)
            
            # Count total nodes
            total_nodes = len(nodes_data)
            
            sync_results["ai_nodes"] = total_nodes
            # Update user's nodes_tmp field with the generated nodes
            await users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"nodes_tmp": nodes_data}}
            )
            
            logger.info(f"AI processing complete: {total_nodes} nodes generated")
            
        except Exception as e:
            sync_results["status"] = "partial" 
            sync_results["ai_error"] = str(e)
            logger.error(f"Error in AI processing for user {user_id}: {str(e)}")
        
        logger.info(f"Completed sync for user {user_id}: {sync_results}")
        return sync_results
        
    except Exception as e:
        logger.error(f"Error in sync_user_data for user {user_id}: {str(e)}")
        raise 
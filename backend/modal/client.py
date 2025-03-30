import argparse
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

import modal
from openai import OpenAI
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class Colors:
    """ANSI color codes"""

    GREEN = "\033[0;32m"
    RED = "\033[0;31m"
    BLUE = "\033[0;34m"
    GRAY = "\033[0;90m"
    BOLD = "\033[1m"
    END = "\033[0m"

async def get_content_for_summarization(
    content_type: str,
    user_id: str,
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Fetch content from MongoDB based on type and parameters"""
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    db = client.get_database("production")
    
    collection = db.get_collection(content_type)
    query = {"user_id": user_id}
    
    if start_date and end_date:
        query["datetime"] = {"$gte": start_date, "$lte": end_date}
    
    cursor = collection.find(query).sort("datetime", -1).limit(limit)
    return await cursor.to_list(length=None)

def format_content_for_prompt(content_type: str, items: List[Dict[str, Any]]) -> str:
    """Format different types of content into a prompt-friendly string"""
    if not items:
        return f"No {content_type} found for the specified criteria."
    
    formatted_content = []
    
    if content_type == "emails":
        for email in items:
            formatted_content.append(
                f"Email from {email['sender']} ({email['datetime']})\n"
                f"Subject: {email['subject']}\n"
                f"Content: {email['content'][:500]}...\n"
            )
    elif content_type == "pdfs":
        for pdf in items:
            formatted_content.append(
                f"PDF: {pdf['title'] or pdf['filename']}\n"
                f"Content: {pdf['content'][:500]}...\n"
            )
    elif content_type == "calendars":
        for event in items:
            formatted_content.append(
                f"Event: {event['event_name']}\n"
                f"Time: {event['datetime_start']} to {event['datetime_end']}\n"
                f"Location: {event['location']}\n"
                f"Description: {event['description']}\n"
                f"Attendees: {', '.join(event['collaborators'])}\n"
            )
    
    return "\n".join(formatted_content)

def get_completion(client, model_id, messages, args):
    completion_args = {
        "model": model_id,
        "messages": messages,
        "frequency_penalty": args.frequency_penalty,
        "max_tokens": args.max_tokens,
        "n": args.n,
        "presence_penalty": args.presence_penalty,
        "seed": args.seed,
        "stop": args.stop,
        "stream": args.stream,
        "temperature": args.temperature,
        "top_p": args.top_p,
    }

    completion_args = {
        k: v for k, v in completion_args.items() if v is not None
    }

    try:
        response = client.chat.completions.create(**completion_args)
        return response
    except Exception as e:
        print(Colors.RED, f"Error during API call: {e}", Colors.END, sep="")
        return None

async def summarize_content(
    content_type: str,
    user_id: str,
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    model_id: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = True,
) -> str:
    """
    Summarize content from the database using the LLM.
    
    Args:
        content_type: Type of content to summarize ("emails", "pdfs", or "calendars")
        user_id: User ID to fetch content for
        limit: Number of items to summarize (default: 10)
        start_date: Optional start date for filtering content
        end_date: Optional end date for filtering content
        model_id: Optional model ID to use (defaults to first available model)
        temperature: Temperature for LLM generation (default: 0.7)
        max_tokens: Maximum tokens to generate (default: None)
        stream: Whether to stream the response (default: True)
    
    Returns:
        str: The generated summary
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "super-secret-key"))
    
    # Set up Modal workspace and environment
    workspace = modal.config._profile
    environment = modal.config.config["environment"]
    prefix = workspace + (f"-{environment}" if environment else "")
    client.base_url = f"https://{prefix}--example-vllm-openai-compatible-serve.modal.run/v1"
    
    # Get model ID if not provided
    if not model_id:
        model = client.models.list().data[0]
        model_id = model.id
    
    # Fetch content
    content = await get_content_for_summarization(
        content_type,
        user_id,
        limit,
        start_date,
        end_date
    )
    
    # Format content for prompt
    formatted_content = format_content_for_prompt(content_type, content)
    
    # Create messages for the LLM
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides concise and informative summaries of content.",
        },
        {
            "role": "user",
            "content": f"Please provide a concise summary of the following {content_type}:\n\n{formatted_content}"
        }
    ]
    
    # Create args object for get_completion
    class Args:
        def __init__(self):
            self.frequency_penalty = 0
            self.presence_penalty = 0
            self.n = 1
            self.seed = None
            self.stop = None
            self.temperature = temperature
            self.top_p = 0.9
            self.max_tokens = max_tokens
            self.stream = stream
    
    args = Args()
    
    # Get completion from LLM
    response = get_completion(client, model_id, messages, args)
    
    if not response:
        return "Error: Failed to generate summary"
    
    if stream:
        # Handle streaming response
        summary = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                summary += chunk.choices[0].delta.content
        return summary
    else:
        # Handle non-streaming response
        return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description="OpenAI Client CLI")

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="The model to use for completion, defaults to the first available model",
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=None,
        help="The workspace where the LLM server app is hosted, defaults to your current Modal workspace",
    )
    parser.add_argument(
        "--environment",
        type=str,
        default=None,
        help="The environment in your Modal workspace where the LLM server app is hosted, defaults to your current environment",
    )
    parser.add_argument(
        "--app-name",
        type=str,
        default="example-vllm-openai-compatible",
        help="A Modal App serving an OpenAI-compatible API",
    )
    parser.add_argument(
        "--function-name",
        type=str,
        default="serve",
        help="A Modal Function serving an OpenAI-compatible API. Append `-dev` to use a `modal serve`d Function.",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default="super-secret-key",
        help="The API key to use for authentication, set in your api.py",
    )

    # Content summarization arguments
    parser.add_argument(
        "--summarize",
        type=str,
        choices=["emails", "pdfs", "calendars"],
        help="Type of content to summarize",
    )
    parser.add_argument(
        "--user-id",
        type=str,
        help="User ID to fetch content for",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of items to summarize",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date for content filtering (ISO format)",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="End date for content filtering (ISO format)",
    )

    # Completion parameters
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--top-k", type=int, default=0)
    parser.add_argument("--frequency-penalty", type=float, default=0)
    parser.add_argument("--presence-penalty", type=float, default=0)
    parser.add_argument(
        "--n",
        type=int,
        default=1,
        help="Number of completions to generate. Streaming and chat mode only support n=1.",
    )
    parser.add_argument("--stop", type=str, default=None)
    parser.add_argument("--seed", type=int, default=None)

    # Prompting
    parser.add_argument(
        "--prompt",
        type=str,
        default="Compose a limerick about baboons and racoons.",
        help="The user prompt for the chat completion",
    )
    parser.add_argument(
        "--system-prompt",
        type=str,
        default="You are a poetic assistant, skilled in writing satirical doggerel with creative flair.",
        help="The system prompt for the chat completion",
    )

    # UI options
    parser.add_argument(
        "--no-stream",
        dest="stream",
        action="store_false",
        help="Disable streaming of response chunks",
    )
    parser.add_argument(
        "--chat", action="store_true", help="Enable interactive chat mode"
    )

    args = parser.parse_args()

    if args.summarize:
        if not args.user_id:
            print(Colors.RED + "Error: --user-id is required when using --summarize" + Colors.END)
            return

        # Parse dates if provided
        start_date = datetime.fromisoformat(args.start_date) if args.start_date else None
        end_date = datetime.fromisoformat(args.end_date) if args.end_date else None

        # Use the summarize_content function
        summary = asyncio.run(summarize_content(
            content_type=args.summarize,
            user_id=args.user_id,
            limit=args.limit,
            start_date=start_date,
            end_date=end_date,
            model_id=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            stream=args.stream
        ))
        
        print(Colors.GREEN + f"\nSummarizing {args.summarize}..." + Colors.END)
        print(Colors.BLUE + f"\nSummary:\n{summary}" + Colors.END)
        return

    # Rest of the original CLI functionality...
    client = OpenAI(api_key=args.api_key)
    workspace = args.workspace or modal.config._profile
    environment = args.environment or modal.config.config["environment"]
    prefix = workspace + (f"-{environment}" if environment else "")
    client.base_url = (
        f"https://{prefix}--{args.app_name}-{args.function_name}.modal.run/v1"
    )

    if args.model:
        model_id = args.model
        print(
            Colors.BOLD,
            f"🧠: Using model {model_id}. This may trigger a model load on first call!",
            Colors.END,
            sep="",
        )
    else:
        print(
            Colors.BOLD,
            f"🔎: Looking up available models on server at {client.base_url}. This may trigger a model load!",
            Colors.END,
            sep="",
        )
        model = client.models.list().data[0]
        model_id = model.id
        print(
            Colors.BOLD,
            f"🧠: Using {model_id}",
            Colors.END,
            sep="",
        )

    messages = [
        {
            "role": "system",
            "content": args.system_prompt,
        }
    ]

    print(
        Colors.BOLD
        + "🧠: Using system prompt: "
        + args.system_prompt
        + Colors.END
    )

    if args.chat:
        print(
            Colors.GREEN
            + Colors.BOLD
            + "\nEntering chat mode. Type 'bye' to end the conversation."
            + Colors.END
        )
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["bye"]:
                break

            MAX_HISTORY = 10
            if len(messages) > MAX_HISTORY:
                messages = messages[:1] + messages[-MAX_HISTORY + 1 :]

            messages.append({"role": "user", "content": user_input})

            response = get_completion(client, model_id, messages, args)

            if response:
                if args.stream:
                    # only stream assuming n=1
                    print(Colors.BLUE + "\n🤖: ", end="")
                    assistant_message = ""
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            print(content, end="")
                            assistant_message += content
                    print(Colors.END)
                else:
                    assistant_message = response.choices[0].message.content
                    print(
                        Colors.BLUE + "\n🤖:" + assistant_message + Colors.END,
                        sep="",
                    )

                messages.append(
                    {"role": "assistant", "content": assistant_message}
                )
    else:
        messages.append({"role": "user", "content": args.prompt})
        print(Colors.GREEN + f"\nYou: {args.prompt}" + Colors.END)
        response = get_completion(client, model_id, messages, args)
        if response:
            if args.stream:
                print(Colors.BLUE + "\n🤖:", end="")
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        print(chunk.choices[0].delta.content, end="")
                print(Colors.END)
            else:
                # only case where multiple completions are returned
                for i, response in enumerate(response.choices):
                    print(
                        Colors.BLUE
                        + f"\n🤖 Choice {i + 1}:{response.message.content}"
                        + Colors.END,
                        sep="",
                    )

if __name__ == "__main__":
    main()
import asyncio
from datetime import datetime
from client import summarize_content

async def main():
    # Get summaries of different content types
    email_summary = await summarize_content(
        content_type="emails",
        user_id="67e8c05fefb58d2def6c5239",
        limit=5
    )
    print("Email Summary:", email_summary)

asyncio.run(main())
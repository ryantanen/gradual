import modal
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Create a Modal stub
stub = modal.Stub("llm-query-service")

# Create an image with the required dependencies
image = modal.Image.debian_slim().pip_install(
    "openai",
    "python-dotenv",
    "fastapi",
    "uvicorn",
    "pydantic",
)

# Create FastAPI app
web_app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@stub.function(
    image=image,
    secrets=[modal.Secret.from_name("openai-secret")],
)
@modal.asgi_app()
def fastapi_app():
    @web_app.post("/query")
    async def process_query(request: QueryRequest) -> Dict[str, str]:
        """
        Process a query using an LLM and return the response.
        
        Args:
            request (QueryRequest): The request containing the query
            
        Returns:
            Dict[str, str]: Dictionary containing the response
        """
        import os
        from openai import OpenAI
        
        # Initialize OpenAI client
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        
        try:
            # Get response from OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": request.query}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return {"response": response.choices[0].message.content}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return web_app

# For local testing
if __name__ == "__main__":
    with stub.run():
        result = process_query.remote("What is the capital of France?")
        print(result)

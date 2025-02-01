from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import json
import logging
import os

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Set the AWS profile to use
        os.environ['AWS_PROFILE'] = 'default'
        
        bedrock_runtime = boto3.client('bedrock-runtime')
        
        prompt = {
            "messages": [
                {
                    "role": "user",
                    "content": f"""Please provide a response in the following JSON format:
                    {{
                        "response": "your helpful response here",
                        "expression": "one of: neutral/happy/thinking/speaking",
                        "voice_tone": "one of: calm/excited/thoughtful"
                    }}

                    User message: {request.message}

                    Ensure the response is engaging and uses natural human vocal expressions. 
                    Use appropriate pauses, intonations, and emphasis to make the response sound more human-like."""
                }
            ],
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000
        }

        try:
            response = bedrock_runtime.invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                body=json.dumps(prompt),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            logger.info("Response from Bedrock: %s", response_body)  # Debug print
            
            if 'content' in response_body and len(response_body['content']) > 0:
                content = response_body['content'][0]['text']
                try:
                    result = json.loads(content)
                    if all(key in result for key in ['response', 'expression', 'voice_tone']):
                        return result
                    else:
                        return {
                            "response": content,
                            "expression": "neutral",
                            "voice_tone": "calm"
                        }
                except json.JSONDecodeError:
                    return {
                        "response": content,
                        "expression": "neutral",
                        "voice_tone": "calm"
                    }
            else:
                raise HTTPException(status_code=500, detail="Unexpected response format from Bedrock")
                
        except Exception as bedrock_error:
            logger.error("Bedrock API error: %s", str(bedrock_error))  # Debug print
            raise HTTPException(status_code=500, detail=f"Bedrock API error: {str(bedrock_error)}")

    except Exception as e:
        logger.error("General error: %s", str(e))  # Debug print
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
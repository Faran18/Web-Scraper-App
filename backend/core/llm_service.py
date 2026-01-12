# backend/core/llm_service.py

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# ========================================
# OPENAI CONFIGURATION
# ========================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-5-nano-2025-08-07"  # GPT-5-nano

if not OPENAI_API_KEY:
    print("⚠️ WARNING: OPENAI_API_KEY not found in environment variables!")
    print("   Please add it to your .env file")
else:
    print(f"✅ OpenAI API key loaded")
    print(f"🤖 Using model: {MODEL_NAME}")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# ========================================
# LLM INFERENCE FUNCTION
# ========================================

def run_llm(prompt: str, max_new_tokens: int = 500) -> str:
    """
    Run OpenAI GPT-5-nano for text generation.
    """
    
    try:
        print(f"🤖 Running OpenAI GPT-5-nano...")
        print(f"   Model: {MODEL_NAME}")
        print(f"   Max completion tokens: {max_new_tokens}")
        print(f"   Prompt length: {len(prompt)} characters")
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based ONLY on the provided context. Never make up information. If the context doesn't contain the answer, say so clearly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=max_new_tokens,
        )
        
        # ✅ DEBUG: Print full response object
        print(f"🔍 DEBUG - Full response:")
        print(f"   Choices: {response.choices}")
        print(f"   Finish reason: {response.choices[0].finish_reason}")
        
        # Extract response
        result = response.choices[0].message.content
        
        # ✅ DEBUG: Check if result is None or empty
        print(f"🔍 DEBUG - Raw result type: {type(result)}")
        print(f"🔍 DEBUG - Raw result value: '{result}'")
        print(f"🔍 DEBUG - Raw result repr: {repr(result)}")
        
        if result is None:
            print("⚠️ Response content is None!")
            result = ""
        
        result = result.strip() if result else ""
        
        # Get usage info
        usage = response.usage
        print(f"✅ Response generated")
        print(f"   Tokens used: {usage.total_tokens} (prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})")
        print(f"   Response length: {len(result)} characters")
        print(f"📄 Preview: {result[:150]}...")
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Error during OpenAI API call: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"

# ========================================
# CHAT WITH CONTEXT FUNCTION
# ========================================

def run_llm_with_context(context: str, question: str, max_tokens: int = 500) -> str:
    """
    Wrapper function that formats context and question into a proper prompt.
    
    Args:
        context: The scraped content/knowledge base
        question: User's question
        max_tokens: Maximum tokens to generate
        
    Returns:
        AI-generated answer
    """
    
    prompt = f"""Answer the following question based ONLY on the context provided below. 

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Use ONLY information from the context above
2. Answer in 2-3 clear, concise sentences
3. If the context doesn't contain the answer, respond with: "I don't have that information in the provided context."
4. Do NOT make up or infer information not in the context
5. Be direct and helpful

ANSWER:"""
    
    return run_llm(prompt, max_tokens)


# ========================================
# MODEL INFO
# ========================================

def get_model_info():
    """Get information about the OpenAI model"""
    
    return {
        "provider": "OpenAI",
        "model_name": MODEL_NAME,
        "model_type": "GPT-5-nano",
        "api_key_set": bool(OPENAI_API_KEY),
        "max_tokens": 16384,  # Context window (verify this for GPT-5-nano)
        "pricing": {
            "input": "$0.150 per 1M tokens",  # Update with actual GPT-5-nano pricing
            "output": "$0.600 per 1M tokens"
        },
        "limitations": {
            "temperature": "Fixed at 1.0 (not customizable)",
            "top_p": "Not supported",
            "frequency_penalty": "Not supported",
            "presence_penalty": "Not supported"
        }
    }


# ========================================
# TEST FUNCTION
# ========================================

def test_openai_connection():
    """Test if OpenAI API is working"""
    
    try:
        print("🧪 Testing OpenAI connection...")
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": "Say 'Hello, I am working!' if you can read this."}
            ],
            max_completion_tokens=20  # ✅ Changed from max_tokens
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI API is working!")
        print(f"   Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False


# Run test on import (optional)
if __name__ == "__main__":
    print("\n" + "="*60)
    print("OpenAI LLM Service - Connection Test")
    print("="*60 + "\n")
    
    info = get_model_info()
    print(f"Model: {info['model_name']}")
    print(f"API Key Set: {info['api_key_set']}")
    print(f"Max Context: {info['max_tokens']} tokens\n")
    
    if info['api_key_set']:
        test_openai_connection()
    else:
        print("⚠️ Please set OPENAI_API_KEY in your .env file")
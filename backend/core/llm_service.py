# backend/core/llm_service.py

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# ========================================
# GROQ CONFIGURATION
# ========================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"  

if not GROQ_API_KEY:
    print("⚠️ WARNING: GROQ_API_KEY not found in environment variables!")
    print("   Please add it to your .env file")
else:
    print(f"✅ Groq API key loaded")
    print(f"🤖 Using model: {MODEL_NAME}")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


# ========================================
# LLM INFERENCE FUNCTION
# ========================================

def run_llm(prompt: str, max_new_tokens: int = 500) -> str:
    """
    Run Groq LLM for text generation.
    
    Args:
        prompt: The input prompt/question with context
        max_new_tokens: Maximum tokens to generate (default: 500)
        
    Returns:
        Generated text response
    """
    
    try:
        print(f"🤖 Running Groq LLM ({MODEL_NAME})...")
        print(f"   Max tokens: {max_new_tokens}")
        print(f"   Prompt length: {len(prompt)} characters")
        
        # Call Groq API
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
            max_tokens=max_new_tokens,
            temperature=0.3,  # ✅ Groq supports temperature
            top_p=0.9,        # ✅ Groq supports top_p
        )
        
        # Extract response
        result = response.choices[0].message.content.strip()
        
        # Get usage info
        usage = response.usage
        print(f"✅ Response generated")
        print(f"   Tokens used: {usage.total_tokens} (prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})")
        print(f"   Response length: {len(result)} characters")
        print(f"📄 Preview: {result[:150]}...")
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Error during Groq API call: {str(e)}"
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
    """Get information about the Groq model"""
    
    return {
        "provider": "Groq",
        "model_name": MODEL_NAME,
        "model_type": "Llama 3.3 70B",
        "api_key_set": bool(GROQ_API_KEY),
        "max_tokens": 32768,  # Context window
        "pricing": "Free tier available",
        "features": {
            "temperature": "Supported (0-2)",
            "top_p": "Supported",
            "streaming": "Supported",
            "speed": "Very fast inference"
        }
    }


# ========================================
# TEST FUNCTION
# ========================================

def test_groq_connection():
    """Test if Groq API is working"""
    
    try:
        print("🧪 Testing Groq connection...")
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": "Say 'Hello, I am working!' if you can read this."}
            ],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        print(f"✅ Groq API is working!")
        print(f"   Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Groq API test failed: {e}")
        return False


# Run test on import (optional)
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Groq LLM Service - Connection Test")
    print("="*60 + "\n")
    
    info = get_model_info()
    print(f"Model: {info['model_name']}")
    print(f"API Key Set: {info['api_key_set']}")
    print(f"Max Context: {info['max_tokens']} tokens\n")
    
    if info['api_key_set']:
        test_groq_connection()
    else:
        print("⚠️ Please set GROQ_API_KEY in your .env file")
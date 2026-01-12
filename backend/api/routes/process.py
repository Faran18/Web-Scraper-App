# backend/api/routes/process.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.vector_db import query_similar
from backend.core.llm_service import run_llm
from backend.models.agent import Agent, ScrapeConfig

router = APIRouter()


class ProcessRequest(BaseModel):
    """Request body for chat/query endpoint"""
    agent_id: str
    query: str


@router.post("/process")
def process_data(data: ProcessRequest):
    """Chat with an agent using its knowledge base."""
    try:
        agent = Agent.get_by_id(data.agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent not found: {data.agent_id}"
            )
        
        print(f"💬 Chat with agent: {agent.name}")
        print(f"👤 User query: '{data.query}'")
        
        # Get agent's primary scrape config for URL info
        primary_config = ScrapeConfig.get_primary(data.agent_id)
        source_url = primary_config.url if primary_config else "Unknown source"
        
        # Search agent's knowledge base
        retrieval = query_similar(
            agent_id=data.agent_id,  
            text_query=data.query,
            top_k=5
        )
        
        if not retrieval.get("documents") or not retrieval["documents"][0]:
            return {
                "message": "I don't have specific information about that in my knowledge base. Could you ask something else?",
                "agent_name": agent.name,
                "source_url": source_url,
                "chunks_used": 0
            }
        
        # Filter useful chunks
        useful_chunks = []
        for chunk in retrieval["documents"][0]:
            if len(chunk) < 100:
                continue
            
            lowercase = chunk.lower()
            noise_indicators = ['copyright', 'powered by', 'quick links', 'follow us', 
                               'privacy policy', 'terms & condition', 'whatsapp us']
            
            if any(indicator in lowercase for indicator in noise_indicators):
                continue
            
            useful_chunks.append(chunk)
        
        if not useful_chunks:
            useful_chunks = retrieval["documents"][0][:2]
        
        context = "\n\n".join(useful_chunks[:5])
        chunks_used = len(useful_chunks[:5])
        
        print(f"📚 Using {chunks_used} chunks")
        print(f"📄 Context length: {len(context)} chars")
        
        # Optimized prompt for GPT-4o-mini
        prompt = f"""You are answering questions about website content. Answer based ONLY on the context below.

CONTEXT:
{context[:3000]}

QUESTION: {data.query}

CRITICAL RULES:
1. Use ONLY information from the context above
2. Answer in 2-3 clear, concise sentences
3. If the answer is not in the context, say: "I don't have that information in the provided content."
4. Do NOT make assumptions or add information not in the context
5. Be helpful and direct

ANSWER:"""
        
        print(f"🤖 Generating response...")
        response_text = run_llm(prompt, max_new_tokens=500)
        
        # ✅ CRITICAL: Ensure response is valid
        if not response_text or len(response_text.strip()) == 0:
            print("⚠️ Empty response from LLM!")
            return {
                "message": "I'm having trouble generating a response. Please try rephrasing your question.",
                "agent_name": agent.name,
                "source_url": source_url,
                "chunks_used": chunks_used
            }
        
        # Check for error messages
        if response_text.startswith("Error:") or response_text.startswith("❌"):
            print(f"⚠️ LLM error: {response_text}")
            return {
                "message": "Sorry, I encountered an error generating a response. Please try again.",
                "agent_name": agent.name,
                "source_url": source_url,
                "chunks_used": chunks_used
            }
        
        print(f"📤 Response: '{response_text[:100]}...'")
        print(f"✅ Response generated")
        
        # Return response with all required fields
        return {
            "message": response_text.strip(),
            "agent_name": agent.name,
            "source_url": source_url,
            "chunks_used": chunks_used
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        
        # Return user-friendly error instead of raising exception
        return {
            "message": "Sorry, I encountered an error. Please try again.",
            "agent_name": "Assistant",
            "source_url": "",
            "chunks_used": 0
        }


@router.post("/agents/{agent_id}/chat")
def chat_with_agent(agent_id: str, query: str):
    """Simplified chat endpoint."""
    try:
        return process_data(ProcessRequest(
            agent_id=agent_id,
            query=query
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
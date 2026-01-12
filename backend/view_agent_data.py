# backend/view_agent_data.py
"""
Simple script to view all scraped text for an agent
"""
# backend/view_agent_data.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.vector_db import get_agent_collection
from backend.models.agent import Agent

def view_agent_text(agent_id: str):
    """Show all text stored for an agent"""
    
    # Get agent info
    agent = Agent.get_by_id(agent_id)
    if not agent:
        print(f"❌ Agent not found: {agent_id}")
        return
    
    print("=" * 100)
    print(f"🤖 Agent: {agent.name}")
    print(f"📍 URL: {agent.url}")
    print(f"🆔 ID: {agent.agent_id}")
    print("=" * 100)
    print()
    
    # Get ChromaDB collection
    collection = get_agent_collection(agent_id)
    
    # Get ALL documents
    all_data = collection.get()
    
    if not all_data or not all_data.get('documents'):
        print("⚠️ No data found")
        return
    
    print(f"📦 Total chunks: {len(all_data['documents'])}")
    print()
    
    # Sort chunks by index to maintain order
    chunks_with_meta = []
    for doc, meta in zip(all_data['documents'], all_data['metadatas']):
        chunks_with_meta.append({
            'text': doc,
            'index': meta.get('chunk_index', 0),
            'url': meta.get('source_url', '')
        })
    
    # Sort by chunk index
    chunks_with_meta.sort(key=lambda x: x['index'])
    
    print("=" * 100)
    print("📄 FULL SCRAPED TEXT:")
    print("=" * 100)
    print()
    
    # Print each chunk with separator
    for i, chunk in enumerate(chunks_with_meta):
        print(f"[Chunk {i}]")
        print(chunk['text'])
        print()
        print("-" * 100)
        print()
    
    # Also show combined text
    print()
    print("=" * 100)
    print("📝 COMBINED TEXT (all chunks together):")
    print("=" * 100)
    print()
    
    combined_text = ''.join(chunk['text'] for chunk in chunks_with_meta)
    print(combined_text)
    
    print()
    print("=" * 100)
    print(f"📊 Total characters: {len(combined_text)}")
    print(f"📊 Total words: {len(combined_text.split())}")
    print("=" * 100)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python backend/view_agent_data.py <agent_id>")
        print("\nExample: python backend/view_agent_data.py e8b05883-c8f7-4cf6-8d7d-ea84860a2352")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    view_agent_text(agent_id)
# backend/show_scraped_text.py
"""
Script to reconstruct and display the complete scraped text from ChromaDB chunks.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import textwrap
from collections import defaultdict
from backend.core.vector_db import get_agent_collection
from backend.models.agent import Agent, ScrapeConfig


def show_full_scraped_text(agent_id: str, wrap_width: int = 100, show_metadata: bool = True):
    """
    Reconstruct and display the complete scraped text for an agent.
    """
    
    print("=" * 120)
    print("📄 FULL SCRAPED TEXT VIEWER")
    print("=" * 120)
    
    # Get agent info
    agent = Agent.get_by_id(agent_id)
    
    if not agent:
        print(f"❌ Agent not found: {agent_id}")
        return
    
    # Get scrape configs
    configs = ScrapeConfig.get_by_agent(agent_id)
    primary_config = next((c for c in configs if c.is_primary), None)
    
    print(f"\n🤖 Agent: {agent.name}")
    print(f"   ID: {agent.agent_id}")
    print(f"   Primary URL: {primary_config.url if primary_config else 'No URL configured'}")
    print(f"   Status: {agent.status}")
    print()
    
    # Get agent's collection
    collection = get_agent_collection(agent_id)
    
    # Get all data
    all_data = collection.get()
    
    if not all_data or not all_data.get('documents'):
        print("⚠️  No scraped data found for this agent")
        return
    
    print(f"📊 Total Chunks Stored: {len(all_data['documents'])}")
    
    # Group chunks by scrape_id (each scraping session)
    scrapes = defaultdict(lambda: {"chunks": [], "metadata": None})
    
    for i, (doc_id, document, metadata) in enumerate(zip(
        all_data['ids'],
        all_data['documents'],
        all_data['metadatas']
    )):
        scrape_id = metadata.get('scrape_id', 'unknown')
        chunk_index = metadata.get('chunk_index', 0)
        
        scrapes[scrape_id]["chunks"].append({
            "index": chunk_index,
            "text": document,
            "id": doc_id
        })
        
        if scrapes[scrape_id]["metadata"] is None:
            scrapes[scrape_id]["metadata"] = metadata
    
    print(f"📦 Unique Scraping Sessions: {len(scrapes)}")
    print()
    
    # Display each scraping session
    for scrape_num, (scrape_id, scrape_data) in enumerate(scrapes.items(), 1):
        print("=" * 120)
        print(f"📥 SCRAPING SESSION #{scrape_num}")
        print("=" * 120)
        
        metadata = scrape_data["metadata"]
        chunks = sorted(scrape_data["chunks"], key=lambda x: x["index"])
        
        if show_metadata:
            print(f"\n📋 Metadata:")
            print(f"   Scrape ID:     {scrape_id}")
            print(f"   Source URL:    {metadata.get('source_url', 'N/A')}")
            print(f"   Total Chunks:  {len(chunks)}")
            
            if metadata.get('css_selector'):
                print(f"   CSS Selector:  {metadata.get('css_selector')}")
            if metadata.get('xpath'):
                print(f"   XPath:         {metadata.get('xpath')}")
            
            print()
        
        print("─" * 120)
        print("📝 COMPLETE SCRAPED TEXT:")
        print("─" * 120)
        print()
        
        # Reconstruct full text from chunks
        full_text = ""
        for chunk in chunks:
            full_text += chunk["text"]
        
        # Display text
        if wrap_width > 0:
            wrapped = textwrap.fill(full_text, width=wrap_width)
            print(wrapped)
        else:
            print(full_text)
        
        print()
        print("─" * 120)
        print(f"📊 Statistics:")
        print(f"   Total Characters: {len(full_text):,}")
        print(f"   Total Words:      {len(full_text.split()):,}")
        print(f"   Total Lines:      {len(full_text.splitlines()):,}")
        print(f"   Chunks Used:      {len(chunks)}")
        print("─" * 120)
        print()


def show_all_agents_text(wrap_width: int = 100):
    """Show scraped text for all agents"""
    
    agents = Agent.get_all()
    
    if not agents:
        print("⚠️  No agents found")
        return
    
    for agent_num, agent in enumerate(agents, 1):
        show_full_scraped_text(agent.agent_id, wrap_width=wrap_width, show_metadata=True)
        
        if agent_num < len(agents):
            print("\n\n")
            print("🔽" * 40)
            print("\n\n")


def export_to_file(agent_id: str, output_file: str = None):
    """Export scraped text to a file."""
    
    agent = Agent.get_by_id(agent_id)
    
    if not agent:
        print(f"❌ Agent not found: {agent_id}")
        return
    
    if output_file is None:
        output_file = f"agent_{agent_id}_scraped.txt"
    
    configs = ScrapeConfig.get_by_agent(agent_id)
    primary_config = next((c for c in configs if c.is_primary), None)
    
    collection = get_agent_collection(agent_id)
    all_data = collection.get()
    
    if not all_data or not all_data.get('documents'):
        print("⚠️  No scraped data found")
        return
    
    # Group by scrape_id
    scrapes = defaultdict(lambda: {"chunks": [], "metadata": None})
    
    for doc_id, document, metadata in zip(
        all_data['ids'],
        all_data['documents'],
        all_data['metadatas']
    ):
        scrape_id = metadata.get('scrape_id', 'unknown')
        chunk_index = metadata.get('chunk_index', 0)
        
        scrapes[scrape_id]["chunks"].append({
            "index": chunk_index,
            "text": document
        })
        
        if scrapes[scrape_id]["metadata"] is None:
            scrapes[scrape_id]["metadata"] = metadata
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Agent: {agent.name}\n")
        f.write(f"Agent ID: {agent.agent_id}\n")
        f.write(f"Primary URL: {primary_config.url if primary_config else 'N/A'}\n")
        f.write(f"Status: {agent.status}\n")
        f.write(f"\n{'=' * 80}\n\n")
        
        for scrape_num, (scrape_id, scrape_data) in enumerate(scrapes.items(), 1):
            metadata = scrape_data["metadata"]
            chunks = sorted(scrape_data["chunks"], key=lambda x: x["index"])
            
            f.write(f"SCRAPING SESSION #{scrape_num}\n")
            f.write(f"{'=' * 80}\n\n")
            f.write(f"Scrape ID: {scrape_id}\n")
            f.write(f"Source URL: {metadata.get('source_url', 'N/A')}\n")
            f.write(f"Total Chunks: {len(chunks)}\n")
            
            if metadata.get('css_selector'):
                f.write(f"CSS Selector: {metadata.get('css_selector')}\n")
            if metadata.get('xpath'):
                f.write(f"XPath: {metadata.get('xpath')}\n")
            
            f.write(f"\n{'-' * 80}\n")
            f.write("COMPLETE TEXT:\n")
            f.write(f"{'-' * 80}\n\n")
            
            full_text = "".join(chunk["text"] for chunk in chunks)
            f.write(full_text)
            
            f.write(f"\n\n{'-' * 80}\n")
            f.write(f"Statistics:\n")
            f.write(f"  Characters: {len(full_text):,}\n")
            f.write(f"  Words: {len(full_text.split()):,}\n")
            f.write(f"  Lines: {len(full_text.splitlines()):,}\n")
            f.write(f"{'-' * 80}\n\n\n")
    
    print(f"✅ Exported to: {output_file}")
    print(f"   Agent: {agent.name}")
    print(f"   Scraping Sessions: {len(scrapes)}")
    print(f"   Total Chunks: {len(all_data['documents'])}")

def show_individual_chunks(agent_id: str):
    """Display each chunk separately with metadata"""
    
    print("=" * 120)
    print("📦 INDIVIDUAL CHUNKS VIEWER")
    print("=" * 120)
    
    agent = Agent.get_by_id(agent_id)
    
    if not agent:
        print(f"❌ Agent not found: {agent_id}")
        return
    
    configs = ScrapeConfig.get_by_agent(agent_id)
    primary_config = next((c for c in configs if c.is_primary), None)
    
    print(f"\n🤖 Agent: {agent.name}")
    print(f"   ID: {agent.agent_id}")
    print(f"   Primary URL: {primary_config.url if primary_config else 'No URL'}")
    print()
    
    collection = get_agent_collection(agent_id)
    all_data = collection.get()
    
    if not all_data or not all_data.get('documents'):
        print("⚠️  No scraped data found")
        return
    
    print(f"📊 Total Chunks: {len(all_data['documents'])}\n")
    
    # Group by scrape_id
    scrapes = defaultdict(lambda: {"chunks": [], "metadata": None})
    
    for doc_id, document, metadata in zip(
        all_data['ids'],
        all_data['documents'],
        all_data['metadatas']
    ):
        scrape_id = metadata.get('scrape_id', 'unknown')
        chunk_index = metadata.get('chunk_index', 0)
        
        scrapes[scrape_id]["chunks"].append({
            "index": chunk_index,
            "text": document,
            "id": doc_id,
            "metadata": metadata
        })
        
        if scrapes[scrape_id]["metadata"] is None:
            scrapes[scrape_id]["metadata"] = metadata
    
    # Display each scraping session
    for scrape_num, (scrape_id, scrape_data) in enumerate(scrapes.items(), 1):
        print("=" * 120)
        print(f"📥 SCRAPING SESSION #{scrape_num}")
        print(f"   Scrape ID: {scrape_id}")
        print("=" * 120)
        print()
        
        chunks = sorted(scrape_data["chunks"], key=lambda x: x["index"])
        
        for chunk in chunks:
            print("─" * 120)
            print(f"📦 CHUNK #{chunk['index'] + 1} of {len(chunks)}")
            print("─" * 120)
            print(f"   Chunk ID: {chunk['id']}")
            print(f"   Length: {len(chunk['text'])} characters")
            print(f"   Source: {chunk['metadata'].get('source_url', 'N/A')}")
            print()
            print(chunk['text'])
            print()
        
        print("=" * 120)
        print(f"📊 Session Summary:")
        print(f"   Total Chunks: {len(chunks)}")
        print(f"   Total Characters: {sum(len(c['text']) for c in chunks):,}")
        print("=" * 120)
        print()


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backend/show_scraped_text.py <agent_id>                    # Show full text")
        print("  python backend/show_scraped_text.py <agent_id> --chunks           # Show individual chunks")
        print("  python backend/show_scraped_text.py <agent_id> --no-wrap          # No text wrapping")
        print("  python backend/show_scraped_text.py <agent_id> --export [file]    # Export to file")
        print("  python backend/show_scraped_text.py --all                         # Show all agents")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "--all":
        show_all_agents_text(wrap_width=100)
    else:
        agent_id = command
        
        if len(sys.argv) > 2:
            option = sys.argv[2]
            
            if option == "--chunks":
                show_individual_chunks(agent_id)  # ← NEW
            elif option == "--no-wrap":
                show_full_scraped_text(agent_id, wrap_width=0)
            elif option == "--export":
                output_file = sys.argv[3] if len(sys.argv) > 3 else None
                export_to_file(agent_id, output_file)
            else:
                print(f"Unknown option: {option}")
        else:
            show_full_scraped_text(agent_id, wrap_width=100)
# backend/core/check_database.py
from chromadb import PersistentClient
import textwrap
from collections import defaultdict

VECTOR_DIR = "E:/web_scraper/data/vectors"

def check_chroma(show_full_text=True, limit=10, search_url=None):
    """
    Check ChromaDB contents with various options
    
    Args:
        show_full_text: Show complete text or just preview
        limit: Number of documents to display
        search_url: Filter by specific URL (optional)
    """
    client = PersistentClient(path=VECTOR_DIR)
    collection = client.get_or_create_collection("web_pages")
    
    print("✅ Connected to Chroma collection")
    print(f"📦 Total stored embeddings: {collection.count()}")
    print("=" * 100)
    
    # Fetch documents
    results = collection.get(limit=limit)

    if not results or not results.get("ids"):
        print("⚠️ No documents found in collection.")
        return
    
    # Group by URL
    urls_dict = defaultdict(list)
    for i, metadata in enumerate(results["metadatas"]):
        url = metadata.get("source_url", "Unknown")
        urls_dict[url].append({
            "id": results["ids"][i],
            "doc": results["documents"][i],
            "chunk": metadata.get("chunk_index", "N/A"),
            "metadata": metadata
        })
    
    # Display URL summary
    print(f"\n📊 STORED URLS ({len(urls_dict)} unique URLs):\n")
    print("─" * 100)
    for idx, (url, chunks) in enumerate(urls_dict.items(), 1):
        if search_url and search_url.lower() not in url.lower():
            continue
        print(f"{idx}. 🔗 {url}")
        print(f"   📦 Chunks: {len(chunks)} | Characters: {sum(len(c['doc']) for c in chunks)}")
        print("─" * 100)
    
    # Display documents
    print(f"\n📄 DOCUMENT DETAILS:\n")
    
    for i, doc in enumerate(results["documents"], 1):
        metadata = results["metadatas"][i-1]
        doc_id = results["ids"][i-1]
        url = metadata.get("source_url", "N/A")
        
        # Filter by URL if specified
        if search_url and search_url.lower() not in url.lower():
            continue
        
        print(f"\n{'═' * 100}")
        print(f"📄 DOCUMENT #{i}")
        print(f"{'═' * 100}")
        print(f"🆔 ID:           {doc_id}")
        print(f"🔗 Source URL:   {url}")
        print(f"📦 Chunk Index:  {metadata.get('chunk_index', 'N/A')}")
        
        # Show CSS/XPath if available
        if metadata.get('css_selector'):
            print(f"🎯 CSS Selector: {metadata.get('css_selector')}")
        if metadata.get('xpath'):
            print(f"🎯 XPath:        {metadata.get('xpath')}")
        
        print(f"{'─' * 100}")
        
        if show_full_text:
            print(f"📝 FULL TEXT:")
            print(f"{'─' * 100}")
            wrapped_text = textwrap.fill(doc, width=95, initial_indent="   ", subsequent_indent="   ")
            print(wrapped_text)
        else:
            print(f"📝 PREVIEW (first 200 chars):")
            print(f"{'─' * 100}")
            print(f"   {doc[:200]}...")
        
        print(f"{'─' * 100}")
        print(f"📊 Character count: {len(doc)}")
        print(f"{'═' * 100}")
    
    print("\n" + "=" * 100)
    print("✅ Database check complete!")
    print("=" * 100)


def list_all_urls():
    """Quick function to list all stored URLs"""
    client = PersistentClient(path=VECTOR_DIR)
    collection = client.get_or_create_collection("web_pages")
    
    results = collection.get()
    
    if not results or not results.get("metadatas"):
        print("⚠️ No documents found.")
        return
    
    urls = set()
    for metadata in results["metadatas"]:
        urls.add(metadata.get("source_url", "Unknown"))
    
    print(f"\n📋 All Stored URLs ({len(urls)} unique):\n")
    for idx, url in enumerate(sorted(urls), 1):
        print(f"{idx}. {url}")


def search_content(query: str):
    """Search for content using semantic similarity"""
    client = PersistentClient(path=VECTOR_DIR)
    collection = client.get_or_create_collection("web_pages")
    
    print(f"🔍 Searching for: '{query}'")
    print("=" * 100)
    
    results = collection.query(query_texts=[query], n_results=5)
    
    if not results or not results.get("documents"):
        print("⚠️ No matching documents found.")
        return
    
    for i, doc in enumerate(results["documents"][0], 1):
        metadata = results["metadatas"][0][i-1]
        distance = results["distances"][0][i-1] if results.get("distances") else "N/A"
        
        print(f"\n{'─' * 100}")
        print(f"📄 Result #{i} (Similarity: {1 - distance:.3f})")
        print(f"{'─' * 100}")
        print(f"🔗 URL: {metadata.get('source_url', 'N/A')}")
        print(f"📦 Chunk: {metadata.get('chunk_index', 'N/A')}")
        print(f"📝 Content:\n   {doc[:300]}...")
        print(f"{'─' * 100}")


def clear_database():
    """Delete all documents from the database"""
    response = input("⚠️  Are you sure you want to clear ALL data? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Cancelled.")
        return
    
    client = PersistentClient(path=VECTOR_DIR)
    collection = client.get_or_create_collection("web_pages")
    
    # Get all IDs
    results = collection.get()
    if results and results.get("ids"):
        collection.delete(ids=results["ids"])
        print(f"✅ Deleted {len(results['ids'])} documents.")
    else:
        print("⚠️ Database is already empty.")


# Main menu
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_all_urls()
        elif command == "search" and len(sys.argv) > 2:
            search_content(" ".join(sys.argv[2:]))
        elif command == "clear":
            clear_database()
        elif command == "preview":
            check_chroma(show_full_text=False, limit=20)
        elif command == "url" and len(sys.argv) > 2:
            check_chroma(show_full_text=True, limit=50, search_url=sys.argv[2])
        else:
            print("Usage:")
            print("  python check_database.py list          - List all URLs")
            print("  python check_database.py search <query> - Search content")
            print("  python check_database.py preview       - Show previews only")
            print("  python check_database.py url <url>     - Filter by URL")
            print("  python check_database.py clear         - Clear database")
            print("  python check_database.py               - Show full database")
    else:
        # Default: show full database
        check_chroma(show_full_text=True, limit=20)
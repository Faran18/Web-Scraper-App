# backend/utils/multi_page_scraper.py

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from backend.utils.playwright_scraper import extract_text_from_html
import time


def is_same_domain(url1, url2):
    """Check if two URLs are from the same domain"""
    return urlparse(url1).netloc == urlparse(url2).netloc


def scrape_multiple_pages(start_url: str, max_pages: int = 20, 
                          css_selector: str = None, xpath: str = None):
    """
    Crawl multiple pages starting from a URL.
    
    Returns:
        dict: {
            'pages': [
                {'url': '...', 'text': '...', 'title': '...'},
                ...
            ],
            'total_pages': int,
            'total_chars': int
        }
    """
    
    visited_urls = set()
    to_visit = [start_url]
    pages_data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Block resources
        page.route("**/*", lambda route: route.abort()
                   if route.request.resource_type in ["stylesheet", "font", "image", "media"]
                   else route.continue_())
        
        while to_visit and len(visited_urls) < max_pages:
            current_url = to_visit.pop(0)
            
            # Skip if already visited
            if current_url in visited_urls:
                continue
            
            # Skip if different domain
            if not is_same_domain(current_url, start_url):
                continue
            
            try:
                print(f"🔍 Scraping ({len(visited_urls) + 1}/{max_pages}): {current_url}")
                
                page.goto(current_url, timeout=30000, wait_until="domcontentloaded")
                page.wait_for_timeout(1000)
                
                html_content = page.content()
                
                # Extract text
                text = extract_text_from_html(html_content, css_selector, xpath)
                
                # Get page title
                title = page.title()
                
                if text and len(text) > 100:  # Only save pages with substantial content
                    pages_data.append({
                        'url': current_url,
                        'text': text,
                        'title': title,
                        'char_count': len(text)
                    })
                
                visited_urls.add(current_url)
                
                # Find links on the page
                soup = BeautifulSoup(html_content, 'html.parser')
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link['href']
                    absolute_url = urljoin(current_url, href)
                    
                    # Add to queue if not visited and same domain
                    if (absolute_url not in visited_urls and 
                        absolute_url not in to_visit and
                        is_same_domain(absolute_url, start_url) and
                        not absolute_url.endswith(('.pdf', '.jpg', '.png', '.zip'))):
                        to_visit.append(absolute_url)
                
                time.sleep(0.5)  # Be polite
                
            except Exception as e:
                print(f"⚠️ Error scraping {current_url}: {e}")
                continue
        
        browser.close()
    
    total_chars = sum(p['char_count'] for p in pages_data)
    
    return {
        'pages': pages_data,
        'total_pages': len(pages_data),
        'total_chars': total_chars
    }
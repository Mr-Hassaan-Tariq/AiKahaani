"""
Article Content Scraper Service

This service scrapes article content from URLs using multiple fallback methods:
1. newspaper3k - best for news articles and blog posts
2. BeautifulSoup - fallback for general web pages

Handles various edge cases and provides detailed error messages.
"""

import logging
import requests
from typing import Tuple
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Try to import newspaper3k (optional dependency)
try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False
    logger.warning("[ARTICLE_SCRAPER] newspaper3k not installed. Using BeautifulSoup only.")


class ArticleScraperService:
    """Service for scraping article content from URLs"""
    
    # Maximum content length to avoid token limits
    MAX_CONTENT_LENGTH = 3000
    
    # Request timeout in seconds
    REQUEST_TIMEOUT = 10
    
    # User agent for requests
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    @classmethod
    def scrape_article(cls, article_url: str) -> Tuple[str, str]:
        """
        Scrape article content from URL using multiple methods
        
        Args:
            article_url: URL of the article to scrape
            
        Returns:
            Tuple of (title, content)
            
        Raises:
            Exception: If scraping fails or content is insufficient
        """
        logger.info(f"[ARTICLE_SCRAPER] Starting scrape for URL: {article_url}")
        
        # Method 1: Try newspaper3k (best for news articles)
        if NEWSPAPER_AVAILABLE:
            try:
                title, content = cls._scrape_with_newspaper(article_url)
                if content and len(content.strip()) > 100:
                    logger.info(
                        f"[ARTICLE_SCRAPER] ✅ Success with newspaper3k - "
                        f"Title: '{title[:50]}...', Content length: {len(content)}"
                    )
                    return cls._process_content(title, content)
            except Exception as e:
                logger.warning(f"[ARTICLE_SCRAPER] newspaper3k failed: {str(e)}, trying BeautifulSoup...")
        
        # Method 2: Fallback to BeautifulSoup
        try:
            title, content = cls._scrape_with_beautifulsoup(article_url)
            if content and len(content.strip()) > 100:
                logger.info(
                    f"[ARTICLE_SCRAPER] ✅ Success with BeautifulSoup - "
                    f"Title: '{title[:50]}...', Content length: {len(content)}"
                )
                return cls._process_content(title, content)
            else:
                raise Exception("Insufficient content extracted")
        except Exception as e:
            # Log technical details for debugging but don't expose to users
            logger.error(f"[ARTICLE_SCRAPER] ❌ All methods failed: {str(e)}", exc_info=True)
            raise Exception(
                "Unable to fetch article content. Please try a different article URL or use text description instead."
            )
    
    @classmethod
    def _scrape_with_newspaper(cls, article_url: str) -> Tuple[str, str]:
        """
        Scrape article using newspaper3k library
        
        Args:
            article_url: URL of the article
            
        Returns:
            Tuple of (title, content)
        """
        article = Article(article_url)
        article.download()
        article.parse()
        
        title = article.title or "Article Content"
        content = article.text or ""
        
        return title, content
    
    @classmethod
    def _scrape_with_beautifulsoup(cls, article_url: str) -> Tuple[str, str]:
        """
        Scrape article using BeautifulSoup
        
        Args:
            article_url: URL of the article
            
        Returns:
            Tuple of (title, content)
        """
        headers = {'User-Agent': cls.USER_AGENT}
        response = requests.get(article_url, headers=headers, timeout=cls.REQUEST_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = cls._extract_title(soup)
        
        # Extract main content
        content = cls._extract_content(soup)
        
        return title, content
    
    @classmethod
    def _extract_title(cls, soup: BeautifulSoup) -> str:
        """
        Extract title from HTML soup
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Article title
        """
        # Try multiple methods to find title
        title_tags = [
            soup.find('h1'),
            soup.find('title'),
            soup.find('meta', property='og:title'),
            soup.find('meta', attrs={'name': 'title'}),
        ]
        
        for tag in title_tags:
            if tag:
                if tag.name == 'meta':
                    title = tag.get('content', '').strip()
                else:
                    title = tag.get_text().strip()
                
                if title:
                    return title
        
        return "Article Content"
    
    @classmethod
    def _extract_content(cls, soup: BeautifulSoup) -> str:
        """
        Extract main content from HTML soup
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Article content
        """
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()
        
        # Try to find main content areas with common class/id patterns
        content_selectors = [
            ('article', None),
            ('main', None),
            ('div', lambda x: x and any(
                keyword in str(x).lower() 
                for keyword in ['content', 'article', 'post-body', 'entry-content', 'story-body']
            )),
        ]
        
        for tag_name, class_filter in content_selectors:
            if class_filter:
                content_areas = soup.find_all(tag_name, class_=class_filter)
            else:
                content_areas = soup.find_all(tag_name)
            
            if content_areas:
                # Get text from the first matching area
                content = content_areas[0].get_text(separator=' ', strip=True)
                if len(content) > 100:
                    return cls._clean_text(content)
        
        # Fallback: get all paragraphs
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs])
        return cls._clean_text(content)
    
    @classmethod
    def _clean_text(cls, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        return ' '.join(text.split())
    
    @classmethod
    def _process_content(cls, title: str, content: str) -> Tuple[str, str]:
        """
        Process and truncate content if necessary
        
        Args:
            title: Article title
            content: Article content
            
        Returns:
            Tuple of (title, processed_content)
        """
        # Truncate content if too long
        if len(content) > cls.MAX_CONTENT_LENGTH:
            content = content[:cls.MAX_CONTENT_LENGTH] + "... (content truncated for brevity)"
            logger.info(f"[ARTICLE_SCRAPER] Content truncated to {cls.MAX_CONTENT_LENGTH} characters")
        
        return title, content


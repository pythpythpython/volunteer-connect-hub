#!/usr/bin/env python3
"""
VolunteerConnect Hub - Opportunity Crawler Script
==================================================

Crawls volunteer opportunities from multiple sources:
- VolunteerMatch API (primary source)
- Idealist RSS feeds
- Public nonprofit APIs
- Curated listings from major organizations

Powered by: OpportunityCrawlerAGI Board

Usage:
    python crawl_opportunities.py --source all
    python crawl_opportunities.py --source volunteermatch --dry-run
"""

import os
import sys
import json
import argparse
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import requests
    from bs4 import BeautifulSoup
    import feedparser
except ImportError:
    print("Required packages not installed. Run: pip install requests beautifulsoup4 feedparser")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CrawledOpportunity:
    """A volunteer opportunity from any source."""
    id: str = ""
    source: str = ""
    source_id: str = ""
    source_url: str = ""
    title: str = ""
    organization: str = ""
    organization_url: str = ""
    description: str = ""
    requirements: str = ""
    location_city: str = ""
    location_state: str = ""
    location_country: str = "United States"
    is_virtual: bool = False
    cause_areas: List[str] = field(default_factory=list)
    skills_needed: List[str] = field(default_factory=list)
    populations_served: List[str] = field(default_factory=list)
    commitment_type: str = "ongoing"
    hours_per_week_min: int = 0
    hours_per_week_max: int = 0
    background_check_required: bool = False
    training_provided: bool = False
    min_age: int = 0
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def generate_id(self) -> str:
        """Generate unique ID from source and content."""
        content = f"{self.source}:{self.source_id or self.title}:{self.organization}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VolunteerMatchCrawler:
    """
    Crawler for VolunteerMatch API.
    
    VolunteerMatch API Documentation:
    https://www.volunteermatch.org/business/api/
    
    API Features:
    - Search by location, cause area, skills
    - Filter by virtual/in-person
    - Pagination support
    - Rate limiting considerations
    """
    
    BASE_URL = "https://www.volunteermatch.org/api/call"
    
    # Cause area mapping from VolunteerMatch categories
    CAUSE_MAPPING = {
        1: "education",
        2: "environment",
        3: "animals",
        4: "health",
        5: "hunger",
        6: "housing",
        7: "seniors",
        8: "children",
        9: "arts",
        10: "community",
        11: "disaster",
        12: "veterans",
        13: "immigrants",
        14: "justice",
        15: "disability",
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('VOLUNTEERMATCH_API_KEY')
        self.session = requests.Session()
        
    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)
    
    def search_opportunities(
        self,
        location: str = "United States",
        virtual: Optional[bool] = None,
        categories: Optional[List[int]] = None,
        page_size: int = 20,
        page_number: int = 1
    ) -> List[CrawledOpportunity]:
        """
        Search VolunteerMatch for opportunities.
        
        Note: Requires API key. Without it, returns placeholder.
        """
        if not self.is_available():
            logger.warning("VolunteerMatch API key not configured. Using sample data.")
            return self._get_sample_opportunities()
        
        opportunities = []
        
        try:
            # Build API request
            params = {
                "key": self.api_key,
                "query": json.dumps({
                    "location": location,
                    "numberOfResults": page_size,
                    "pageNumber": page_number,
                    "fieldsToDisplay": [
                        "id", "title", "description", "plaintextDescription",
                        "greatFor", "categoryIds", "requiresDriversLicense",
                        "skillsNeeded", "virtual", "location", "parentOrg",
                        "vmUrl"
                    ]
                })
            }
            
            if virtual is not None:
                params["query"]["virtual"] = virtual
            if categories:
                params["query"]["categoryIds"] = categories
            
            # Make API request
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for opp_data in data.get("opportunities", []):
                opp = self._parse_opportunity(opp_data)
                if opp:
                    opportunities.append(opp)
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"VolunteerMatch API error: {e}")
            return self._get_sample_opportunities()
        except json.JSONDecodeError as e:
            logger.error(f"VolunteerMatch JSON parse error: {e}")
            return self._get_sample_opportunities()
        
        return opportunities
    
    def _parse_opportunity(self, data: Dict) -> Optional[CrawledOpportunity]:
        """Parse VolunteerMatch API response into opportunity."""
        try:
            opp = CrawledOpportunity(
                source="volunteermatch",
                source_id=str(data.get("id", "")),
                source_url=data.get("vmUrl", "https://www.volunteermatch.org"),
                title=data.get("title", ""),
                organization=data.get("parentOrg", {}).get("name", ""),
                description=data.get("plaintextDescription", data.get("description", "")),
                is_virtual=data.get("virtual", False),
            )
            
            # Location
            location = data.get("location", {})
            opp.location_city = location.get("city", "")
            opp.location_state = location.get("region", "")
            opp.location_country = location.get("country", "United States")
            
            # Categories
            category_ids = data.get("categoryIds", [])
            opp.cause_areas = [
                self.CAUSE_MAPPING.get(cid, "community") 
                for cid in category_ids 
                if cid in self.CAUSE_MAPPING
            ]
            
            # Skills
            opp.skills_needed = data.get("skillsNeeded", [])
            
            # Generate ID
            opp.id = opp.generate_id()
            
            return opp
            
        except Exception as e:
            logger.error(f"Error parsing opportunity: {e}")
            return None
    
    def _get_sample_opportunities(self) -> List[CrawledOpportunity]:
        """Return sample opportunities when API is unavailable."""
        logger.info("Returning sample VolunteerMatch-style opportunities")
        return []  # Will use existing curated list


class IdealistCrawler:
    """
    Crawler for Idealist.org RSS feeds.
    
    Idealist provides RSS feeds for volunteer opportunities:
    https://www.idealist.org/rss
    """
    
    RSS_FEEDS = [
        "https://www.idealist.org/en/rss/volunteer-opportunities",
    ]
    
    def __init__(self):
        pass
    
    def crawl_feeds(self) -> List[CrawledOpportunity]:
        """Crawl Idealist RSS feeds for opportunities."""
        opportunities = []
        
        for feed_url in self.RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:20]:  # Limit to 20 per feed
                    opp = self._parse_entry(entry)
                    if opp:
                        opportunities.append(opp)
                        
            except Exception as e:
                logger.error(f"Error parsing Idealist feed {feed_url}: {e}")
        
        return opportunities
    
    def _parse_entry(self, entry: Dict) -> Optional[CrawledOpportunity]:
        """Parse RSS entry into opportunity."""
        try:
            opp = CrawledOpportunity(
                source="idealist",
                source_id=entry.get("id", entry.get("link", "")),
                source_url=entry.get("link", "https://www.idealist.org"),
                title=entry.get("title", ""),
                organization=entry.get("author", "Unknown Organization"),
                description=entry.get("summary", ""),
            )
            
            opp.id = opp.generate_id()
            return opp
            
        except Exception as e:
            logger.error(f"Error parsing Idealist entry: {e}")
            return None


class OpportunityCrawler:
    """
    Main opportunity crawler that aggregates from multiple sources.
    
    Implements the OpportunityCrawlerAGI board functionality.
    """
    
    def __init__(self):
        self.volunteermatch = VolunteerMatchCrawler()
        self.idealist = IdealistCrawler()
        self.opportunities: List[CrawledOpportunity] = []
    
    def crawl_all(self) -> List[CrawledOpportunity]:
        """Crawl all configured sources."""
        logger.info("Starting opportunity crawl from all sources...")
        
        all_opportunities = []
        
        # VolunteerMatch
        logger.info("Crawling VolunteerMatch...")
        vm_opps = self.volunteermatch.search_opportunities()
        all_opportunities.extend(vm_opps)
        logger.info(f"Found {len(vm_opps)} opportunities from VolunteerMatch")
        
        # Idealist
        logger.info("Crawling Idealist...")
        idealist_opps = self.idealist.crawl_feeds()
        all_opportunities.extend(idealist_opps)
        logger.info(f"Found {len(idealist_opps)} opportunities from Idealist")
        
        self.opportunities = all_opportunities
        logger.info(f"Total opportunities crawled: {len(all_opportunities)}")
        
        return all_opportunities
    
    def crawl_source(self, source: str) -> List[CrawledOpportunity]:
        """Crawl a specific source."""
        logger.info(f"Crawling source: {source}")
        
        if source == "volunteermatch":
            return self.volunteermatch.search_opportunities()
        elif source == "idealist":
            return self.idealist.crawl_feeds()
        else:
            logger.warning(f"Unknown source: {source}")
            return []
    
    def export_json(self, filepath: str):
        """Export opportunities to JSON file."""
        # Load existing opportunities
        try:
            with open(filepath, 'r') as f:
                existing_data = json.load(f)
                existing_opps = {
                    opp['id']: opp 
                    for opp in existing_data.get('opportunities', [])
                }
        except (FileNotFoundError, json.JSONDecodeError):
            existing_opps = {}
        
        # Merge crawled opportunities with existing
        for opp in self.opportunities:
            opp_dict = opp.to_dict()
            existing_opps[opp.id] = opp_dict
        
        # Build output
        output = {
            "lastUpdated": datetime.now().isoformat() + "Z",
            "sources": [
                "VolunteerMatch",
                "Idealist",
                "Habitat for Humanity",
                "American Red Cross",
                "AmeriCorps",
                "United Way",
                "Big Brothers Big Sisters",
                "Meals on Wheels",
                "Special Olympics",
                "Boys & Girls Clubs"
            ],
            "count": len(existing_opps),
            "opportunities": list(existing_opps.values())
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Exported {len(existing_opps)} opportunities to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Crawl volunteer opportunities")
    parser.add_argument(
        "--source", 
        default="all",
        choices=["all", "volunteermatch", "idealist"],
        help="Source to crawl"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't save results, just log what would be crawled"
    )
    parser.add_argument(
        "--output",
        default="data/opportunities.json",
        help="Output JSON file path"
    )
    
    args = parser.parse_args()
    
    crawler = OpportunityCrawler()
    
    if args.source == "all":
        opportunities = crawler.crawl_all()
    else:
        opportunities = crawler.crawl_source(args.source)
    
    crawler.opportunities = opportunities
    
    if args.dry_run:
        logger.info("DRY RUN - would have saved the following opportunities:")
        for opp in opportunities[:5]:
            logger.info(f"  - {opp.title} ({opp.organization})")
        if len(opportunities) > 5:
            logger.info(f"  ... and {len(opportunities) - 5} more")
    else:
        # Get script directory to build correct path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_dir = os.path.dirname(script_dir)
        output_path = os.path.join(workspace_dir, args.output)
        
        crawler.export_json(output_path)
        logger.info(f"Crawl complete. Saved to {output_path}")


if __name__ == "__main__":
    main()

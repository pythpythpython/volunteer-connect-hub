#!/usr/bin/env python3
"""
VolunteerConnect Hub - VolunteerMatch API Integration
=======================================================

Full integration with the VolunteerMatch API for searching and
retrieving volunteer opportunities.

VolunteerMatch API Documentation:
https://www.volunteermatch.org/business/api/

API Features:
- Search by location, keywords, categories
- Filter by skills, virtual/in-person
- Detailed opportunity information
- Organization details

To get API access:
1. Register at https://www.volunteermatch.org/business/
2. Apply for API access
3. Get your API key and set VOLUNTEERMATCH_API_KEY environment variable

This module is used by the opportunity crawler workflow.
"""

import os
import json
import logging
import base64
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    requests = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# VolunteerMatch category mappings
CATEGORY_MAPPING = {
    1: "advocacy_human_rights",
    2: "animals",
    3: "arts_culture",
    4: "board_development",
    5: "children_youth",
    6: "community",
    7: "computers_technology",
    8: "crisis_support",
    9: "disaster_relief",
    10: "education_literacy",
    11: "emergency_safety",
    12: "employment",
    13: "environment",
    14: "faith_based",
    15: "health_medicine",
    16: "homeless_housing",
    17: "hunger",
    18: "immigrants_refugees",
    19: "international",
    20: "justice_legal",
    21: "lgbtq",
    22: "media_broadcasting",
    23: "people_with_disabilities",
    24: "politics",
    25: "race_ethnicity",
    26: "seniors",
    27: "sports_recreation",
    28: "veterans_military_families",
    29: "women",
}

# Reverse mapping for our cause areas
CAUSE_TO_CATEGORY = {
    "education": [5, 10],
    "environment": [13],
    "health": [15],
    "hunger": [17],
    "housing": [16],
    "animals": [2],
    "seniors": [26],
    "youth": [5],
    "veterans": [28],
    "disaster": [9, 11],
    "community": [6],
    "immigrants": [18],
    "mental_health": [8, 15],
    "arts": [3],
    "justice": [20],
    "disability": [23],
    "faith": [14],
    "international": [19],
}


@dataclass
class VolunteerMatchOpportunity:
    """Opportunity from VolunteerMatch API."""
    id: str = ""
    title: str = ""
    description: str = ""
    plaintext_description: str = ""
    organization_name: str = ""
    organization_url: str = ""
    vm_url: str = ""
    location: Dict[str, Any] = field(default_factory=dict)
    is_virtual: bool = False
    category_ids: List[int] = field(default_factory=list)
    skills_needed: List[str] = field(default_factory=list)
    great_for: List[str] = field(default_factory=list)
    availability: Dict[str, Any] = field(default_factory=dict)
    requires_background_check: bool = False
    requires_drivers_license: bool = False
    min_age: int = 0
    
    def to_standard_format(self) -> Dict[str, Any]:
        """Convert to our standard opportunity format."""
        return {
            "id": f"vm-{self.id}",
            "source": "volunteermatch",
            "source_id": self.id,
            "source_url": self.vm_url,
            "title": self.title,
            "organization": self.organization_name,
            "organization_url": self.organization_url,
            "description": self.plaintext_description or self.description,
            "location_city": self.location.get("city", ""),
            "location_state": self.location.get("region", ""),
            "location_country": self.location.get("country", "United States"),
            "is_virtual": self.is_virtual,
            "cause_areas": self._map_categories_to_causes(),
            "skills_needed": self.skills_needed,
            "populations_served": self._determine_populations(),
            "commitment_type": self._determine_commitment_type(),
            "hours_per_week_min": 0,
            "hours_per_week_max": 0,
            "background_check_required": self.requires_background_check,
            "training_provided": True,  # Most VM opportunities provide training
            "min_age": self.min_age,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    
    def _map_categories_to_causes(self) -> List[str]:
        """Map VolunteerMatch categories to our cause areas."""
        causes = set()
        for cat_id in self.category_ids:
            cat_name = CATEGORY_MAPPING.get(cat_id, "")
            # Map to our cause areas
            for cause, cat_ids in CAUSE_TO_CATEGORY.items():
                if cat_id in cat_ids:
                    causes.add(cause)
        return list(causes) or ["community"]
    
    def _determine_populations(self) -> List[str]:
        """Determine populations served based on categories."""
        populations = []
        if 5 in self.category_ids:
            populations.extend(["children", "teens"])
        if 26 in self.category_ids:
            populations.append("seniors")
        if 2 in self.category_ids:
            populations.append("animals")
        if 28 in self.category_ids:
            populations.append("veterans")
        return populations or ["general"]
    
    def _determine_commitment_type(self) -> str:
        """Determine commitment type from availability."""
        # Default to ongoing, but this could be enhanced
        return "ongoing"


class VolunteerMatchAPI:
    """
    Client for VolunteerMatch API.
    
    The API uses WSSE authentication with username and API key.
    
    Example usage:
        api = VolunteerMatchAPI("your_username", "your_api_key")
        opportunities = api.search_opportunities(
            location="San Francisco, CA",
            categories=[10],  # Education
            num_results=20
        )
    """
    
    BASE_URL = "https://www.volunteermatch.org/api/call"
    
    def __init__(self, username: str = None, api_key: str = None):
        """
        Initialize the API client.
        
        Args:
            username: VolunteerMatch account username
            api_key: VolunteerMatch API key
        """
        self.username = username or os.environ.get('VOLUNTEERMATCH_USERNAME')
        self.api_key = api_key or os.environ.get('VOLUNTEERMATCH_API_KEY')
        
        if not requests:
            raise ImportError("requests library is required. Install with: pip install requests")
    
    def is_configured(self) -> bool:
        """Check if API credentials are configured."""
        return bool(self.api_key)
    
    def _generate_wsse_header(self) -> str:
        """
        Generate WSSE authentication header.
        
        VolunteerMatch uses WSSE (WS-Security) authentication.
        """
        created = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        nonce = os.urandom(16)
        nonce_b64 = base64.b64encode(nonce).decode('utf-8')
        
        # Password digest = Base64(SHA256(nonce + created + api_key))
        digest_input = nonce + created.encode('utf-8') + self.api_key.encode('utf-8')
        digest = hashlib.sha256(digest_input).digest()
        digest_b64 = base64.b64encode(digest).decode('utf-8')
        
        return f'UsernameToken Username="{self.username}", PasswordDigest="{digest_b64}", Nonce="{nonce_b64}", Created="{created}"'
    
    def _make_request(self, action: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with authentication."""
        if not self.is_configured():
            logger.warning("VolunteerMatch API not configured")
            return {"error": "API not configured"}
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Add WSSE auth if username is available
        if self.username:
            headers["X-WSSE"] = self._generate_wsse_header()
        
        params = {
            "action": action,
            "query": json.dumps(query)
        }
        
        # Add API key as query param if no username
        if not self.username:
            params["key"] = self.api_key
        
        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error("VolunteerMatch API request timed out")
            return {"error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            logger.error(f"VolunteerMatch API request failed: {e}")
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse VolunteerMatch API response: {e}")
            return {"error": "Invalid JSON response"}
    
    def search_opportunities(
        self,
        location: str = "United States",
        keywords: str = None,
        categories: List[int] = None,
        skills: List[str] = None,
        virtual: bool = None,
        num_results: int = 20,
        page_number: int = 1,
        sort_criteria: str = "relevance"
    ) -> List[VolunteerMatchOpportunity]:
        """
        Search for volunteer opportunities.
        
        Args:
            location: Location string (city, state or zip code)
            keywords: Search keywords
            categories: List of category IDs (see CATEGORY_MAPPING)
            skills: List of skills to filter by
            virtual: Filter for virtual opportunities only
            num_results: Number of results per page (max 100)
            page_number: Page number for pagination
            sort_criteria: How to sort results (relevance, distance, update)
            
        Returns:
            List of VolunteerMatchOpportunity objects
        """
        query = {
            "location": location,
            "numberOfResults": min(num_results, 100),
            "pageNumber": page_number,
            "sortCriteria": sort_criteria,
            "fieldsToDisplay": [
                "id",
                "title",
                "description",
                "plaintextDescription",
                "greatFor",
                "categoryIds",
                "skillsNeeded",
                "virtual",
                "vmUrl",
                "location",
                "parentOrg",
                "availability",
                "requiresBackgroundCheck",
                "requiresDriversLicense",
                "minimumAge"
            ]
        }
        
        if keywords:
            query["keywords"] = keywords
        if categories:
            query["categoryIds"] = categories
        if skills:
            query["skills"] = skills
        if virtual is not None:
            query["virtual"] = virtual
        
        result = self._make_request("searchOpportunities", query)
        
        if "error" in result:
            logger.error(f"Search failed: {result['error']}")
            return []
        
        opportunities = []
        for opp_data in result.get("opportunities", []):
            opp = self._parse_opportunity(opp_data)
            if opp:
                opportunities.append(opp)
        
        return opportunities
    
    def _parse_opportunity(self, data: Dict[str, Any]) -> Optional[VolunteerMatchOpportunity]:
        """Parse API response into VolunteerMatchOpportunity."""
        try:
            return VolunteerMatchOpportunity(
                id=str(data.get("id", "")),
                title=data.get("title", ""),
                description=data.get("description", ""),
                plaintext_description=data.get("plaintextDescription", ""),
                organization_name=data.get("parentOrg", {}).get("name", ""),
                organization_url=data.get("parentOrg", {}).get("url", ""),
                vm_url=data.get("vmUrl", ""),
                location=data.get("location", {}),
                is_virtual=data.get("virtual", False),
                category_ids=data.get("categoryIds", []),
                skills_needed=data.get("skillsNeeded", []),
                great_for=data.get("greatFor", []),
                availability=data.get("availability", {}),
                requires_background_check=data.get("requiresBackgroundCheck", False),
                requires_drivers_license=data.get("requiresDriversLicense", False),
                min_age=data.get("minimumAge", 0),
            )
        except Exception as e:
            logger.error(f"Failed to parse opportunity: {e}")
            return None
    
    def search_by_cause(
        self,
        cause: str,
        location: str = "United States",
        virtual: bool = None,
        num_results: int = 10
    ) -> List[VolunteerMatchOpportunity]:
        """
        Search opportunities by our cause area.
        
        Args:
            cause: Our cause area (education, environment, etc.)
            location: Location string
            virtual: Filter for virtual only
            num_results: Number of results
            
        Returns:
            List of opportunities
        """
        categories = CAUSE_TO_CATEGORY.get(cause, [6])  # Default to community
        return self.search_opportunities(
            location=location,
            categories=categories,
            virtual=virtual,
            num_results=num_results
        )
    
    def get_opportunity_details(self, opportunity_id: str) -> Optional[VolunteerMatchOpportunity]:
        """Get detailed information about a specific opportunity."""
        query = {
            "ids": [int(opportunity_id)],
            "fieldsToDisplay": [
                "id", "title", "description", "plaintextDescription",
                "greatFor", "categoryIds", "skillsNeeded", "virtual",
                "vmUrl", "location", "parentOrg", "availability",
                "requiresBackgroundCheck", "requiresDriversLicense",
                "minimumAge", "contactEmail", "contactPhone"
            ]
        }
        
        result = self._make_request("getOpportunitiesById", query)
        
        if "error" in result:
            return None
        
        opportunities = result.get("opportunities", [])
        if opportunities:
            return self._parse_opportunity(opportunities[0])
        return None


def fetch_opportunities_from_volunteermatch(
    cause_areas: List[str] = None,
    location: str = "United States",
    include_virtual: bool = True,
    max_per_cause: int = 5
) -> List[Dict[str, Any]]:
    """
    Convenience function to fetch opportunities from VolunteerMatch.
    
    Args:
        cause_areas: List of cause areas to search (uses all if None)
        location: Location string
        include_virtual: Whether to include virtual opportunities
        max_per_cause: Maximum opportunities per cause area
        
    Returns:
        List of opportunities in our standard format
    """
    api = VolunteerMatchAPI()
    
    if not api.is_configured():
        logger.warning("VolunteerMatch API not configured. Returning empty list.")
        return []
    
    # Default cause areas
    if not cause_areas:
        cause_areas = ["education", "environment", "health", "hunger", 
                       "animals", "seniors", "youth", "community"]
    
    all_opportunities = []
    
    for cause in cause_areas:
        logger.info(f"Fetching {cause} opportunities from VolunteerMatch...")
        
        # Fetch in-person opportunities
        opps = api.search_by_cause(
            cause=cause,
            location=location,
            virtual=False,
            num_results=max_per_cause
        )
        all_opportunities.extend([o.to_standard_format() for o in opps])
        
        # Fetch virtual opportunities if requested
        if include_virtual:
            virtual_opps = api.search_by_cause(
                cause=cause,
                location=location,
                virtual=True,
                num_results=max_per_cause // 2
            )
            all_opportunities.extend([o.to_standard_format() for o in virtual_opps])
    
    # Remove duplicates by ID
    seen_ids = set()
    unique_opps = []
    for opp in all_opportunities:
        if opp['id'] not in seen_ids:
            seen_ids.add(opp['id'])
            unique_opps.append(opp)
    
    logger.info(f"Fetched {len(unique_opps)} unique opportunities from VolunteerMatch")
    return unique_opps


if __name__ == "__main__":
    # Test the API
    api = VolunteerMatchAPI()
    
    print("VolunteerMatch API Integration")
    print("=" * 50)
    
    if api.is_configured():
        print("API is configured. Testing search...")
        opps = api.search_opportunities(
            location="San Francisco, CA",
            categories=[10],  # Education
            num_results=5
        )
        print(f"Found {len(opps)} opportunities")
        for opp in opps[:3]:
            print(f"  - {opp.title} ({opp.organization_name})")
    else:
        print("API not configured. Set VOLUNTEERMATCH_API_KEY environment variable.")
        print("\nTo get API access:")
        print("1. Register at https://www.volunteermatch.org/business/")
        print("2. Apply for API access")
        print("3. Set your API key as an environment variable")

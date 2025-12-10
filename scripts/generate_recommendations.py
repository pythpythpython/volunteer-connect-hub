#!/usr/bin/env python3
"""
VolunteerConnect Hub - Recommendation Generator
=================================================

Generates personalized opportunity recommendations for users
based on their profiles using the RecommendationAGI board.

Runs as part of the opportunity crawler workflow to update
recommendations after new opportunities are added.

Requires:
    SUPABASE_URL - Supabase project URL
    SUPABASE_SERVICE_KEY - Service role key for database access
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Import recommendation board
try:
    from agi_boards.recommendation_board import RecommendationAGI, generate_recommendations_for_profile
    AGI_AVAILABLE = True
except ImportError:
    logger.warning("RecommendationAGI not available - using simplified matching")
    AGI_AVAILABLE = False


def get_supabase_client():
    """Initialize Supabase client."""
    try:
        from supabase import create_client, Client
    except ImportError:
        logger.error("Supabase package not installed. Run: pip install supabase")
        return None
    
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not url or not key:
        logger.warning("Supabase credentials not configured.")
        return None
    
    try:
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        return None


def get_active_profiles(supabase) -> List[Dict]:
    """Get profiles that have completed the questionnaire."""
    try:
        result = supabase.table('profiles').select('*').eq('profile_complete', True).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching profiles: {e}")
        return []


def get_active_opportunities(supabase) -> List[Dict]:
    """Get all active opportunities."""
    try:
        result = supabase.table('opportunities').select('*').eq('is_active', True).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"Error fetching opportunities: {e}")
        return []


def calculate_match_score(profile: Dict, opportunity: Dict) -> Dict:
    """
    Calculate match score between profile and opportunity.
    Uses RecommendationAGI if available, otherwise simplified matching.
    """
    if AGI_AVAILABLE:
        agi = RecommendationAGI()
        score = agi._calculate_match_score(profile, opportunity)
        return {
            'score': score.total_score,
            'match_reasons': score.match_reasons
        }
    
    # Simplified matching
    score = 0
    reasons = []
    
    # Cause matching
    profile_causes = set(c.lower() for c in profile.get('causes_interested', []))
    opp_causes = set(c.lower() for c in opportunity.get('cause_areas', []))
    
    cause_matches = profile_causes & opp_causes
    if cause_matches:
        score += len(cause_matches) * 20
        reasons.append(f"Matches your interests: {', '.join(cause_matches)}")
    
    # Skill matching
    profile_skills = set()
    for s in profile.get('skills', []):
        if isinstance(s, dict):
            profile_skills.add(s.get('name', '').lower())
        else:
            profile_skills.add(str(s).lower())
    
    opp_skills = set(s.lower() for s in opportunity.get('skills_needed', []))
    
    skill_matches = profile_skills & opp_skills
    if skill_matches:
        score += len(skill_matches) * 15
        reasons.append(f"Uses your skills: {', '.join(skill_matches)}")
    
    # Virtual preference
    if profile.get('prefers_virtual') and opportunity.get('is_virtual'):
        score += 10
        reasons.append("Remote opportunity")
    
    # Availability
    profile_hours = profile.get('availability_hours_per_week', 0)
    opp_max_hours = opportunity.get('hours_per_week_max', 0)
    
    if opp_max_hours > 0 and profile_hours >= opp_max_hours:
        score += 10
        reasons.append(f"Fits your {profile_hours}hrs/week availability")
    
    return {
        'score': min(100, score),
        'match_reasons': reasons
    }


def generate_user_recommendations(
    supabase, 
    profile: Dict, 
    opportunities: List[Dict],
    max_recommendations: int = 10
) -> List[Dict]:
    """Generate recommendations for a single user."""
    recommendations = []
    
    for opp in opportunities:
        result = calculate_match_score(profile, opp)
        
        if result['score'] >= 20:  # Minimum score threshold
            recommendations.append({
                'user_id': profile['id'],
                'opportunity_id': opp['id'],
                'score': result['score'],
                'match_reasons': result['match_reasons'],
                'created_at': datetime.now().isoformat()
            })
    
    # Sort by score and take top N
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:max_recommendations]


def save_recommendations(supabase, recommendations: List[Dict]):
    """Save recommendations to database."""
    if not recommendations:
        return
    
    try:
        # Upsert recommendations
        for rec in recommendations:
            supabase.table('recommendations').upsert(
                rec,
                on_conflict='user_id,opportunity_id'
            ).execute()
        
        logger.info(f"Saved {len(recommendations)} recommendations")
    except Exception as e:
        logger.error(f"Error saving recommendations: {e}")


def main():
    logger.info("Starting recommendation generation...")
    
    # Initialize Supabase
    supabase = get_supabase_client()
    
    if not supabase:
        logger.error("Could not connect to Supabase")
        return
    
    # Get data
    profiles = get_active_profiles(supabase)
    logger.info(f"Found {len(profiles)} complete profiles")
    
    opportunities = get_active_opportunities(supabase)
    logger.info(f"Found {len(opportunities)} active opportunities")
    
    if not profiles or not opportunities:
        logger.warning("No profiles or opportunities to process")
        return
    
    # Generate recommendations for each user
    total_recommendations = 0
    
    for profile in profiles:
        recommendations = generate_user_recommendations(
            supabase, 
            profile, 
            opportunities
        )
        
        if recommendations:
            save_recommendations(supabase, recommendations)
            total_recommendations += len(recommendations)
            logger.info(f"Generated {len(recommendations)} recommendations for user {profile['id'][:8]}...")
    
    logger.info(f"Recommendation generation complete. Total: {total_recommendations}")


if __name__ == "__main__":
    main()

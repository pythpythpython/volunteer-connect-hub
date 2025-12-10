#!/usr/bin/env python3
"""
VolunteerConnect Hub - Database Opportunity Updater
====================================================

Syncs opportunities from JSON to Supabase database.
Handles deduplication, updates, and deactivation of stale entries.

Requires:
    SUPABASE_URL - Supabase project URL
    SUPABASE_SERVICE_KEY - Service role key for database access
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
        logger.warning("Supabase credentials not configured. Skipping database update.")
        return None
    
    try:
        return create_client(url, key)
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        return None


def load_opportunities_json(filepath: str) -> List[Dict]:
    """Load opportunities from JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data.get('opportunities', [])
    except FileNotFoundError:
        logger.error(f"Opportunities file not found: {filepath}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing opportunities JSON: {e}")
        return []


def sync_opportunities_to_db(supabase, opportunities: List[Dict]):
    """Sync opportunities to Supabase database."""
    if not supabase:
        logger.warning("No Supabase client - skipping database sync")
        return
    
    logger.info(f"Syncing {len(opportunities)} opportunities to database...")
    
    inserted = 0
    updated = 0
    errors = 0
    
    for opp in opportunities:
        try:
            # Prepare data for database
            db_record = {
                'source': opp.get('source', 'manual'),
                'source_id': opp.get('source_id', opp.get('id')),
                'source_url': opp.get('source_url', ''),
                'title': opp.get('title', ''),
                'organization': opp.get('organization', ''),
                'organization_url': opp.get('organization_url', ''),
                'description': opp.get('description', ''),
                'requirements': opp.get('requirements', ''),
                'location_city': opp.get('location_city', ''),
                'location_state': opp.get('location_state', ''),
                'location_country': opp.get('location_country', 'United States'),
                'is_virtual': opp.get('is_virtual', False),
                'cause_areas': opp.get('cause_areas', []),
                'skills_needed': opp.get('skills_needed', []),
                'populations_served': opp.get('populations_served', []),
                'commitment_type': opp.get('commitment_type', 'ongoing'),
                'hours_per_week_min': opp.get('hours_per_week_min', 0),
                'hours_per_week_max': opp.get('hours_per_week_max', 0),
                'background_check_required': opp.get('background_check_required', False),
                'training_provided': opp.get('training_provided', False),
                'min_age': opp.get('min_age', 0),
                'is_active': opp.get('is_active', True),
                'updated_at': datetime.now().isoformat(),
            }
            
            # Try to upsert
            result = supabase.table('opportunities').upsert(
                db_record,
                on_conflict='source,source_id'
            ).execute()
            
            if result.data:
                # Check if it was an insert or update
                if len(result.data) > 0:
                    inserted += 1
            else:
                updated += 1
                
        except Exception as e:
            logger.error(f"Error syncing opportunity '{opp.get('title', 'unknown')}': {e}")
            errors += 1
    
    logger.info(f"Sync complete: {inserted} inserted/updated, {errors} errors")


def deactivate_stale_opportunities(supabase, days_threshold: int = 30):
    """Mark opportunities as inactive if not updated recently."""
    if not supabase:
        return
    
    threshold_date = (datetime.now() - timedelta(days=days_threshold)).isoformat()
    
    try:
        result = supabase.table('opportunities').update({
            'is_active': False
        }).lt('updated_at', threshold_date).eq('is_active', True).execute()
        
        if result.data:
            logger.info(f"Deactivated {len(result.data)} stale opportunities")
    except Exception as e:
        logger.error(f"Error deactivating stale opportunities: {e}")


def main():
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(script_dir)
    json_path = os.path.join(workspace_dir, 'data', 'opportunities.json')
    
    # Load opportunities
    opportunities = load_opportunities_json(json_path)
    
    if not opportunities:
        logger.warning("No opportunities to sync")
        return
    
    logger.info(f"Loaded {len(opportunities)} opportunities from {json_path}")
    
    # Initialize Supabase
    supabase = get_supabase_client()
    
    if supabase:
        # Sync to database
        sync_opportunities_to_db(supabase, opportunities)
        
        # Deactivate stale entries
        deactivate_stale_opportunities(supabase)
    else:
        logger.info("Database sync skipped - Supabase not configured")
    
    logger.info("Database update complete")


if __name__ == "__main__":
    main()

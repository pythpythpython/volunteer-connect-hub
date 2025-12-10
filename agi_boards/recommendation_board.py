"""
VolunteerConnect Hub - Recommendation AGI Board
================================================

Intelligent recommendation engine that:
1. Matches user profiles to volunteer opportunities
2. Generates personalized suggestions
3. Learns from user feedback
4. Optimizes for user goals and preferences

Quality Target: 100% - Highly relevant, personalized recommendations
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import math


class MatchFactor(Enum):
    """Factors used in recommendation scoring."""
    CAUSE_ALIGNMENT = "cause_alignment"
    SKILL_MATCH = "skill_match"
    AVAILABILITY_FIT = "availability_fit"
    LOCATION_PROXIMITY = "location_proximity"
    VIRTUAL_PREFERENCE = "virtual_preference"
    POPULATION_INTEREST = "population_interest"
    ACTIVITY_TYPE = "activity_type"
    COMMITMENT_FIT = "commitment_fit"
    GOAL_ALIGNMENT = "goal_alignment"
    EXPERIENCE_LEVEL = "experience_level"


@dataclass
class MatchScore:
    """Detailed match score breakdown."""
    total_score: float
    factor_scores: Dict[str, float]
    match_reasons: List[str]
    improvement_suggestions: List[str]


@dataclass
class Recommendation:
    """A single opportunity recommendation."""
    opportunity_id: str
    opportunity: Dict[str, Any]
    score: MatchScore
    rank: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class RecommendationAGI:
    """
    Recommendation AGI Board - Intelligent opportunity matching.
    
    Uses multi-factor scoring algorithm:
    - Weighted cause alignment (30%)
    - Skill matching (25%)
    - Availability fit (15%)
    - Location/virtual preference (10%)
    - Population interest (10%)
    - Goal alignment (10%)
    
    Quality Target: 100% - Relevant, actionable recommendations
    """
    
    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        MatchFactor.CAUSE_ALIGNMENT: 0.30,
        MatchFactor.SKILL_MATCH: 0.25,
        MatchFactor.AVAILABILITY_FIT: 0.15,
        MatchFactor.LOCATION_PROXIMITY: 0.05,
        MatchFactor.VIRTUAL_PREFERENCE: 0.05,
        MatchFactor.POPULATION_INTEREST: 0.10,
        MatchFactor.GOAL_ALIGNMENT: 0.10,
    }
    
    # Cause area relationships (for semantic matching)
    RELATED_CAUSES = {
        "education": ["youth", "literacy", "tutoring", "mentoring"],
        "environment": ["conservation", "climate", "sustainability", "parks"],
        "health": ["mental_health", "wellness", "medical", "hospital"],
        "hunger": ["food_bank", "food_security", "nutrition", "meals"],
        "housing": ["homelessness", "shelter", "construction", "habitat"],
        "animals": ["pets", "wildlife", "shelter", "rescue"],
        "seniors": ["elderly", "aging", "retirement", "elder_care"],
        "youth": ["children", "teens", "kids", "students"],
        "veterans": ["military", "service_members", "armed_forces"],
        "disaster": ["emergency", "relief", "crisis", "red_cross"],
        "community": ["neighborhood", "civic", "local", "development"],
        "arts": ["culture", "music", "theater", "museum"],
        "immigrants": ["refugees", "asylum", "newcomers", "esl"],
        "disability": ["accessibility", "special_needs", "adaptive"],
        "mental_health": ["counseling", "crisis", "support", "wellness"],
        "poverty": ["low_income", "economic", "assistance", "welfare"],
    }
    
    # Goal to opportunity type mapping
    GOAL_OPPORTUNITY_MAP = {
        "make_difference": ["direct_service", "advocacy"],
        "learn_skills": ["training_provided", "professional"],
        "build_resume": ["professional", "leadership"],
        "network": ["group", "corporate", "board"],
        "explore_careers": ["professional", "industry_specific"],
        "meet_people": ["group", "team", "community"],
        "stay_active": ["physical", "outdoor"],
        "family_time": ["family_friendly", "group"],
        "leadership": ["board", "coordinator", "lead"],
        "give_back": ["direct_service", "community"],
    }
    
    def __init__(self):
        self.recommendations_cache: Dict[str, List[Recommendation]] = {}
    
    def generate_recommendations(
        self,
        user_profile: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        max_results: int = 10
    ) -> List[Recommendation]:
        """
        Generate personalized recommendations for a user.
        
        Args:
            user_profile: Complete user profile from questionnaire
            opportunities: List of available opportunities
            max_results: Maximum recommendations to return
            
        Returns:
            Sorted list of Recommendation objects
        """
        recommendations = []
        
        for opp in opportunities:
            score = self._calculate_match_score(user_profile, opp)
            
            # Only include opportunities with meaningful scores
            if score.total_score >= 20:
                recommendations.append(Recommendation(
                    opportunity_id=opp.get('id', ''),
                    opportunity=opp,
                    score=score,
                    rank=0  # Will be set after sorting
                ))
        
        # Sort by score descending
        recommendations.sort(key=lambda r: r.score.total_score, reverse=True)
        
        # Assign ranks
        for i, rec in enumerate(recommendations):
            rec.rank = i + 1
        
        return recommendations[:max_results]
    
    def _calculate_match_score(
        self,
        profile: Dict[str, Any],
        opportunity: Dict[str, Any]
    ) -> MatchScore:
        """Calculate detailed match score between profile and opportunity."""
        factor_scores = {}
        match_reasons = []
        improvement_suggestions = []
        
        # 1. Cause alignment (30%)
        cause_score, cause_reasons = self._score_cause_alignment(profile, opportunity)
        factor_scores[MatchFactor.CAUSE_ALIGNMENT.value] = cause_score
        match_reasons.extend(cause_reasons)
        
        # 2. Skill match (25%)
        skill_score, skill_reasons = self._score_skill_match(profile, opportunity)
        factor_scores[MatchFactor.SKILL_MATCH.value] = skill_score
        match_reasons.extend(skill_reasons)
        
        # 3. Availability fit (15%)
        avail_score, avail_reasons = self._score_availability_fit(profile, opportunity)
        factor_scores[MatchFactor.AVAILABILITY_FIT.value] = avail_score
        match_reasons.extend(avail_reasons)
        
        # 4. Location/Virtual (10% combined)
        loc_score, loc_reasons = self._score_location_match(profile, opportunity)
        factor_scores[MatchFactor.LOCATION_PROXIMITY.value] = loc_score * 0.5
        factor_scores[MatchFactor.VIRTUAL_PREFERENCE.value] = loc_score * 0.5
        match_reasons.extend(loc_reasons)
        
        # 5. Population interest (10%)
        pop_score, pop_reasons = self._score_population_match(profile, opportunity)
        factor_scores[MatchFactor.POPULATION_INTEREST.value] = pop_score
        match_reasons.extend(pop_reasons)
        
        # 6. Goal alignment (10%)
        goal_score, goal_reasons = self._score_goal_alignment(profile, opportunity)
        factor_scores[MatchFactor.GOAL_ALIGNMENT.value] = goal_score
        match_reasons.extend(goal_reasons)
        
        # Calculate weighted total
        total = sum(
            factor_scores.get(factor.value, 0) * weight
            for factor, weight in self.WEIGHTS.items()
        )
        
        # Generate improvement suggestions
        if skill_score < 50:
            improvement_suggestions.append(
                "Consider developing skills in: " + 
                ", ".join(opportunity.get('skills_needed', [])[:3])
            )
        
        if avail_score < 50:
            improvement_suggestions.append(
                "This opportunity may require adjusting your availability"
            )
        
        return MatchScore(
            total_score=round(total, 1),
            factor_scores=factor_scores,
            match_reasons=[r for r in match_reasons if r],
            improvement_suggestions=improvement_suggestions
        )
    
    def _score_cause_alignment(
        self,
        profile: Dict,
        opportunity: Dict
    ) -> Tuple[float, List[str]]:
        """Score cause area alignment."""
        user_causes = set(c.lower() for c in profile.get('causes_interested', []))
        opp_causes = set(c.lower() for c in opportunity.get('cause_areas', []))
        
        if not user_causes or not opp_causes:
            return 0, []
        
        # Direct matches
        direct_matches = user_causes & opp_causes
        
        # Related matches
        related_matches = set()
        for user_cause in user_causes:
            related = set(self.RELATED_CAUSES.get(user_cause, []))
            related_matches.update(opp_causes & related)
        
        direct_score = len(direct_matches) * 40  # Up to 100 for direct
        related_score = len(related_matches) * 20  # Up to 60 for related
        
        total = min(100, direct_score + related_score)
        
        reasons = []
        if direct_matches:
            reasons.append(f"Aligns with your passion for {', '.join(direct_matches)}")
        if related_matches and not direct_matches:
            reasons.append(f"Related to your interests")
        
        return total, reasons
    
    def _score_skill_match(
        self,
        profile: Dict,
        opportunity: Dict
    ) -> Tuple[float, List[str]]:
        """Score skill alignment."""
        user_skills = [s.get('name', s) if isinstance(s, dict) else s 
                       for s in profile.get('skills', [])]
        user_skills_lower = set(s.lower() for s in user_skills)
        
        opp_skills = opportunity.get('skills_needed', [])
        opp_skills_lower = set(s.lower() for s in opp_skills)
        
        if not opp_skills:
            return 80, ["No specific skills required"]
        
        if not user_skills:
            if opportunity.get('training_provided', False):
                return 60, ["Training provided - great for learning"]
            return 30, []
        
        matches = user_skills_lower & opp_skills_lower
        
        if not matches:
            # Check for partial matches
            partial = any(
                any(us in os or os in us for os in opp_skills_lower)
                for us in user_skills_lower
            )
            if partial:
                return 50, ["Your skills are related to requirements"]
            if opportunity.get('training_provided', False):
                return 40, ["Training provided for required skills"]
            return 20, []
        
        match_pct = (len(matches) / len(opp_skills)) * 100
        
        matched_skills = [s for s in opp_skills if s.lower() in matches]
        reasons = [f"Uses your skills in {', '.join(matched_skills[:3])}"]
        
        return min(100, match_pct + 20), reasons  # Bonus for any match
    
    def _score_availability_fit(
        self,
        profile: Dict,
        opportunity: Dict
    ) -> Tuple[float, List[str]]:
        """Score availability match."""
        user_hours = profile.get('availability_hours_per_week', 0)
        opp_min = opportunity.get('hours_per_week_min', 0)
        opp_max = opportunity.get('hours_per_week_max', 0)
        
        if opp_max == 0:  # Flexible hours
            return 90, ["Flexible time commitment"]
        
        if user_hours == 0:
            return 50, []
        
        # Check if user has enough time
        if user_hours >= opp_min:
            if opp_max <= user_hours:
                return 100, [f"Perfect fit for your {user_hours}hrs/week"]
            else:
                return 80, [f"Fits within your {user_hours}hrs/week availability"]
        else:
            # User has less time than minimum
            shortage = opp_min - user_hours
            if shortage <= 2:
                return 60, ["May require slightly more time than usual"]
            return 30, ["Requires more hours than your stated availability"]
        
        return 50, []
    
    def _score_location_match(
        self,
        profile: Dict,
        opportunity: Dict
    ) -> Tuple[float, List[str]]:
        """Score location/virtual preference match."""
        prefers_virtual = profile.get('prefers_virtual', False)
        prefers_in_person = profile.get('prefers_in_person', True)
        opp_virtual = opportunity.get('is_virtual', False)
        
        if opp_virtual:
            if prefers_virtual:
                return 100, ["Remote opportunity - matches your preference"]
            elif prefers_in_person:
                return 60, ["Virtual opportunity available"]
            return 80, []
        else:
            if prefers_in_person:
                # Could add distance calculation here
                return 90, ["In-person opportunity"]
            elif prefers_virtual:
                return 40, ["Requires in-person attendance"]
            return 70, []
    
    def _score_population_match(
        self,
        profile: Dict,
        opportunity: Dict
    ) -> Tuple[float, List[str]]:
        """Score population interest match."""
        user_pops = set(p.lower() for p in profile.get('populations_interested', []))
        opp_pops = set(p.lower() for p in opportunity.get('populations_served', []))
        
        if not user_pops or not opp_pops:
            return 70, []  # Neutral if not specified
        
        matches = user_pops & opp_pops
        
        if matches:
            return 100, [f"Serves {', '.join(matches)} - your preferred population"]
        
        return 50, []
    
    def _score_goal_alignment(
        self,
        profile: Dict,
        opportunity: Dict
    ) -> Tuple[float, List[str]]:
        """Score alignment with user's volunteering goals."""
        user_goals = profile.get('goals', [])
        user_motivation = profile.get('primary_motivation', '')
        
        if not user_goals:
            return 60, []
        
        score = 60  # Base score
        reasons = []
        
        # Check goal-opportunity alignment
        opp_provides = set()
        
        # Infer what this opportunity provides
        if opportunity.get('training_provided', False):
            opp_provides.add('learn_skills')
        
        if opportunity.get('is_virtual', False):
            opp_provides.add('flexible')
        
        commitment = opportunity.get('commitment_type', '')
        if commitment == 'recurring':
            opp_provides.add('build_resume')
            opp_provides.add('network')
        
        if any(pop in ['children', 'teens', 'youth'] 
               for pop in opportunity.get('populations_served', [])):
            opp_provides.add('make_difference')
        
        # Score matches
        for goal in user_goals:
            goal_lower = goal.lower().replace(' ', '_')
            if goal_lower in opp_provides:
                score += 15
                reasons.append(f"Helps you {goal.lower()}")
        
        return min(100, score), reasons[:2]  # Limit reasons
    
    def explain_recommendation(self, recommendation: Recommendation) -> str:
        """Generate human-readable explanation of why this was recommended."""
        score = recommendation.score
        opp = recommendation.opportunity
        
        explanation = f"**{opp.get('title', 'Opportunity')}** (Match: {score.total_score}%)\n\n"
        explanation += f"Organization: {opp.get('organization', 'Unknown')}\n\n"
        
        if score.match_reasons:
            explanation += "**Why we think you'd be great for this:**\n"
            for reason in score.match_reasons:
                explanation += f"• {reason}\n"
        
        explanation += f"\n**Commitment:** "
        hours_min = opp.get('hours_per_week_min', 0)
        hours_max = opp.get('hours_per_week_max', 0)
        if hours_max > 0:
            explanation += f"{hours_min}-{hours_max} hours/week"
        else:
            explanation += "Flexible"
        
        if opp.get('is_virtual'):
            explanation += " (Remote)"
        else:
            explanation += " (In-person)"
        
        if score.improvement_suggestions:
            explanation += "\n\n**Tips for success:**\n"
            for tip in score.improvement_suggestions:
                explanation += f"• {tip}\n"
        
        return explanation
    
    def get_top_causes_for_user(
        self,
        profile: Dict,
        opportunities: List[Dict]
    ) -> List[Tuple[str, int]]:
        """Get top cause areas based on available opportunities matching user."""
        cause_counts = {}
        
        user_causes = set(c.lower() for c in profile.get('causes_interested', []))
        
        for opp in opportunities:
            for cause in opp.get('cause_areas', []):
                if cause.lower() in user_causes:
                    cause_counts[cause] = cause_counts.get(cause, 0) + 1
        
        sorted_causes = sorted(cause_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_causes[:5]


def generate_recommendations_for_profile(
    profile: Dict[str, Any],
    opportunities: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Convenience function to generate recommendations.
    Returns serializable dict format.
    """
    agi = RecommendationAGI()
    recommendations = agi.generate_recommendations(profile, opportunities)
    
    return [
        {
            "opportunity_id": rec.opportunity_id,
            "opportunity": rec.opportunity,
            "score": rec.score.total_score,
            "match_reasons": rec.score.match_reasons,
            "rank": rec.rank,
        }
        for rec in recommendations
    ]


if __name__ == "__main__":
    print("Recommendation AGI Board")
    print("=" * 50)
    
    # Test with sample data
    sample_profile = {
        "causes_interested": ["education", "youth"],
        "skills": [{"name": "Teaching"}, {"name": "Communication"}],
        "availability_hours_per_week": 4,
        "prefers_virtual": False,
        "prefers_in_person": True,
        "populations_interested": ["children", "teens"],
        "goals": ["make_difference", "learn_skills"],
    }
    
    sample_opportunities = [
        {
            "id": "1",
            "title": "Youth Tutoring Volunteer",
            "organization": "Local Library",
            "cause_areas": ["education", "youth"],
            "skills_needed": ["Teaching", "Patience"],
            "populations_served": ["children", "teens"],
            "hours_per_week_min": 2,
            "hours_per_week_max": 4,
            "is_virtual": False,
            "training_provided": True,
        },
        {
            "id": "2",
            "title": "Food Bank Helper",
            "organization": "Food Bank",
            "cause_areas": ["hunger"],
            "skills_needed": ["Physical ability"],
            "populations_served": ["families"],
            "hours_per_week_min": 3,
            "hours_per_week_max": 4,
            "is_virtual": False,
            "training_provided": True,
        },
    ]
    
    recs = generate_recommendations_for_profile(sample_profile, sample_opportunities)
    
    for rec in recs:
        print(f"\n{rec['rank']}. {rec['opportunity']['title']} - Score: {rec['score']}%")
        print(f"   Reasons: {', '.join(rec['match_reasons'])}")

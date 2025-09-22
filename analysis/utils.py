import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

def calculate_engagement_metrics(progress_data: List[Dict], roadmap_data: List[Dict], user_data: List[Dict]) -> pd.DataFrame:
    """
    Calculate engagement metrics from progress, roadmap, and user data.
    
    Args:
        progress_data: List of progress records from MongoDB
        roadmap_data: List of roadmap records from MongoDB  
        user_data: List of user records from MongoDB
        
    Returns:
        DataFrame with engagement metrics per step
    """
    
    # Create DataFrames
    progress_df = pd.DataFrame(progress_data)
    roadmap_df = pd.DataFrame(roadmap_data)
    user_df = pd.DataFrame(user_data)
    
    # Prepare user lookup
    user_lookup = {str(user['_id']): user for user in user_data}
    roadmap_lookup = {str(roadmap['_id']): roadmap for roadmap in roadmap_data}
    
    engagement_records = []
    
    for _, progress in progress_df.iterrows():
        user_id = progress['user_id']
        roadmap_id = progress['roadmap_id']
        
        # Get user and roadmap info
        user = user_lookup.get(user_id)
        roadmap = roadmap_lookup.get(roadmap_id)
        
        if not user or not roadmap or not user.get('brain_type'):
            continue
            
        # Find the corresponding step in the roadmap
        step = None
        for s in roadmap['steps']:
            if s['step_number'] == progress['step_number']:
                step = s
                break
                
        if not step:
            continue
            
        # Calculate time spent (if completed)
        time_spent_minutes = None
        if progress['completed'] and progress.get('completed_at') and progress.get('created_at'):
            try:
                completed_at = progress['completed_at']
                created_at = progress['created_at']
                
                # Handle both datetime objects and strings
                if isinstance(completed_at, str):
                    completed_at = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    
                time_diff = completed_at - created_at
                time_spent_minutes = max(1, min(time_diff.total_seconds() / 60, step['estimated_time_minutes'] * 3))  # Cap at 3x estimated time
            except:
                time_spent_minutes = step['estimated_time_minutes'] if progress['completed'] else None
        
        engagement_records.append({
            'user_id': user_id,
            'user_brain_type': user['brain_type'],
            'roadmap_id': roadmap_id,
            'roadmap_topic': roadmap['topic'],
            'step_number': progress['step_number'],
            'step_title': step['title'],
            'resource_type': step['resource_type'],
            'estimated_time_minutes': step['estimated_time_minutes'],
            'brain_type_optimized': step.get('brain_type_optimized', False),
            'completed': progress['completed'],
            'time_spent_minutes': time_spent_minutes,
            'created_at': progress['created_at'],
            'completed_at': progress.get('completed_at'),
            'updated_at': progress['updated_at']
        })
    
    return pd.DataFrame(engagement_records)

def determine_resource_match_level(brain_type: str, resource_type: str, preferences: Dict) -> str:
    """
    Determine if a resource type matches the user's brain type preferences.
    
    Args:
        brain_type: User's brain type (Visual, Auditory, ReadWrite, Kinesthetic)
        resource_type: Type of resource (video, article, tutorial, etc.)
        preferences: Brain type preference configuration
        
    Returns:
        Match level: 'high_match', 'medium_match', 'low_match'
    """
    
    brain_prefs = preferences.get(brain_type, {})
    resource_preference = brain_prefs.get(resource_type, 0)
    
    if resource_preference >= 0.25:  # High preference threshold
        return 'high_match'
    elif resource_preference >= 0.15:  # Medium preference threshold  
        return 'medium_match'
    else:
        return 'low_match'

def calculate_completion_rate(df: pd.DataFrame, group_by: List[str]) -> pd.DataFrame:
    """
    Calculate completion rates grouped by specified columns.
    
    Args:
        df: DataFrame with engagement data
        group_by: List of columns to group by
        
    Returns:
        DataFrame with completion rates
    """
    
    grouped = df.groupby(group_by).agg({
        'completed': ['count', 'sum'],
        'time_spent_minutes': ['mean', 'median', 'std']
    }).round(3)
    
    # Flatten column names
    grouped.columns = ['_'.join(col).strip() for col in grouped.columns]
    
    # Calculate completion rate
    grouped['completion_rate'] = (grouped['completed_sum'] / grouped['completed_count']).round(3)
    
    # Calculate average time for completed steps only
    completed_df = df[df['completed'] == True]
    if not completed_df.empty:
        completed_grouped = completed_df.groupby(group_by)['time_spent_minutes'].agg(['mean', 'count']).round(2)
        grouped['avg_completion_time'] = completed_grouped['mean']
        grouped['completed_steps_count'] = completed_grouped['count']
    else:
        grouped['avg_completion_time'] = 0
        grouped['completed_steps_count'] = 0
    
    return grouped.reset_index()

def generate_summary_statistics(df: pd.DataFrame) -> Dict:
    """
    Generate summary statistics for the analysis.
    
    Args:
        df: DataFrame with engagement data including match levels
        
    Returns:
        Dictionary with summary statistics
    """
    
    total_steps = len(df)
    total_users = df['user_id'].nunique()
    total_roadmaps = df['roadmap_id'].nunique()
    
    # Overall completion rate
    overall_completion_rate = df['completed'].mean()
    
    # Completion rates by match level
    match_completion = df.groupby('match_level')['completed'].agg(['count', 'mean']).round(3)
    
    # Completion rates by brain type
    brain_type_completion = df.groupby('user_brain_type')['completed'].agg(['count', 'mean']).round(3)
    
    # Average time spent by match level (completed steps only)
    completed_df = df[df['completed'] == True]
    if not completed_df.empty:
        match_time = completed_df.groupby('match_level')['time_spent_minutes'].mean().round(2)
        brain_type_time = completed_df.groupby('user_brain_type')['time_spent_minutes'].mean().round(2)
    else:
        match_time = pd.Series()
        brain_type_time = pd.Series()
    
    return {
        'total_analysis_records': total_steps,
        'unique_users': total_users,
        'unique_roadmaps': total_roadmaps,
        'overall_completion_rate': round(overall_completion_rate, 3),
        'completion_by_match_level': match_completion.to_dict(),
        'completion_by_brain_type': brain_type_completion.to_dict(),
        'avg_time_by_match_level': match_time.to_dict(),
        'avg_time_by_brain_type': brain_type_time.to_dict(),
        'analysis_date': datetime.now().isoformat()
    }

def format_insights(summary_stats: Dict) -> List[str]:
    """
    Generate human-readable insights from summary statistics.
    
    Args:
        summary_stats: Dictionary with summary statistics
        
    Returns:
        List of insight strings
    """
    
    insights = []
    
    # Overall statistics
    insights.append(f"📊 ANALYSIS OVERVIEW:")
    insights.append(f"   • Analyzed {summary_stats['total_analysis_records']} learning steps")
    insights.append(f"   • Across {summary_stats['unique_users']} users and {summary_stats['unique_roadmaps']} roadmaps")
    insights.append(f"   • Overall completion rate: {summary_stats['overall_completion_rate']:.1%}")
    
    # Match level analysis
    match_completion = summary_stats.get('completion_by_match_level', {})
    if match_completion:
        insights.append(f"\n🎯 BRAIN TYPE MATCHING EFFECTIVENESS:")
        
        high_match_rate = match_completion.get('mean', {}).get('high_match', 0)
        medium_match_rate = match_completion.get('mean', {}).get('medium_match', 0)
        low_match_rate = match_completion.get('mean', {}).get('low_match', 0)
        
        insights.append(f"   • High Match Resources: {high_match_rate:.1%} completion rate")
        insights.append(f"   • Medium Match Resources: {medium_match_rate:.1%} completion rate") 
        insights.append(f"   • Low Match Resources: {low_match_rate:.1%} completion rate")
        
        # Calculate improvement
        if low_match_rate > 0:
            improvement = ((high_match_rate - low_match_rate) / low_match_rate) * 100
            insights.append(f"   • Improvement with matching: {improvement:+.1f}%")
    
    # Brain type performance
    brain_completion = summary_stats.get('completion_by_brain_type', {})
    if brain_completion:
        insights.append(f"\n🧠 BRAIN TYPE PERFORMANCE:")
        for brain_type, rate in brain_completion.get('mean', {}).items():
            count = brain_completion.get('count', {}).get(brain_type, 0)
            insights.append(f"   • {brain_type}: {rate:.1%} completion ({count} steps)")
    
    # Time analysis
    match_time = summary_stats.get('avg_time_by_match_level', {})
    if match_time:
        insights.append(f"\n⏱️  TIME EFFICIENCY:")
        for match_level, avg_time in match_time.items():
            insights.append(f"   • {match_level.replace('_', ' ').title()}: {avg_time:.1f} min average")
    
    return insights
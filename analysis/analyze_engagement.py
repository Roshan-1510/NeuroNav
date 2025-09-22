#!/usr/bin/env python3
"""
NeuroNav Engagement Analysis Script

This script analyzes the effectiveness of brain-type matched learning resources
by comparing completion rates and engagement metrics between matched and non-matched
resource types for different brain types.

Usage:
    python analyze_engagement.py [--output-dir results] [--verbose]
    
Output:
    - engagement_analysis.csv: Detailed engagement metrics per step
    - summary_metrics.csv: Aggregated statistics and insights
"""

import sys
import os
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
from pymongo import MongoClient
from typing import Dict, List, Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import MONGO_URI, ANALYSIS_CONFIG, RESOURCE_TYPE_MAPPINGS
from utils import (
    calculate_engagement_metrics, 
    determine_resource_match_level,
    calculate_completion_rate,
    generate_summary_statistics,
    format_insights
)

class NeuroNavAnalyzer:
    """Main analyzer class for NeuroNav engagement analysis."""
    
    def __init__(self, mongo_uri: str = MONGO_URI, verbose: bool = False):
        """
        Initialize the analyzer with MongoDB connection.
        
        Args:
            mongo_uri: MongoDB connection string
            verbose: Enable verbose logging
        """
        self.mongo_uri = mongo_uri
        self.verbose = verbose
        self.client = None
        self.db = None
        
    def connect_to_database(self):
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client.neuronav
            
            # Test connection
            self.db.command('ping')
            
            if self.verbose:
                print(f"✅ Connected to MongoDB: {self.mongo_uri}")
                
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            sys.exit(1)
    
    def fetch_data(self) -> tuple:
        """
        Fetch all necessary data from MongoDB collections.
        
        Returns:
            Tuple of (progress_data, roadmap_data, user_data)
        """
        if self.verbose:
            print("📊 Fetching data from MongoDB...")
        
        try:
            # Fetch progress data
            progress_data = list(self.db.progress.find({}))
            
            # Fetch roadmap data
            roadmap_data = list(self.db.roadmaps.find({}))
            
            # Fetch user data (only users with brain types)
            user_data = list(self.db.users.find({'brain_type': {'$exists': True, '$ne': None}}))
            
            if self.verbose:
                print(f"   • Progress records: {len(progress_data)}")
                print(f"   • Roadmaps: {len(roadmap_data)}")
                print(f"   • Users with brain types: {len(user_data)}")
            
            return progress_data, roadmap_data, user_data
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            sys.exit(1)
    
    def preprocess_data(self, progress_data: List[Dict], roadmap_data: List[Dict], user_data: List[Dict]) -> pd.DataFrame:
        """
        Preprocess and combine data into analysis-ready format.
        
        Args:
            progress_data: Raw progress data from MongoDB
            roadmap_data: Raw roadmap data from MongoDB
            user_data: Raw user data from MongoDB
            
        Returns:
            DataFrame ready for analysis
        """
        if self.verbose:
            print("🔄 Preprocessing data...")
        
        # Calculate engagement metrics
        df = calculate_engagement_metrics(progress_data, roadmap_data, user_data)
        
        if df.empty:
            print("⚠️  No valid engagement data found. Analysis cannot proceed.")
            return df
        
        # Normalize resource types using mappings
        df['normalized_resource_type'] = df['resource_type'].map(RESOURCE_TYPE_MAPPINGS).fillna(df['resource_type'])
        
        # Determine match level for each step
        preferences = ANALYSIS_CONFIG['brain_type_preferences']
        df['match_level'] = df.apply(
            lambda row: determine_resource_match_level(
                row['user_brain_type'], 
                row['normalized_resource_type'], 
                preferences
            ), 
            axis=1
        )
        
        # Add additional derived metrics
        df['completion_efficiency'] = np.where(
            df['completed'] & (df['time_spent_minutes'].notna()),
            df['estimated_time_minutes'] / df['time_spent_minutes'],
            np.nan
        )
        
        if self.verbose:
            print(f"   • Processed {len(df)} engagement records")
            print(f"   • Brain types: {df['user_brain_type'].value_counts().to_dict()}")
            print(f"   • Resource types: {df['normalized_resource_type'].value_counts().to_dict()}")
            print(f"   • Match levels: {df['match_level'].value_counts().to_dict()}")
        
        return df
    
    def analyze_engagement(self, df: pd.DataFrame) -> Dict:
        """
        Perform comprehensive engagement analysis.
        
        Args:
            df: Preprocessed engagement data
            
        Returns:
            Dictionary containing analysis results
        """
        if self.verbose:
            print("📈 Performing engagement analysis...")
        
        results = {}
        
        # 1. Overall completion rates by match level
        match_level_analysis = calculate_completion_rate(df, ['match_level'])
        results['completion_by_match_level'] = match_level_analysis
        
        # 2. Brain type specific analysis
        brain_type_analysis = calculate_completion_rate(df, ['user_brain_type'])
        results['completion_by_brain_type'] = brain_type_analysis
        
        # 3. Resource type analysis
        resource_type_analysis = calculate_completion_rate(df, ['normalized_resource_type'])
        results['completion_by_resource_type'] = resource_type_analysis
        
        # 4. Combined analysis: brain type + match level
        combined_analysis = calculate_completion_rate(df, ['user_brain_type', 'match_level'])
        results['completion_by_brain_type_and_match'] = combined_analysis
        
        # 5. Topic-specific analysis
        topic_analysis = calculate_completion_rate(df, ['roadmap_topic'])
        results['completion_by_topic'] = topic_analysis
        
        # 6. Efficiency analysis (time spent vs estimated time)
        efficiency_df = df[df['completed'] & df['time_spent_minutes'].notna()].copy()
        if not efficiency_df.empty:
            efficiency_analysis = efficiency_df.groupby(['match_level']).agg({
                'completion_efficiency': ['mean', 'median', 'std', 'count']
            }).round(3)
            efficiency_analysis.columns = ['_'.join(col) for col in efficiency_analysis.columns]
            results['efficiency_by_match_level'] = efficiency_analysis.reset_index()
        
        # 7. Generate summary statistics
        summary_stats = generate_summary_statistics(df)
        results['summary_statistics'] = summary_stats
        
        # 8. Generate insights
        insights = format_insights(summary_stats)
        results['insights'] = insights
        
        if self.verbose:
            print("   • Analysis complete!")
            print("\n".join(insights))
        
        return results
    
    def save_results(self, df: pd.DataFrame, analysis_results: Dict, output_dir: str):
        """
        Save analysis results to CSV files.
        
        Args:
            df: Processed engagement data
            analysis_results: Analysis results dictionary
            output_dir: Directory to save results
        """
        if self.verbose:
            print(f"💾 Saving results to {output_dir}...")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Save detailed engagement data
        detailed_file = os.path.join(output_dir, ANALYSIS_CONFIG['csv_filename'])
        df.to_csv(detailed_file, index=False)
        
        # 2. Save summary metrics
        summary_file = os.path.join(output_dir, ANALYSIS_CONFIG['summary_filename'])
        
        # Prepare summary data for CSV
        summary_data = []
        
        # Add overall statistics
        stats = analysis_results['summary_statistics']
        summary_data.append({
            'metric_category': 'overall',
            'metric_name': 'total_records',
            'value': stats['total_analysis_records'],
            'description': 'Total learning steps analyzed'
        })
        summary_data.append({
            'metric_category': 'overall', 
            'metric_name': 'unique_users',
            'value': stats['unique_users'],
            'description': 'Number of unique users'
        })
        summary_data.append({
            'metric_category': 'overall',
            'metric_name': 'overall_completion_rate',
            'value': stats['overall_completion_rate'],
            'description': 'Overall completion rate across all steps'
        })
        
        # Add match level completion rates
        match_completion = stats.get('completion_by_match_level', {}).get('mean', {})
        for match_level, rate in match_completion.items():
            summary_data.append({
                'metric_category': 'match_level_completion',
                'metric_name': match_level,
                'value': rate,
                'description': f'Completion rate for {match_level} resources'
            })
        
        # Add brain type completion rates
        brain_completion = stats.get('completion_by_brain_type', {}).get('mean', {})
        for brain_type, rate in brain_completion.items():
            summary_data.append({
                'metric_category': 'brain_type_completion',
                'metric_name': brain_type,
                'value': rate,
                'description': f'Completion rate for {brain_type} learners'
            })
        
        # Save summary CSV
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(summary_file, index=False)
        
        # 3. Save insights as text file
        insights_file = os.path.join(output_dir, 'analysis_insights.txt')
        with open(insights_file, 'w') as f:
            f.write("NeuroNav Engagement Analysis Insights\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("\n".join(analysis_results['insights']))
        
        if self.verbose:
            print(f"   • Detailed data: {detailed_file}")
            print(f"   • Summary metrics: {summary_file}")
            print(f"   • Insights: {insights_file}")
    
    def run_analysis(self, output_dir: str = None):
        """
        Run the complete engagement analysis pipeline.
        
        Args:
            output_dir: Directory to save results (default from config)
        """
        if output_dir is None:
            output_dir = ANALYSIS_CONFIG['output_dir']
        
        print("🚀 Starting NeuroNav Engagement Analysis")
        print("=" * 50)
        
        # Step 1: Connect to database
        self.connect_to_database()
        
        # Step 2: Fetch data
        progress_data, roadmap_data, user_data = self.fetch_data()
        
        # Check if we have enough data
        if len(user_data) < ANALYSIS_CONFIG['min_users_per_brain_type']:
            print(f"⚠️  Insufficient data: Need at least {ANALYSIS_CONFIG['min_users_per_brain_type']} users with brain types")
            return
        
        # Step 3: Preprocess data
        df = self.preprocess_data(progress_data, roadmap_data, user_data)
        
        if df.empty or len(df) < ANALYSIS_CONFIG['min_steps_per_analysis']:
            print(f"⚠️  Insufficient data: Need at least {ANALYSIS_CONFIG['min_steps_per_analysis']} learning steps")
            return
        
        # Step 4: Analyze engagement
        analysis_results = self.analyze_engagement(df)
        
        # Step 5: Save results
        self.save_results(df, analysis_results, output_dir)
        
        print("\n✅ Analysis complete!")
        print(f"📁 Results saved to: {output_dir}")
        
        # Close database connection
        if self.client:
            self.client.close()

def main():
    """Main entry point for the analysis script."""
    parser = argparse.ArgumentParser(description='Analyze NeuroNav engagement and brain-type matching effectiveness')
    parser.add_argument('--output-dir', default=ANALYSIS_CONFIG['output_dir'], 
                       help='Directory to save analysis results')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--mongo-uri', default=MONGO_URI,
                       help='MongoDB connection URI')
    
    args = parser.parse_args()
    
    # Create analyzer and run analysis
    analyzer = NeuroNavAnalyzer(mongo_uri=args.mongo_uri, verbose=args.verbose)
    analyzer.run_analysis(output_dir=args.output_dir)

if __name__ == '__main__':
    main()
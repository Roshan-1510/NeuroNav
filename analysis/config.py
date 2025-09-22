import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/neuronav')

# Analysis parameters
ANALYSIS_CONFIG = {
    # Brain type to resource type preferences (from roadmap generator logic)
    'brain_type_preferences': {
        'Visual': {
            'video': 0.40,
            'tutorial': 0.30,
            'article': 0.20,
            'course': 0.10
        },
        'Auditory': {
            'course': 0.40,
            'video': 0.30,
            'podcast': 0.20,
            'article': 0.10
        },
        'ReadWrite': {
            'article': 0.40,
            'book': 0.30,
            'tutorial': 0.20,
            'course': 0.10
        },
        'Kinesthetic': {
            'tutorial': 0.40,
            'exercise': 0.30,
            'course': 0.20,
            'video': 0.10
        }
    },
    
    # Thresholds for analysis
    'high_preference_threshold': 0.25,  # Resources with >25% preference are "highly matched"
    'low_preference_threshold': 0.15,   # Resources with <15% preference are "poorly matched"
    
    # Minimum data requirements
    'min_users_per_brain_type': 1,     # Minimum users needed for analysis
    'min_steps_per_analysis': 5,       # Minimum steps needed for meaningful analysis
    
    # Output configuration
    'output_dir': 'analysis/results',
    'csv_filename': 'engagement_analysis.csv',
    'summary_filename': 'summary_metrics.csv'
}

# Resource type mappings for consistency
RESOURCE_TYPE_MAPPINGS = {
    'video': 'video',
    'article': 'article', 
    'tutorial': 'tutorial',
    'course': 'course',
    'book': 'article',  # Map books to articles for analysis
    'podcast': 'video',  # Map podcasts to video for analysis (audio content)
    'exercise': 'tutorial'  # Map exercises to tutorials for analysis
}
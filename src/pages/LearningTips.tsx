import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft, 
  Brain, 
  Eye, 
  Headphones, 
  PenTool, 
  Hand,
  Lightbulb,
  BookOpen,
  Target,
  Clock
} from 'lucide-react';
import { useAuth } from '@/lib/api';

const BRAIN_TYPE_ICONS = {
  Visual: Eye,
  Auditory: Headphones,
  ReadWrite: PenTool,
  Kinesthetic: Hand
};

const LEARNING_TIPS = {
  Visual: {
    title: "Visual Learning Strategies",
    description: "You learn best through visual information and spatial understanding.",
    tips: [
      {
        icon: Eye,
        title: "Use Visual Aids",
        description: "Create mind maps, diagrams, and flowcharts to organize information",
        techniques: ["Mind mapping", "Infographics", "Color coding", "Visual diagrams"]
      },
      {
        icon: Target,
        title: "Highlight and Organize",
        description: "Use colors and visual markers to emphasize important concepts",
        techniques: ["Highlighting key points", "Visual timelines", "Sticky notes", "Visual summaries"]
      },
      {
        icon: BookOpen,
        title: "Prefer Visual Resources",
        description: "Choose videos, illustrations, and visual tutorials",
        techniques: ["Educational videos", "Interactive demos", "Visual documentation", "Image-based learning"]
      },
      {
        icon: Clock,
        title: "Study Environment",
        description: "Create a clean, organized visual space for learning",
        techniques: ["Organized workspace", "Good lighting", "Visual reminders", "Clean backgrounds"]
      }
    ]
  },
  Auditory: {
    title: "Auditory Learning Strategies",
    description: "You learn best through listening and verbal communication.",
    tips: [
      {
        icon: Headphones,
        title: "Listen and Discuss",
        description: "Engage with audio content and participate in discussions",
        techniques: ["Podcasts", "Audio lectures", "Group discussions", "Reading aloud"]
      },
      {
        icon: Target,
        title: "Verbal Repetition",
        description: "Repeat information out loud to reinforce learning",
        techniques: ["Verbal summaries", "Teaching others", "Recording yourself", "Rhymes and songs"]
      },
      {
        icon: BookOpen,
        title: "Audio Resources",
        description: "Prefer podcasts, lectures, and audio explanations",
        techniques: ["Audio books", "Recorded lectures", "Voice notes", "Music while studying"]
      },
      {
        icon: Clock,
        title: "Study Habits",
        description: "Schedule regular discussion sessions and verbal reviews",
        techniques: ["Study groups", "Verbal quizzes", "Explaining concepts", "Background music"]
      }
    ]
  },
  ReadWrite: {
    title: "Read/Write Learning Strategies", 
    description: "You learn best through reading and writing activities.",
    tips: [
      {
        icon: PenTool,
        title: "Take Detailed Notes",
        description: "Write comprehensive notes and summaries",
        techniques: ["Detailed note-taking", "Written summaries", "Lists and outlines", "Rewriting concepts"]
      },
      {
        icon: Target,
        title: "Practice Writing",
        description: "Reinforce learning through written exercises",
        techniques: ["Written practice", "Essays", "Journaling", "Written explanations"]
      },
      {
        icon: BookOpen,
        title: "Text-Based Resources",
        description: "Prefer books, articles, and written documentation",
        techniques: ["Reading materials", "Written tutorials", "Documentation", "Text-based research"]
      },
      {
        icon: Clock,
        title: "Study Methods",
        description: "Use reading and writing as primary study methods",
        techniques: ["Reading schedules", "Written reviews", "Text analysis", "Written goals"]
      }
    ]
  },
  Kinesthetic: {
    title: "Kinesthetic Learning Strategies",
    description: "You learn best through hands-on activities and movement.",
    tips: [
      {
        icon: Hand,
        title: "Hands-On Practice",
        description: "Engage in practical exercises and real-world applications",
        techniques: ["Practical exercises", "Hands-on projects", "Building/creating", "Physical models"]
      },
      {
        icon: Target,
        title: "Active Learning",
        description: "Move and engage physically while learning",
        techniques: ["Walking while studying", "Standing desk", "Fidget tools", "Physical breaks"]
      },
      {
        icon: BookOpen,
        title: "Interactive Resources",
        description: "Choose interactive tutorials and practical courses",
        techniques: ["Interactive tutorials", "Simulations", "Lab work", "Trial and error"]
      },
      {
        icon: Clock,
        title: "Study Environment",
        description: "Create an active, engaging learning environment",
        techniques: ["Flexible seating", "Movement breaks", "Physical space", "Activity-based learning"]
      }
    ]
  }
};

export default function LearningTips() {
  const { user } = useAuth();
  const navigate = useNavigate();

  if (!user) {
    navigate('/login');
    return null;
  }

  const brainType = user.brain_type || 'Visual';
  const tips = LEARNING_TIPS[brainType as keyof typeof LEARNING_TIPS];
  const IconComponent = BRAIN_TYPE_ICONS[brainType as keyof typeof BRAIN_TYPE_ICONS];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate('/dashboard')}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
          
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-indigo-100 rounded-full">
              <IconComponent className="h-8 w-8 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{tips.title}</h1>
              <p className="text-gray-600">{tips.description}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-indigo-600" />
            <span className="text-sm text-gray-600">Your Brain Type:</span>
            <Badge variant="secondary" className="bg-indigo-100 text-indigo-700">
              {brainType} Learner
            </Badge>
          </div>
        </div>

        {/* Learning Tips Grid */}
        <div className="grid gap-6 md:grid-cols-2">
          {tips.tips.map((tip, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-indigo-50 rounded-lg">
                    <tip.icon className="h-5 w-5 text-indigo-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{tip.title}</CardTitle>
                    <CardDescription>{tip.description}</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <h4 className="font-medium text-sm text-gray-700 mb-3">Recommended Techniques:</h4>
                  <ul className="space-y-2">
                    {tip.techniques.map((technique, techIndex) => (
                      <li key={techIndex} className="flex items-center gap-2 text-sm text-gray-600">
                        <Lightbulb className="h-3 w-3 text-yellow-500 flex-shrink-0" />
                        {technique}
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Call to Action */}
        <Card className="mt-8 bg-indigo-50 border-indigo-200">
          <CardContent className="p-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-indigo-900 mb-2">
                Ready to Apply Your Learning Style?
              </h3>
              <p className="text-indigo-700 mb-4">
                Use these strategies in your personalized learning roadmaps for better results.
              </p>
              <Button
                onClick={() => navigate('/dashboard')}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                <Target className="mr-2 h-4 w-4" />
                View My Roadmaps
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
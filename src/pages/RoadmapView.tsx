// Copilot, fix roadmap step editing modal
// - Update roadmap steps locally and reflect backend changes


import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  ArrowLeft, 
  Clock, 
  ExternalLink, 
  CheckCircle2, 
  Circle, 
  Play,
  Brain,
  Target,
  Calendar,
  BookOpen,
  Video,
  FileText,
  Code,
  Headphones,
  Edit3,
  Plus,
  Trash2,
  GripVertical,
  Save,
  X
} from 'lucide-react';
import { Roadmap, RoadmapStep, roadmapApi, progressApi } from '@/lib/api';
import EditStepModal from '@/components/EditStepModal';

export default function RoadmapView() {
  const { id } = useParams<{ id: string }>();
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [editingStep, setEditingStep] = useState<RoadmapStep | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [updatingProgress, setUpdatingProgress] = useState<number | null>(null);

  useEffect(() => {
    if (id) {
      loadRoadmap();
    }
  }, [id]);

  const loadRoadmap = async () => {
    if (!id) return;
    
    setLoading(true);
    setError('');
    try {
      const data = await roadmapApi.getRoadmap(id);
      setRoadmap(data);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load roadmap';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleProgressToggle = async (stepNumber: number, completed: boolean) => {
    if (!id || updatingProgress === stepNumber) return;
    
    setUpdatingProgress(stepNumber);
    try {
      await progressApi.updateStepProgress(id, stepNumber, completed);
      
      // Update local state
      setRoadmap(prev => {
        if (!prev) return prev;
        
        const updatedSteps = prev.steps.map(step => 
          step.step_number === stepNumber 
            ? { ...step, completed, completed_at: completed ? new Date().toISOString() : undefined }
            : step
        );
        
        const completedSteps = updatedSteps.filter(step => step.completed).length;
        const completionPercentage = (completedSteps / updatedSteps.length) * 100;
        
        return {
          ...prev,
          steps: updatedSteps,
          progress_summary: {
            total_steps: updatedSteps.length,
            completed_steps: completedSteps,
            completion_percentage: Math.round(completionPercentage * 10) / 10
          }
        };
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update progress';
      setError(errorMessage);
    } finally {
      setUpdatingProgress(null);
    }
  };

  const handleSaveStep = async (stepData: Partial<RoadmapStep>) => {
    if (!id || !roadmap) return;
    
    try {
      if (editingStep) {
        // Update existing step
        const updatedSteps = roadmap.steps.map(step =>
          step.step_number === editingStep.step_number
            ? { ...step, ...stepData }
            : step
        );
        
        await roadmapApi.updateRoadmap(id, { steps: updatedSteps });
      } else {
        // Add new step
        await roadmapApi.addStep(id, stepData);
      }
      
      // Reload roadmap to get updated data
      await loadRoadmap();
      setEditingStep(null);
      setShowAddModal(false);
    } catch (err: unknown) {
      throw new Error(err instanceof Error ? err.message : 'Failed to save step');
    }
  };

  const handleDeleteStep = async (stepNumber: number) => {
    if (!id || !roadmap) return;
    
    if (!confirm('Are you sure you want to delete this step? This action cannot be undone.')) {
      return;
    }
    
    try {
      await roadmapApi.deleteStep(id, stepNumber);
      await loadRoadmap();
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete step';
      setError(errorMessage);
    }
  };

  const handleDeleteRoadmap = async () => {
    if (!id) return;
    
    if (!confirm('Are you sure you want to delete this entire roadmap? This action cannot be undone and will remove all progress.')) {
      return;
    }
    
    try {
      await roadmapApi.deleteRoadmap(id);
      // Redirect to dashboard after deletion
      window.location.href = '/dashboard';
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete roadmap';
      setError(errorMessage);
    }
  };

  const getResourceIcon = (type: string) => {
    const icons = {
      video: Video,
      article: FileText,
      tutorial: Code,
      course: BookOpen,
      podcast: Headphones,
      book: BookOpen,
      exercise: Target,
    };
    const Icon = icons[type as keyof typeof icons] || FileText;
    return <Icon className="h-4 w-4" />;
  };

  const getResourceColor = (type: string) => {
    const colors = {
      video: 'bg-red-100 text-red-700',
      article: 'bg-blue-100 text-blue-700',
      tutorial: 'bg-green-100 text-green-700',
      course: 'bg-purple-100 text-purple-700',
      podcast: 'bg-orange-100 text-orange-700',
      book: 'bg-indigo-100 text-indigo-700',
      exercise: 'bg-yellow-100 text-yellow-700',
    };
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-700';
  };

  const progressPercentage = roadmap?.progress_summary?.completion_percentage || 0;
  const totalTimeMinutes = roadmap?.steps.reduce((sum, step) => sum + step.estimated_time_minutes, 0) || 0;
  const totalHours = Math.round(totalTimeMinutes / 60 * 10) / 10;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Loading roadmap...</p>
        </div>
      </div>
    );
  }

  if (error && !roadmap) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Error Loading Roadmap</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button asChild>
            <Link to="/dashboard">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Dashboard
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  if (!roadmap) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Roadmap not found</h2>
          <Button asChild>
            <Link to="/dashboard">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Dashboard
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <Button variant="ghost" asChild>
              <Link to="/dashboard">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Dashboard
              </Link>
            </Button>
            
            <div className="flex items-center space-x-4">
              <Badge className="bg-blue-100 text-blue-800">
                {roadmap.brain_type} Optimized
              </Badge>
              <Button
                variant={editMode ? "default" : "outline"}
                size="sm"
                onClick={() => setEditMode(!editMode)}
              >
                {editMode ? (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Done Editing
                  </>
                ) : (
                  <>
                    <Edit3 className="mr-2 h-4 w-4" />
                    Edit Roadmap
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDeleteRoadmap}
                className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete Roadmap
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Roadmap Header */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-2xl mb-2">{roadmap.topic}</CardTitle>
                <CardDescription className="text-base">
                  Personalized learning path for {roadmap.brain_type} learners
                </CardDescription>
              </div>
              <Brain className="h-8 w-8 text-blue-600" />
            </div>
          </CardHeader>
          
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{roadmap.steps.length}</div>
                <div className="text-sm text-gray-600">Learning Steps</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{totalHours}h</div>
                <div className="text-sm text-gray-600">Total Time</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{roadmap.estimated_completion_weeks}</div>
                <div className="text-sm text-gray-600">Weeks</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{roadmap.daily_time_minutes}min</div>
                <div className="text-sm text-gray-600">Per Day</div>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progress: {roadmap.progress_summary?.completed_steps || 0} of {roadmap.steps.length} completed</span>
                <span>{Math.round(progressPercentage)}%</span>
              </div>
              <Progress value={progressPercentage} />
            </div>
          </CardContent>
        </Card>

        {/* Learning Steps */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold flex items-center">
              <Target className="mr-2 h-5 w-5" />
              Learning Steps
            </h2>
            {editMode && (
              <Button onClick={() => setShowAddModal(true)} size="sm">
                <Plus className="mr-2 h-4 w-4" />
                Add Step
              </Button>
            )}
          </div>
          
          {roadmap.steps.map((step, index) => {
            const isCompleted = step.completed || false;
            const isUpdating = updatingProgress === step.step_number;
            
            return (
              <Card 
                key={step.step_number} 
                className={`transition-all duration-200 ${
                  isCompleted ? 'bg-green-50 border-green-200' : ''
                }`}
              >
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    {/* Progress Checkbox */}
                    <div className="flex-shrink-0 pt-1">
                      <Checkbox
                        checked={isCompleted}
                        onCheckedChange={(checked) => 
                          handleProgressToggle(step.step_number, checked as boolean)
                        }
                        disabled={isUpdating}
                        className="w-5 h-5"
                      />
                    </div>

                    {/* Step Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className={`text-lg font-semibold ${isCompleted ? 'line-through text-gray-500' : ''}`}>
                          {step.title}
                        </h3>
                        <div className="flex items-center space-x-2">
                          <Badge variant="secondary" className={getResourceColor(step.resource_type)}>
                            {getResourceIcon(step.resource_type)}
                            <span className="ml-1 capitalize">{step.resource_type}</span>
                          </Badge>
                          {step.brain_type_optimized && (
                            <Badge variant="outline" className="text-blue-600 border-blue-200">
                              <Brain className="h-3 w-3 mr-1" />
                              Optimized
                            </Badge>
                          )}
                          {editMode && (
                            <div className="flex items-center space-x-1">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setEditingStep(step)}
                              >
                                <Edit3 className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDeleteStep(step.step_number)}
                                className="text-red-600 hover:text-red-700"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <p className={`text-gray-700 mb-4 ${isCompleted ? 'line-through text-gray-500' : ''}`}>
                        {step.description}
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {step.estimated_time_minutes} min
                          </div>
                          <div className="flex items-center space-x-1">
                            {step.tags?.slice(0, 2).map(tag => (
                              <Badge key={tag} variant="outline" className="text-xs">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                          {isCompleted && step.completed_at && (
                            <div className="flex items-center text-green-600">
                              <CheckCircle2 className="h-4 w-4 mr-1" />
                              Completed {new Date(step.completed_at).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                        
                        <Button 
                          variant={isCompleted ? "outline" : "default"} 
                          size="sm"
                          asChild
                        >
                          <a 
                            href={step.resource_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                          >
                            <ExternalLink className="h-4 w-4 mr-2" />
                            {isCompleted ? 'Review' : 'Start Learning'}
                          </a>
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
                
                {index < roadmap.steps.length - 1 && (
                  <div className="flex justify-center pb-4">
                    <div className="w-0.5 h-6 bg-gray-200"></div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>

        {/* Completion Message */}
        {progressPercentage === 100 && (
          <Card className="mt-8 bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
            <CardContent className="text-center py-8">
              <CheckCircle2 className="h-12 w-12 text-green-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Congratulations! 🎉</h3>
              <p className="text-gray-600 mb-4">
                You've completed your {roadmap.topic} learning roadmap!
              </p>
              <div className="flex justify-center space-x-4">
                <Button asChild>
                  <Link to="/quiz">Create New Roadmap</Link>
                </Button>
                <Button variant="outline" asChild>
                  <Link to="/dashboard">Back to Dashboard</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Edit Step Modal */}
      <EditStepModal
        isOpen={!!editingStep}
        onClose={() => setEditingStep(null)}
        onSave={handleSaveStep}
        step={editingStep}
      />

      {/* Add Step Modal */}
      <EditStepModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSave={handleSaveStep}
        isNew={true}
      />
    </div>
  );
}
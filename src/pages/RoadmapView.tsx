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
<<<<<<< HEAD
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
=======
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
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

<<<<<<< HEAD
const brainTypeGuidance: Record<string, { title: string; description: string; highlight: string[] }> = {
  visual: {
    title: 'Visual learning path',
    description: 'This roadmap emphasizes diagrams, structured examples, and resource previews so you can understand the big picture quickly.',
    highlight: ['Diagrams', 'Pattern matching', 'Example-first'],
  },
  auditory: {
    title: 'Auditory learning path',
    description: 'This roadmap favors explanations, walkthroughs, and discussion-friendly resources that are easier to absorb by listening.',
    highlight: ['Lectures', 'Talk-throughs', 'Discussion'],
  },
  reading: {
    title: 'Reading/Writing learning path',
    description: 'This roadmap uses detailed notes, guides, and summaries so you can process the material through text and reflection.',
    highlight: ['Guides', 'Summaries', 'Note-taking'],
  },
  kinesthetic: {
    title: 'Hands-on learning path',
    description: 'This roadmap leans on practice, exercises, and build-as-you-learn steps so progress feels concrete and active.',
    highlight: ['Projects', 'Exercises', 'Practice'],
  },
};

const getHostname = (url: string) => {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
};

const getStepPhase = (title: string) => {
  const phase = title.split(':')[0]?.trim();
  return phase || 'Step';
};

const sanitizeExternalUrl = (url: string) => {
  const trimmed = (url || '').trim();
  if (!trimmed) return '';
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) return trimmed;
  if (trimmed.startsWith('www.')) return `https://${trimmed}`;
  return `https://${trimmed}`;
};

const fallbackResourceByType: Record<string, string> = {
  video: 'https://www.youtube.com/c/joshstarmer',
  article: 'https://www.khanacademy.org/math/statistics-probability',
  project: 'https://www.kaggle.com/learn',
  tutorial: 'https://www.kaggle.com/learn',
  course: 'https://www.kaggle.com/learn',
  podcast: 'https://www.youtube.com/c/joshstarmer',
  exercise: 'https://www.kaggle.com/learn',
};

=======
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
export default function RoadmapView() {
  const { id } = useParams<{ id: string }>();
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [editingStep, setEditingStep] = useState<RoadmapStep | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [updatingProgress, setUpdatingProgress] = useState<number | null>(null);
<<<<<<< HEAD
  const [regenerating, setRegenerating] = useState(false);
=======
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b

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
<<<<<<< HEAD
      const normalizedSteps = Array.isArray(data.steps) ? data.steps : [];
      const safeRoadmap: Roadmap = {
        ...data,
        topic: data.topic || data.goal || 'Untitled Roadmap',
        brain_type: data.brain_type || 'reading',
        steps: normalizedSteps,
        estimated_completion_weeks: data.estimated_completion_weeks || 1,
        daily_time_minutes: data.daily_time_minutes || 45,
      };
      setRoadmap(safeRoadmap);
=======
      setRoadmap(data);
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
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
<<<<<<< HEAD
      window.dispatchEvent(new CustomEvent('neuronav:progress-updated'));
=======
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
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
<<<<<<< HEAD
      window.dispatchEvent(new CustomEvent('neuronav:progress-updated'));
=======
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
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
<<<<<<< HEAD
      window.dispatchEvent(new CustomEvent('neuronav:progress-updated'));
=======
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
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

<<<<<<< HEAD
  const buildFallbackResourceUrl = (step: RoadmapStep) => {
    const primary = sanitizeExternalUrl(step.resource_url || '');
    if (primary) {
      return primary;
    }

    return fallbackResourceByType[String(step.resource_type || '').toLowerCase()] || '';
  };

  const handleStartLearning = (step: RoadmapStep) => {
    const targetUrl = buildFallbackResourceUrl(step);
    if (!targetUrl) {
      setError('This step does not have a direct resource link yet. Regenerate the roadmap to refresh links.');
      return;
    }
    const popup = window.open(targetUrl, '_blank', 'noopener,noreferrer');
    if (!popup) {
      setError('Could not open resource. Please allow popups for this site and try again.');
    }
  };

  const handleRegenerateRoadmap = async () => {
    if (!id || regenerating) return;

    setRegenerating(true);
    setError('');
    try {
      const response = await roadmapApi.regenerateRoadmap(id, {
        goal: roadmap?.topic,
        brain_type: roadmap?.brain_type,
      });
      setRoadmap(response.roadmap);
      window.dispatchEvent(new CustomEvent('neuronav:progress-updated'));
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to regenerate roadmap';
      setError(errorMessage);
    } finally {
      setRegenerating(false);
    }
  };

  const progressPercentage = roadmap?.progress_summary?.completion_percentage || 0;
  const totalTimeMinutes = roadmap?.steps.reduce((sum, step) => sum + step.estimated_time_minutes, 0) || 0;
  const totalHours = Math.round(totalTimeMinutes / 60 * 10) / 10;
  const roadmapGuidance = roadmap
    ? brainTypeGuidance[roadmap.brain_type?.toLowerCase()] || brainTypeGuidance.reading
    : brainTypeGuidance.reading;

  const completedSteps = roadmap?.steps.filter((step) => step.completed).length || 0;
  const remainingSteps = roadmap?.steps.length ? roadmap.steps.length - completedSteps : 0;
  const activeStep = roadmap?.steps.find((step) => !step.completed) || null;
  const resourceReadySteps = roadmap?.steps.filter((step) => !!buildFallbackResourceUrl(step)).length || 0;
  const missionCoverage = roadmap?.steps.filter((step) => !!step.mission).length || 0;
  const proofCoverage = roadmap?.steps.filter((step) => !!step.proof_of_work).length || 0;
  const winCoverage = roadmap?.steps.filter((step) => !!step.win_condition).length || 0;
  const totalSteps = roadmap?.steps.length || 0;
  const score = totalSteps
    ? Math.round(
        ((resourceReadySteps / totalSteps) * 0.3 +
          (missionCoverage / totalSteps) * 0.2 +
          (proofCoverage / totalSteps) * 0.25 +
          (winCoverage / totalSteps) * 0.25) *
          100
      )
    : 0;
=======
  const progressPercentage = roadmap?.progress_summary?.completion_percentage || 0;
  const totalTimeMinutes = roadmap?.steps.reduce((sum, step) => sum + step.estimated_time_minutes, 0) || 0;
  const totalHours = Math.round(totalTimeMinutes / 60 * 10) / 10;
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b

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
<<<<<<< HEAD
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-72 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.18),_transparent_40%),radial-gradient(circle_at_top_right,_rgba(14,165,233,0.16),_transparent_35%)]" />
      <div className="pointer-events-none absolute -left-32 top-40 h-72 w-72 rounded-full bg-blue-200/25 blur-3xl" />
      <div className="pointer-events-none absolute -right-24 top-96 h-72 w-72 rounded-full bg-cyan-200/30 blur-3xl" />
      {/* Header */}
      <header className="sticky top-0 z-20 border-b border-white/60 bg-white/80 shadow-sm backdrop-blur-xl">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-center justify-between gap-3 py-4">
            <Button variant="ghost" asChild className="shrink-0">
=======
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <Button variant="ghost" asChild>
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
              <Link to="/dashboard">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Dashboard
              </Link>
            </Button>
            
<<<<<<< HEAD
            <div className="flex flex-wrap items-center gap-2 sm:gap-3">
              <Badge className="rounded-full bg-blue-100 px-3 py-1 text-blue-800 shadow-sm">
                {roadmap.brain_type} optimized
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRegenerateRoadmap}
                disabled={regenerating}
              >
                {regenerating ? 'Regenerating...' : 'Regenerate for Brain Type'}
              </Button>
              <Button
=======
            <div className="flex items-center space-x-4">
              <Badge className="bg-blue-100 text-blue-800">
                {roadmap.brain_type} Optimized
              </Badge>
              <Button
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
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

<<<<<<< HEAD
      <div className="relative z-10 mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
=======
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Roadmap Header */}
<<<<<<< HEAD
        <Card className="mb-8 overflow-hidden border-white/60 bg-white/85 shadow-xl shadow-slate-200/60 backdrop-blur">
          <div className="h-2 bg-gradient-to-r from-blue-500 via-cyan-500 to-emerald-400" />
          <CardHeader className="space-y-4 pb-4">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-3xl space-y-3">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="secondary" className="rounded-full bg-blue-50 text-blue-700">
                    {roadmapGuidance.title}
                  </Badge>
                  <Badge variant="outline" className="rounded-full border-slate-200 text-slate-600">
                    {roadmap.steps.length} steps
                  </Badge>
                  <Badge variant="outline" className="rounded-full border-slate-200 text-slate-600">
                    {totalHours}h total
                  </Badge>
                </div>
                <CardTitle className="text-3xl tracking-tight text-slate-900 sm:text-4xl">
                  {roadmap.topic}
                </CardTitle>
                <CardDescription className="max-w-2xl text-base leading-7 text-slate-600">
                  Personalized learning path for {roadmap.brain_type} learners, with direct resources attached to each step instead of vague search links.
                </CardDescription>
              </div>
              <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm">
                <Brain className="h-9 w-9 text-blue-600" />
                <div>
                  <p className="text-xs uppercase tracking-[0.22em] text-slate-500">Brain fit</p>
                  <p className="text-sm font-semibold text-slate-900">{roadmap.brain_type} optimized</p>
                </div>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Learning Steps</div>
                <div className="mt-2 text-3xl font-bold text-slate-900">{roadmap.steps.length}</div>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Total Time</div>
                <div className="mt-2 text-3xl font-bold text-slate-900">{totalHours}h</div>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Timeline</div>
                <div className="mt-2 text-3xl font-bold text-slate-900">{roadmap.estimated_completion_weeks}w</div>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Daily Pace</div>
                <div className="mt-2 text-3xl font-bold text-slate-900">{roadmap.daily_time_minutes}m</div>
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
              <div className="space-y-3 rounded-2xl border border-blue-100 bg-blue-50/70 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
                  <span className="font-medium text-slate-700">
                    Progress: {completedSteps} of {roadmap.steps.length} completed
                  </span>
                  <span className="font-semibold text-blue-700">{Math.round(progressPercentage)}%</span>
                </div>
                <Progress value={progressPercentage} />
                <p className="text-sm leading-6 text-slate-600">
                  {roadmapGuidance.description}
                </p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                <p className="text-sm font-semibold text-slate-900">Learning style signals</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {roadmapGuidance.highlight.map((item) => (
                    <Badge key={item} variant="secondary" className="rounded-full bg-slate-100 text-slate-700">
                      {item}
                    </Badge>
                  ))}
                </div>
                <div className="mt-4 text-sm text-slate-500">
                  {remainingSteps} steps remaining
                </div>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 xl:col-span-1">
                <p className="text-xs font-semibold uppercase tracking-wide text-emerald-700">NeuroNav Score</p>
                <p className="mt-2 text-3xl font-bold text-emerald-900">{score}</p>
                <p className="text-xs text-emerald-800">Outperformance index</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-600">Resource Reliability</p>
                <p className="mt-2 text-2xl font-bold text-slate-900">{totalSteps ? Math.round((resourceReadySteps / totalSteps) * 100) : 0}%</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-600">Mission Coverage</p>
                <p className="mt-2 text-2xl font-bold text-slate-900">{totalSteps ? Math.round((missionCoverage / totalSteps) * 100) : 0}%</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-600">Proof of Work</p>
                <p className="mt-2 text-2xl font-bold text-slate-900">{totalSteps ? Math.round((proofCoverage / totalSteps) * 100) : 0}%</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-600">Win Conditions</p>
                <p className="mt-2 text-2xl font-bold text-slate-900">{totalSteps ? Math.round((winCoverage / totalSteps) * 100) : 0}%</p>
              </div>
            </div>
          </CardHeader>
=======
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
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
        </Card>

        {/* Learning Steps */}
        <div className="space-y-6">
<<<<<<< HEAD
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="flex items-center text-xl font-semibold text-slate-900">
                <Target className="mr-2 h-5 w-5 text-blue-600" />
                Learning Steps
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Each step includes a direct resource, a completion toggle, and a clear learning signal.
              </p>
            </div>
            {editMode && (
              <Button onClick={() => setShowAddModal(true)} size="sm" className="shrink-0">
=======
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold flex items-center">
              <Target className="mr-2 h-5 w-5" />
              Learning Steps
            </h2>
            {editMode && (
              <Button onClick={() => setShowAddModal(true)} size="sm">
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
                <Plus className="mr-2 h-4 w-4" />
                Add Step
              </Button>
            )}
          </div>
<<<<<<< HEAD

          {roadmap.steps.length === 0 ? (
            <Card className="border-amber-200 bg-amber-50">
              <CardContent className="py-8 text-center">
                <h3 className="text-lg font-semibold text-amber-900">This roadmap has no steps yet</h3>
                <p className="mt-2 text-sm text-amber-800">
                  This can happen with older roadmap records. Regenerate to rebuild it with the latest format.
                </p>
                <Button className="mt-4" onClick={handleRegenerateRoadmap} disabled={regenerating}>
                  {regenerating ? 'Regenerating...' : 'Regenerate Roadmap'}
                </Button>
              </CardContent>
            </Card>
          ) : (
          <Tabs defaultValue="timeline" className="w-full">
            <TabsList className="mb-4 grid w-full max-w-sm grid-cols-2 rounded-full bg-slate-100 p-1">
              <TabsTrigger value="timeline" className="rounded-full data-[state=active]:bg-white data-[state=active]:shadow-sm">
                Timeline
              </TabsTrigger>
              <TabsTrigger value="kanban" className="rounded-full data-[state=active]:bg-white data-[state=active]:shadow-sm">
                Kanban
              </TabsTrigger>
            </TabsList>

            <TabsContent value="timeline" className="mt-4 space-y-5">
              {roadmap.steps.map((step, index) => {
                const isCompleted = step.completed || false;
                const isUpdating = updatingProgress === step.step_number;
                const isActive = activeStep?.step_number === step.step_number;
                const stepPhase = getStepPhase(step.title);

                return (
                  <Card
                    key={step.step_number}
                    className={`overflow-hidden border-slate-200 bg-white/90 shadow-sm transition-all duration-200 ${
                      isCompleted ? 'border-emerald-200 bg-emerald-50/70' : ''
                    } ${isActive ? 'ring-2 ring-blue-200 shadow-lg' : ''}`}
                  >
                    <CardContent className="p-0">
                      <div className="grid gap-0 lg:grid-cols-[auto_1fr]">
                        <div className="flex items-start gap-3 border-b border-slate-100 px-5 py-5 lg:border-b-0 lg:border-r lg:px-6 lg:py-6">
                          <div className={`flex h-11 w-11 items-center justify-center rounded-full text-sm font-bold ${isCompleted ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>
                            {step.step_number}
                          </div>
                          <Checkbox
                            checked={isCompleted}
                            onCheckedChange={(checked) => handleProgressToggle(step.step_number, checked as boolean)}
                            disabled={isUpdating}
                            className="mt-2 h-5 w-5"
                          />
                        </div>

                        <div className="space-y-5 px-5 py-5 lg:px-6 lg:py-6">
                          <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                            <div className="space-y-2">
                              <div className="flex flex-wrap items-center gap-2">
                                <Badge variant="secondary" className="rounded-full bg-slate-100 text-slate-700">
                                  {stepPhase}
                                </Badge>
                                {isActive && (
                                  <Badge className="rounded-full bg-blue-100 text-blue-700">
                                    Current step
                                  </Badge>
                                )}
                                {step.brain_type_optimized && (
                                  <Badge variant="outline" className="rounded-full border-blue-200 text-blue-700">
                                    <Brain className="mr-1 h-3 w-3" />
                                    Optimized
                                  </Badge>
                                )}
                              </div>
                              <h3 className={`text-xl font-semibold text-slate-900 ${isCompleted ? 'line-through decoration-2 decoration-emerald-400/70 text-slate-500' : ''}`}>
                                {step.title}
                              </h3>
                              <p className={`max-w-3xl text-sm leading-7 text-slate-600 ${isCompleted ? 'text-slate-500' : ''}`}>
                                {step.description}
                              </p>
                            </div>

                            <div className="flex flex-wrap items-center gap-2">
                              <Badge variant="secondary" className={getResourceColor(step.resource_type)}>
                                {getResourceIcon(step.resource_type)}
                                <span className="ml-1 capitalize">{step.resource_type}</span>
                              </Badge>
                              {editMode && (
                                <div className="flex items-center gap-2">
                                  <Button size="sm" variant="outline" onClick={() => setEditingStep(step)}>
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

                          <div className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-start">
                            <div className="rounded-2xl border border-blue-100 bg-gradient-to-br from-blue-50 to-cyan-50 p-4">
                              <div className="flex items-center justify-between gap-3">
                                <div>
                                  <p className="text-sm font-semibold text-blue-900">Recommended resource</p>
                                  <p className="text-sm text-blue-700">
                                    {step.resource_title || step.resource_type} • {getHostname(step.resource_url || '')}
                                  </p>
                                </div>
                                <ExternalLink className="h-4 w-4 text-blue-500" />
                              </div>
                              <a
                                href={step.resource_url || undefined}
                                target="_blank"
                                rel="noreferrer"
                                className={`mt-3 block text-sm font-medium text-blue-700 underline-offset-4 ${step.resource_url ? 'hover:underline' : 'pointer-events-none text-blue-300'}`}
                              >
                                {step.resource_url ? step.resource_url : 'Direct link will be attached on regenerate'}
                              </a>
                            </div>

                            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                              <div className="flex items-center gap-3 text-sm text-slate-600">
                                <div className="flex items-center">
                                  <Clock className="mr-1 h-4 w-4" />
                                  {step.estimated_time_minutes} min
                                </div>
                                {isCompleted && step.completed_at && (
                                  <div className="flex items-center text-emerald-700">
                                    <CheckCircle2 className="mr-1 h-4 w-4" />
                                    {new Date(step.completed_at).toLocaleDateString()}
                                  </div>
                                )}
                              </div>
                              <div className="mt-3 flex flex-wrap gap-2">
                                {step.tags?.slice(0, 3).map((tag) => (
                                  <Badge key={tag} variant="outline" className="rounded-full text-xs">
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                              <div className="mt-4 flex justify-end">
                                <Button
                                  variant={isCompleted ? 'outline' : 'default'}
                                  size="sm"
                                  onClick={() => handleStartLearning(step)}
                                  disabled={!step.resource_url}
                                >
                                  <ExternalLink className="mr-2 h-4 w-4" />
                                  {isCompleted ? 'Review' : 'Start Learning'}
                                </Button>
                              </div>
                            </div>
                          </div>

                          {(step.mission || step.proof_of_work || step.win_condition || step.speed_boost || step.generic_gap) && (
                            <div className="rounded-2xl border border-violet-200 bg-violet-50/80 p-4">
                              <p className="text-sm font-semibold text-violet-900">NeuroNav Performance Edge</p>
                              <div className="mt-3 grid gap-3 md:grid-cols-2">
                                {step.mission && (
                                  <div>
                                    <p className="text-xs font-semibold uppercase tracking-wide text-violet-700">Mission</p>
                                    <p className="text-sm text-violet-900">{step.mission}</p>
                                  </div>
                                )}
                                {step.proof_of_work && (
                                  <div>
                                    <p className="text-xs font-semibold uppercase tracking-wide text-violet-700">Proof of Work</p>
                                    <p className="text-sm text-violet-900">{step.proof_of_work}</p>
                                  </div>
                                )}
                                {step.win_condition && (
                                  <div>
                                    <p className="text-xs font-semibold uppercase tracking-wide text-violet-700">Win Condition</p>
                                    <p className="text-sm text-violet-900">{step.win_condition}</p>
                                  </div>
                                )}
                                {step.speed_boost && (
                                  <div>
                                    <p className="text-xs font-semibold uppercase tracking-wide text-violet-700">Brain-Type Speed Boost</p>
                                    <p className="text-sm text-violet-900">{step.speed_boost}</p>
                                  </div>
                                )}
                              </div>
                              {step.generic_gap && (
                                <p className="mt-3 rounded-lg border border-violet-200 bg-white/70 p-3 text-sm text-violet-800">
                                  {step.generic_gap}
                                </p>
                              )}

                              {step.learning_contract && (
                                <p className="mt-3 rounded-lg border border-violet-300 bg-violet-100/70 p-3 text-sm text-violet-900">
                                  {step.learning_contract}
                                </p>
                              )}

                              {step.neuronav_engine && (
                                <div className="mt-4 rounded-xl border border-violet-200 bg-white/80 p-4">
                                  <div className="flex flex-wrap items-center gap-2">
                                    {step.neuronav_engine.phase && (
                                      <Badge variant="outline" className="rounded-full border-violet-300 text-violet-800">
                                        Phase: {step.neuronav_engine.phase}
                                      </Badge>
                                    )}
                                    {step.neuronav_engine.focus && (
                                      <Badge variant="outline" className="rounded-full border-violet-300 text-violet-800">
                                        Focus: {step.neuronav_engine.focus}
                                      </Badge>
                                    )}
                                    {step.neuronav_engine.decision_style && (
                                      <Badge variant="outline" className="rounded-full border-violet-300 text-violet-800">
                                        Decision style: {step.neuronav_engine.decision_style}
                                      </Badge>
                                    )}
                                  </div>

                                  {step.neuronav_engine.phase_directive && (
                                    <p className="mt-3 text-sm text-violet-900">
                                      {step.neuronav_engine.phase_directive}
                                    </p>
                                  )}

                                  {step.neuronav_engine.cognitive_loop && (
                                    <div className="mt-3 grid gap-3 md:grid-cols-2">
                                      {step.neuronav_engine.cognitive_loop.encode && (
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-violet-700">Encode</p>
                                          <p className="text-sm text-violet-900">{step.neuronav_engine.cognitive_loop.encode}</p>
                                        </div>
                                      )}
                                      {step.neuronav_engine.cognitive_loop.retrieve && (
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-violet-700">Retrieve</p>
                                          <p className="text-sm text-violet-900">{step.neuronav_engine.cognitive_loop.retrieve}</p>
                                        </div>
                                      )}
                                      {step.neuronav_engine.cognitive_loop.apply && (
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-violet-700">Apply</p>
                                          <p className="text-sm text-violet-900">{step.neuronav_engine.cognitive_loop.apply}</p>
                                        </div>
                                      )}
                                      {step.neuronav_engine.cognitive_loop.review && (
                                        <div>
                                          <p className="text-xs font-semibold uppercase tracking-wide text-violet-700">Review</p>
                                          <p className="text-sm text-violet-900">{step.neuronav_engine.cognitive_loop.review}</p>
                                        </div>
                                      )}
                                    </div>
                                  )}

                                  {step.neuronav_engine.session_plan && (
                                    <div className="mt-3 flex flex-wrap gap-2">
                                      <Badge variant="secondary" className="rounded-full bg-violet-100 text-violet-900">
                                        Warmup {step.neuronav_engine.session_plan.warmup_min || 0}m
                                      </Badge>
                                      <Badge variant="secondary" className="rounded-full bg-violet-100 text-violet-900">
                                        Deep Work {step.neuronav_engine.session_plan.deep_work_min || 0}m
                                      </Badge>
                                      <Badge variant="secondary" className="rounded-full bg-violet-100 text-violet-900">
                                        Synthesis {step.neuronav_engine.session_plan.synthesis_min || 0}m
                                      </Badge>
                                    </div>
                                  )}

                                  {step.neuronav_engine.measurable_validation && (
                                    <p className="mt-3 rounded-lg border border-violet-200 bg-violet-50 p-3 text-sm text-violet-900">
                                      {step.neuronav_engine.measurable_validation}
                                    </p>
                                  )}
                                </div>
                              )}
=======
          
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
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
                            </div>
                          )}
                        </div>
                      </div>
<<<<<<< HEAD
                    </CardContent>

                    {index < roadmap.steps.length - 1 && (
                      <div className="flex justify-center pb-4">
                        <div className="h-8 w-px bg-gradient-to-b from-slate-200 to-transparent" />
                      </div>
                    )}
                  </Card>
                );
              })}
            </TabsContent>

            <TabsContent value="kanban" className="mt-4">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <Card className="border-slate-200 bg-white/90 shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm text-slate-700">To Do</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {roadmap.steps.filter((step) => !step.completed && step !== activeStep).map((step) => (
                      <div key={`todo-${step.step_number}`} className="rounded-xl border border-slate-200 bg-slate-50 p-3">
                        <p className="font-medium text-sm text-slate-900">{step.title}</p>
                        <p className="mt-1 text-xs text-slate-500">
                          {step.resource_type} • {step.estimated_time_minutes} min
                        </p>
                      </div>
                    ))}
                    {!roadmap.steps.filter((step) => !step.completed && step !== activeStep).length && (
                      <p className="text-sm text-slate-500">No remaining backlog.</p>
                    )}
                  </CardContent>
                </Card>

                <Card className="border-blue-200 bg-white/90 shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm text-slate-700">In Progress</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {activeStep ? (
                      <div className="rounded-xl border border-blue-200 bg-blue-50 p-3">
                        <p className="font-medium text-sm text-slate-900">{activeStep.title}</p>
                        <p className="mt-1 text-xs text-slate-600">
                          {activeStep.resource_type} • {activeStep.estimated_time_minutes} min
                        </p>
                        <Button size="sm" className="mt-3" onClick={() => handleStartLearning(activeStep)} disabled={!activeStep.resource_url}>
                          Start Learning
                        </Button>
                      </div>
                    ) : (
                      <p className="text-sm text-slate-500">All steps are complete.</p>
                    )}
                  </CardContent>
                </Card>

                <Card className="border-emerald-200 bg-white/90 shadow-sm">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm text-slate-700">Done</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {roadmap.steps.filter((step) => step.completed).map((step) => (
                      <div key={`done-${step.step_number}`} className="rounded-xl border border-emerald-200 bg-emerald-50 p-3">
                        <p className="font-medium text-sm line-through text-slate-700">{step.title}</p>
                        <p className="mt-1 text-xs text-emerald-700">Completed</p>
                      </div>
                    ))}
                    {!roadmap.steps.filter((step) => step.completed).length && (
                      <p className="text-sm text-slate-500">No completed steps yet.</p>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
          )}
=======
                      
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
>>>>>>> f90bd2a678a3c3dfbdbb9b9a8b54a2f88137d77b
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
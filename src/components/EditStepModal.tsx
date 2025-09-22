import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { X, Plus } from 'lucide-react';
import { RoadmapStep } from '@/lib/api';

interface EditStepModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (stepData: Partial<RoadmapStep>) => Promise<void>;
  step?: RoadmapStep | null;
  isNew?: boolean;
}

export default function EditStepModal({ isOpen, onClose, onSave, step, isNew = false }: EditStepModalProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    resource_url: '',
    resource_type: 'article',
    estimated_time_minutes: 60,
    tags: [] as string[],
    brain_type_optimized: true,
  });
  const [newTag, setNewTag] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (step && !isNew) {
      setFormData({
        title: step.title || '',
        description: step.description || '',
        resource_url: step.resource_url || '',
        resource_type: step.resource_type || 'article',
        estimated_time_minutes: step.estimated_time_minutes || 60,
        tags: step.tags || [],
        brain_type_optimized: step.brain_type_optimized ?? true,
      });
    } else {
      // Reset form for new step
      setFormData({
        title: '',
        description: '',
        resource_url: '',
        resource_type: 'article',
        estimated_time_minutes: 60,
        tags: [],
        brain_type_optimized: true,
      });
    }
    setError('');
  }, [step, isNew, isOpen]);

  const handleInputChange = (field: string, value: unknown) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError('');
  };

  const addTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.title.trim()) {
      setError('Title is required');
      return;
    }
    if (!formData.description.trim()) {
      setError('Description is required');
      return;
    }
    if (!formData.resource_url.trim()) {
      setError('Resource URL is required');
      return;
    }
    if (formData.estimated_time_minutes < 1) {
      setError('Estimated time must be at least 1 minute');
      return;
    }

    setLoading(true);
    try {
      await onSave(formData);
      onClose();
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save step';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isNew ? 'Add New Step' : 'Edit Step'}
          </DialogTitle>
          <DialogDescription>
            {isNew 
              ? 'Create a new learning step for this roadmap'
              : 'Modify the details of this learning step'
            }
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="title">Step Title</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              placeholder="e.g., Introduction to Data Science"
              disabled={loading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="Describe what the learner will do in this step..."
              rows={3}
              disabled={loading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="resource_url">Resource URL</Label>
            <Input
              id="resource_url"
              type="url"
              value={formData.resource_url}
              onChange={(e) => handleInputChange('resource_url', e.target.value)}
              placeholder="https://example.com/resource"
              disabled={loading}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="resource_type">Resource Type</Label>
              <Select 
                value={formData.resource_type} 
                onValueChange={(value) => handleInputChange('resource_type', value)}
                disabled={loading}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="video">Video</SelectItem>
                  <SelectItem value="article">Article</SelectItem>
                  <SelectItem value="tutorial">Tutorial</SelectItem>
                  <SelectItem value="course">Course</SelectItem>
                  <SelectItem value="book">Book</SelectItem>
                  <SelectItem value="podcast">Podcast</SelectItem>
                  <SelectItem value="exercise">Exercise</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="estimated_time">Estimated Time (minutes)</Label>
              <Input
                id="estimated_time"
                type="number"
                min="1"
                value={formData.estimated_time_minutes}
                onChange={(e) => handleInputChange('estimated_time_minutes', parseInt(e.target.value) || 60)}
                disabled={loading}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Tags</Label>
            <div className="flex flex-wrap gap-2 mb-2">
              {formData.tags.map((tag, index) => (
                <Badge key={index} variant="secondary" className="flex items-center gap-1">
                  {tag}
                  <button
                    type="button"
                    onClick={() => removeTag(tag)}
                    className="ml-1 hover:bg-gray-300 rounded-full p-0.5"
                    disabled={loading}
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Add a tag..."
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                disabled={loading}
              />
              <Button type="button" onClick={addTag} variant="outline" size="sm" disabled={loading}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="brain_type_optimized"
              checked={formData.brain_type_optimized}
              onChange={(e) => handleInputChange('brain_type_optimized', e.target.checked)}
              disabled={loading}
            />
            <Label htmlFor="brain_type_optimized">Brain type optimized</Label>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : (isNew ? 'Add Step' : 'Save Changes')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
// Copilot, ensure quiz submission calls backend /quiz route correctly
// - Show brain type and roadmap immediately after submission

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, Brain, CheckCircle, ArrowRight, ArrowLeft } from 'lucide-react';
import { quizApi, QuizQuestion, QuizResponse } from '@/lib/api';

export default function Quiz() {
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [preferences, setPreferences] = useState({
    topic: '',
    intensity: 'intermediate',
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<QuizResponse | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      const data = await quizApi.getQuestions();
      console.log('Quiz data loaded:', data); // Temporary debug log
      setQuestions(data.questions);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load quiz questions';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (value: string) => {
    const questionId = questions[currentQuestion].question_id;
    setAnswers(prev => ({
      ...prev,
      [questionId]: parseInt(value)
    }));
  };

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const canProceed = () => {
    const questionId = questions[currentQuestion]?.question_id;
    return questionId && answers[questionId] !== undefined;
  };

  const isComplete = () => {
    return questions.every(q => answers[q.question_id] !== undefined);
  };

  const submitQuiz = async () => {
    if (!isComplete() || !preferences.topic) {
      setError('Please answer all questions and select your learning topic');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const formattedAnswers = questions.map(q => ({
        question_id: q.question_id,
        selected_option: answers[q.question_id]
      }));

      const response = await quizApi.submitQuiz(formattedAnswers, preferences);
      setResults(response);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to submit quiz';
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading quiz questions...</p>
        </div>
      </div>
    );
  }

  if (results) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-4">
        <div className="max-w-4xl mx-auto">
          <Card className="mb-6">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <CheckCircle className="h-12 w-12 text-green-600" />
              </div>
              <CardTitle className="text-3xl">Assessment Complete!</CardTitle>
              <CardDescription>
                Your brain type has been identified and your personalized roadmap is ready
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {/* Brain Type Results */}
              <div className="bg-blue-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-2">Your Brain Type: {results.assessment_results.brain_type}</h3>
                <p className="text-gray-700 mb-4">{results.brain_type_description.description}</p>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium mb-2">Learning Tips:</h4>
                    <ul className="text-sm space-y-1">
                      {results.brain_type_description.learning_tips.map((tip, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-blue-600 mr-2">•</span>
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Your Strengths:</h4>
                    <ul className="text-sm space-y-1">
                      {results.brain_type_description.strengths.map((strength, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-green-600 mr-2">•</span>
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Confidence Score */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium mb-2">Assessment Confidence</h4>
                <div className="flex items-center space-x-4">
                  <Progress value={results.assessment_results.confidence_score} className="flex-1" />
                  <span className="font-medium">{results.assessment_results.confidence_score.toFixed(1)}%</span>
                </div>
              </div>

              {/* Roadmap Info */}
              <div className="bg-purple-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-2">Your Learning Roadmap</h3>
                <div className="grid md:grid-cols-3 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">{results.roadmap.total_steps}</div>
                    <div className="text-sm text-gray-600">Learning Steps</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">{results.roadmap.estimated_completion_weeks}</div>
                    <div className="text-sm text-gray-600">Weeks to Complete</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">{results.roadmap.daily_time_minutes}</div>
                    <div className="text-sm text-gray-600">Minutes per Day</div>
                  </div>
                </div>
                <p className="text-gray-700 mb-4">
                  Topic: <span className="font-medium">{results.roadmap.topic}</span>
                </p>
              </div>

              {/* Next Steps */}
              <div className="space-y-4">
                <h4 className="font-medium">Next Steps:</h4>
                <ul className="space-y-2">
                  {results.next_steps.map((step, index) => (
                    <li key={index} className="flex items-start">
                      <span className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                        {index + 1}
                      </span>
                      {step}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex gap-4">
                <Button onClick={() => navigate('/dashboard')} className="flex-1">
                  <Brain className="mr-2 h-4 w-4" />
                  Go to Dashboard
                </Button>
                <Button 
                  onClick={() => navigate(`/roadmap/${results.roadmap.roadmap_id}`)} 
                  variant="outline" 
                  className="flex-1"
                >
                  View Roadmap
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const progress = ((Object.keys(answers).length) / questions.length) * 100;
  const question = questions[currentQuestion];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Brain className="mr-2 h-6 w-6" />
              Brain Type Assessment
            </CardTitle>
            <CardDescription>
              Answer honestly - there are no right or wrong answers
            </CardDescription>
          </CardHeader>
        </Card>

        {/* Progress */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Question {currentQuestion + 1} of {questions.length}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
          <Progress value={progress} />
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Question */}
        {question && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">{question.text}</CardTitle>
            </CardHeader>
            <CardContent>
              <RadioGroup
                value={answers[question.question_id]?.toString() || ''}
                onValueChange={handleAnswerChange}
              >
                {question.options.map((option) => (
                  <div key={option.option_id} className="flex items-center space-x-2 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <RadioGroupItem value={option.option_id.toString()} id={`option-${option.option_id}`} />
                    <Label htmlFor={`option-${option.option_id}`} className="flex-1 cursor-pointer">
                      {option.text}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </CardContent>
          </Card>
        )}

        {/* Preferences (show on last question) */}
        {currentQuestion === questions.length - 1 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Learning Preferences</CardTitle>
              <CardDescription>
                Help us personalize your roadmap
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="topic">What would you like to learn?</Label>
                <Select value={preferences.topic} onValueChange={(value) => setPreferences(prev => ({ ...prev, topic: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a learning topic" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Data Science">Data Science</SelectItem>
                    <SelectItem value="Web Development">Web Development</SelectItem>
                    <SelectItem value="Machine Learning">Machine Learning</SelectItem>
                    <SelectItem value="Programming">Programming</SelectItem>
                    <SelectItem value="Design">Design</SelectItem>
                    <SelectItem value="Business">Business</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="intensity">Learning Intensity</Label>
                <Select value={preferences.intensity} onValueChange={(value) => setPreferences(prev => ({ ...prev, intensity: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">Beginner (30 min/day, 8 weeks)</SelectItem>
                    <SelectItem value="intermediate">Intermediate (60 min/day, 6 weeks)</SelectItem>
                    <SelectItem value="advanced">Advanced (90 min/day, 4 weeks)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Navigation */}
        <div className="flex justify-between">
          <Button 
            variant="outline" 
            onClick={prevQuestion}
            disabled={currentQuestion === 0}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Previous
          </Button>
          
          {currentQuestion === questions.length - 1 ? (
            <Button 
              onClick={submitQuiz}
              disabled={!isComplete() || !preferences.topic || submitting}
            >
              {submitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  Complete Assessment
                  <CheckCircle className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          ) : (
            <Button 
              onClick={nextQuestion}
              disabled={!canProceed()}
            >
              Next
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
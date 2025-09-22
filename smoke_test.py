#!/usr/bin/env python3
"""
NeuroNav Smoke Test Script - Milestone 8

This script performs end-to-end testing of the complete NeuroNav user journey:
1. User Registration
2. User Login
3. Quiz Submission (Brain Type Assessment)
4. Roadmap Generation
5. Progress Tracking (Mark Step Complete)

The test validates that all critical functionality works without errors.
"""

import requests
import json
import time
import sys
from datetime import datetime

class NeuroNavSmokeTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user = {
            "name": f"Test User {int(time.time())}",
            "email": f"testuser_{int(time.time())}@smoketest.com",
            "password": "smoketest123"
        }
        self.access_token = None
        self.roadmap_id = None
        self.test_log = []
        
    def log(self, message, success=True):
        """Log test results with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅ PASS" if success else "❌ FAIL"
        log_entry = f"[{timestamp}] {status}: {message}"
        self.test_log.append(log_entry)
        print(log_entry)
        
    def check_backend_health(self):
        """Check if backend is running and healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log("Backend health check passed")
                    return True
                else:
                    self.log(f"Backend unhealthy: {data}", False)
                    return False
            else:
                self.log(f"Backend health check failed: HTTP {response.status_code}", False)
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"Backend connection failed: {e}", False)
            return False
    
    def test_user_registration(self):
        """Test user registration endpoint."""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=self.test_user,
                timeout=10
            )
            
            if response.status_code == 201:
                data = response.json()
                if 'access_token' in data and 'user' in data:
                    self.access_token = data['access_token']
                    self.log(f"User registration successful: {self.test_user['email']}")
                    return True
                else:
                    self.log(f"Registration response missing required fields: {data}", False)
                    return False
            else:
                self.log(f"Registration failed: HTTP {response.status_code} - {response.text}", False)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Registration request failed: {e}", False)
            return False
    
    def test_user_login(self):
        """Test user login endpoint."""
        try:
            login_data = {
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.access_token = data['access_token']
                    self.log("User login successful")
                    return True
                else:
                    self.log(f"Login response missing access_token: {data}", False)
                    return False
            else:
                self.log(f"Login failed: HTTP {response.status_code} - {response.text}", False)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Login request failed: {e}", False)
            return False
    
    def test_quiz_submission(self):
        """Test quiz submission and brain type assessment."""
        try:
            # First get quiz questions
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = self.session.get(
                f"{self.base_url}/quiz/questions",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"Failed to get quiz questions: HTTP {response.status_code}", False)
                return False
            
            questions_data = response.json()
            questions = questions_data.get('questions', [])
            
            if len(questions) < 5:
                self.log(f"Insufficient quiz questions: {len(questions)}", False)
                return False
            
            self.log(f"Retrieved {len(questions)} quiz questions")
            
            # Create sample answers (alternating between options for variety)
            answers = []
            for i, question in enumerate(questions):
                option_count = len(question.get('options', []))
                if option_count > 0:
                    selected_option = i % option_count  # Cycle through options
                    answers.append({
                        "question_id": question['question_id'],
                        "selected_option": selected_option
                    })
            
            # Submit quiz with preferences
            quiz_submission = {
                "answers": answers,
                "preferences": {
                    "topic": "Data Science",
                    "duration": "6 weeks",
                    "intensity": "intermediate"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/quiz/submit",
                json=quiz_submission,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'assessment_results' in data and 'roadmap' in data:
                    brain_type = data['assessment_results'].get('brain_type')
                    self.roadmap_id = data['roadmap'].get('roadmap_id')
                    self.log(f"Quiz submission successful - Brain Type: {brain_type}, Roadmap ID: {self.roadmap_id}")
                    return True
                else:
                    self.log(f"Quiz response missing required fields: {data}", False)
                    return False
            else:
                self.log(f"Quiz submission failed: HTTP {response.status_code} - {response.text}", False)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Quiz submission request failed: {e}", False)
            return False
    
    def test_roadmap_retrieval(self):
        """Test roadmap retrieval endpoint."""
        try:
            if not self.roadmap_id:
                self.log("No roadmap ID available for testing", False)
                return False
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = self.session.get(
                f"{self.base_url}/roadmaps/{self.roadmap_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'steps' in data and len(data['steps']) > 0:
                    step_count = len(data['steps'])
                    self.log(f"Roadmap retrieval successful - {step_count} steps found")
                    return True
                else:
                    self.log(f"Roadmap has no steps: {data}", False)
                    return False
            else:
                self.log(f"Roadmap retrieval failed: HTTP {response.status_code} - {response.text}", False)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Roadmap retrieval request failed: {e}", False)
            return False
    
    def test_progress_tracking(self):
        """Test progress tracking by marking a step as complete."""
        try:
            if not self.roadmap_id:
                self.log("No roadmap ID available for progress testing", False)
                return False
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Mark step 1 as complete
            progress_data = {
                "step_number": 1,
                "completed": True
            }
            
            response = self.session.post(
                f"{self.base_url}/roadmaps/{self.roadmap_id}/progress",
                json=progress_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'roadmap_progress' in data:
                    progress_info = data['roadmap_progress']
                    completed_steps = progress_info.get('completed_steps', 0)
                    completion_percentage = progress_info.get('completion_percentage', 0)
                    self.log(f"Progress tracking successful - {completed_steps} steps completed ({completion_percentage}%)")
                    return True
                else:
                    self.log(f"Progress response missing roadmap_progress: {data}", False)
                    return False
            else:
                self.log(f"Progress tracking failed: HTTP {response.status_code} - {response.text}", False)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Progress tracking request failed: {e}", False)
            return False
    
    def test_progress_retrieval(self):
        """Test progress retrieval endpoint."""
        try:
            if not self.roadmap_id:
                self.log("No roadmap ID available for progress retrieval testing", False)
                return False
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = self.session.get(
                f"{self.base_url}/roadmaps/{self.roadmap_id}/progress",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'progress' in data and 'summary' in data:
                    progress_steps = data['progress']
                    summary = data['summary']
                    completed_count = sum(1 for step in progress_steps if step.get('completed', False))
                    self.log(f"Progress retrieval successful - {completed_count} completed steps found")
                    return True
                else:
                    self.log(f"Progress retrieval response missing required fields: {data}", False)
                    return False
            else:
                self.log(f"Progress retrieval failed: HTTP {response.status_code} - {response.text}", False)
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"Progress retrieval request failed: {e}", False)
            return False
    
    def run_smoke_tests(self):
        """Run all smoke tests in sequence."""
        print("🚀 Starting NeuroNav Smoke Tests")
        print("=" * 60)
        
        test_results = []
        
        # Test 1: Backend Health Check
        test_results.append(("Backend Health Check", self.check_backend_health()))
        
        # Test 2: User Registration
        test_results.append(("User Registration", self.test_user_registration()))
        
        # Test 3: User Login (skip if registration failed)
        if test_results[-1][1]:
            test_results.append(("User Login", self.test_user_login()))
        else:
            test_results.append(("User Login", False))
            self.log("Skipping login test due to registration failure", False)
        
        # Test 4: Quiz Submission (skip if login failed)
        if test_results[-1][1]:
            test_results.append(("Quiz Submission", self.test_quiz_submission()))
        else:
            test_results.append(("Quiz Submission", False))
            self.log("Skipping quiz test due to login failure", False)
        
        # Test 5: Roadmap Retrieval (skip if quiz failed)
        if test_results[-1][1]:
            test_results.append(("Roadmap Retrieval", self.test_roadmap_retrieval()))
        else:
            test_results.append(("Roadmap Retrieval", False))
            self.log("Skipping roadmap test due to quiz failure", False)
        
        # Test 6: Progress Tracking (skip if roadmap failed)
        if test_results[-1][1]:
            test_results.append(("Progress Tracking", self.test_progress_tracking()))
        else:
            test_results.append(("Progress Tracking", False))
            self.log("Skipping progress tracking test due to roadmap failure", False)
        
        # Test 7: Progress Retrieval (skip if progress tracking failed)
        if test_results[-1][1]:
            test_results.append(("Progress Retrieval", self.test_progress_retrieval()))
        else:
            test_results.append(("Progress Retrieval", False))
            self.log("Skipping progress retrieval test due to progress tracking failure", False)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SMOKE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\n📈 Overall Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL SMOKE TESTS PASSED - System is ready for demo!")
            return True
        else:
            print("⚠️  SOME TESTS FAILED - Please check the logs and fix issues before demo")
            return False
    
    def export_test_log(self, filename="smoke_test_log.txt"):
        """Export test log to file."""
        try:
            with open(filename, 'w') as f:
                f.write("NeuroNav Smoke Test Log\n")
                f.write("=" * 50 + "\n")
                f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Backend URL: {self.base_url}\n")
                f.write(f"Test User: {self.test_user['email']}\n")
                f.write("\n" + "=" * 50 + "\n\n")
                
                for log_entry in self.test_log:
                    f.write(log_entry + "\n")
                
                f.write("\n" + "=" * 50 + "\n")
                f.write("End of Test Log\n")
            
            print(f"📄 Test log exported to: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export test log: {e}")
            return False

def main():
    """Main function to run smoke tests."""
    
    # Check if backend URL is provided
    backend_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"🎯 NeuroNav Smoke Test - Milestone 8")
    print(f"🔗 Backend URL: {backend_url}")
    print(f"⏰ Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create and run smoke test
    smoke_test = NeuroNavSmokeTest(backend_url)
    success = smoke_test.run_smoke_tests()
    
    # Export test log
    smoke_test.export_test_log()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
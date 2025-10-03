"""
Firebase service layer for database operations
Handles all Firestore database interactions
"""

from firebase_admin import firestore
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class FirebaseService:
    def __init__(self, db: firestore.Client):
        self.db = db
    
    # Admin operations
    def create_admin(self, admin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new admin user"""
        admin_id = str(uuid.uuid4())
        admin_data.update({
            'id': admin_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        self.db.collection('admins').document(admin_id).set(admin_data)
        return admin_data
    
    def get_admin_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get admin by email"""
        admins = self.db.collection('admins').where(filter=firestore.FieldFilter('email', '==', email)).limit(1).stream()
        for admin in admins:
            return admin.to_dict()
        return None
    
    def get_admin_by_id(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """Get admin by ID"""
        admin_doc = self.db.collection('admins').document(admin_id).get()
        if admin_doc.exists:
            return admin_doc.to_dict()
        return None
    
    # Student operations
    async def create_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new student"""
        student_id = str(uuid.uuid4())
        student_data.update({
            'id': student_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        self.db.collection('students').document(student_id).set(student_data)
        return student_data
    
    async def get_all_students(self) -> List[Dict[str, Any]]:
        """Get all students"""
        students = []
        for doc in self.db.collection('students').stream():
            students.append(doc.to_dict())
        return students
    
    async def get_student_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get student by email"""
        students = self.db.collection('students').where(filter=firestore.FieldFilter('email', '==', email)).limit(1).stream()
        for student in students:
            return student.to_dict()
        return None
    
    async def get_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get student by ID"""
        student_doc = self.db.collection('students').document(student_id).get()
        if student_doc.exists:
            return student_doc.to_dict()
        return None
    
    # Quiz operations
    async def create_quiz(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new quiz"""
        quiz_id = str(uuid.uuid4())
        quiz_data.update({
            'id': quiz_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        print(f"💾 Firebase: Creating quiz with ID: {quiz_id}")
        print(f"📝 Quiz data: {quiz_data}")
        print(f"🗄️  Saving to Firestore collection: quizzes")
        
        self.db.collection('quizzes').document(quiz_id).set(quiz_data)
        print(f"✅ Firebase: Quiz {quiz_id} created successfully")
        print(f"📋 Quiz Title: {quiz_data.get('title', 'No title')}")
        print(f"🎯 Quiz Topic: {quiz_data.get('topic', 'No topic')}")
        print(f"⚡ Quiz Difficulty: {quiz_data.get('difficulty', 'No difficulty')}")
        
        return quiz_data
    
    async def get_quiz_by_id(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """Get quiz by ID"""
        print(f"🔍 Firebase: Getting quiz with ID: {quiz_id}")
        try:
            quiz_doc = self.db.collection('quizzes').document(quiz_id).get()
            if quiz_doc.exists:
                quiz_data = quiz_doc.to_dict()
                quiz_data['id'] = quiz_doc.id
                print(f"✅ Firebase: Found quiz: {quiz_data.get('title', 'No title')}")
                print(f"   Quiz Topic: {quiz_data.get('topic', 'No topic')}")
                print(f"   Quiz Difficulty: {quiz_data.get('difficulty', 'No difficulty')}")
                print(f"   Admin ID: {quiz_data.get('admin_id', 'No admin')}")
                print(f"   Is Active: {quiz_data.get('is_active', False)}")
                return quiz_data
            else:
                print(f"❌ Firebase: Quiz {quiz_id} not found in 'quizzes' collection")
                
                # Debug: Check if any quizzes exist
                print("🔍 Firebase: Checking all quizzes in database...")
                quiz_count = 0
                for doc in self.db.collection('quizzes').limit(5).stream():
                    quiz_count += 1
                    quiz_data = doc.to_dict()
                    print(f"   Found quiz: {doc.id} - {quiz_data.get('title', 'No title')}")
                
                if quiz_count == 0:
                    print("⚠️ Firebase: No quizzes found in database!")
                else:
                    print(f"📊 Firebase: Found {quiz_count} quizzes, but not the requested one")
                
                return None
        except Exception as e:
            print(f"❌ Firebase: Error getting quiz {quiz_id}: {e}")
            return None
    
    async def get_quizzes_by_admin(self, admin_id: str) -> List[Dict[str, Any]]:
        """Get all quizzes for an admin"""
        print(f"🔍 Firebase: Searching for quizzes with admin_id: {admin_id}")
        quizzes = []
        
        try:
            # Remove the order_by to avoid index requirement for now
            query = self.db.collection('quizzes').where(filter=firestore.FieldFilter('admin_id', '==', admin_id))
            docs = query.stream()
            
            for doc in docs:
                quiz_data = doc.to_dict()
                quiz_data['id'] = doc.id
                quizzes.append(quiz_data)
                print(f"📝 Found quiz: {quiz_data.get('title', 'No title')} (ID: {doc.id})")
            
            # Sort in Python instead of Firestore
            quizzes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            print(f"📊 Firebase: Found {len(quizzes)} quizzes for admin {admin_id}")
            
        except Exception as e:
            print(f"❌ Firebase error: {e}")
            
        return quizzes
    
    async def get_all_quizzes(self) -> List[Dict[str, Any]]:
        """Get all quizzes from database (for testing purposes)"""
        print("🔍 Firebase: Getting all quizzes from database")
        quizzes = []
        
        try:
            docs = self.db.collection('quizzes').stream()
            
            for doc in docs:
                quiz_data = doc.to_dict()
                quiz_data['id'] = doc.id
                quizzes.append(quiz_data)
                print(f"📝 Found quiz: {quiz_data.get('title', 'No title')} (ID: {doc.id})")
            
            print(f"📊 Firebase: Found {len(quizzes)} total quizzes")
            
        except Exception as e:
            print(f"❌ Firebase error getting all quizzes: {e}")
            
        return quizzes
    
    async def clear_all_quizzes(self) -> bool:
        """Clear all quizzes from database (for testing)"""
        try:
            print("🗑️ Clearing all quizzes from database...")
            quizzes_ref = self.db.collection('quizzes')
            docs = quizzes_ref.stream()
            
            deleted_count = 0
            for doc in docs:
                doc.reference.delete()
                deleted_count += 1
                print(f"🗑️ Deleted quiz: {doc.id}")
            
            print(f"✅ Deleted {deleted_count} quizzes from database")
            return True
        except Exception as e:
            print(f"❌ Error clearing quizzes: {e}")
            return False
    
    async def update_quiz(self, quiz_id: str, update_data: Dict[str, Any]) -> bool:
        """Update quiz"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            self.db.collection('quizzes').document(quiz_id).update(update_data)
            return True
        except Exception:
            return False
    
    # Question operations
    async def create_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new question"""
        question_id = str(uuid.uuid4())
        question_data.update({
            'id': question_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        self.db.collection('questions').document(question_id).set(question_data)
        return question_data
    
    async def get_questions_by_quiz(self, quiz_id: str) -> List[Dict[str, Any]]:
        """Get all questions for a quiz"""
        print(f"🔍 Firebase: Getting questions for quiz {quiz_id}")
        questions = []
        try:
            # Use new Firestore filter syntax to avoid warnings
            query = self.db.collection('questions').where(filter=firestore.FieldFilter('quiz_id', '==', quiz_id))
            docs = query.stream()
            
            for doc in docs:
                question_data = doc.to_dict()
                question_data['id'] = doc.id
                questions.append(question_data)
                print(f"   ❓ Found question: {question_data.get('question_text', 'No text')[:50]}...")
            
            # Sort by order field in Python
            questions.sort(key=lambda x: x.get('order', 0))
            print(f"✅ Firebase: Found {len(questions)} questions for quiz {quiz_id}")
            return questions
        except Exception as e:
            print(f"❌ Firebase: Error fetching questions for quiz {quiz_id}: {e}")
            return []
    
    # Quiz invitation operations
    async def create_quiz_invitation(self, invitation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new quiz invitation"""
        invitation_id = str(uuid.uuid4())
        invitation_data.update({
            'id': invitation_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        self.db.collection('quiz_invitations').document(invitation_id).set(invitation_data)
        return invitation_data
    
    async def get_invitation_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get invitation by token"""
        print(f"🔍 Firebase: Looking for invitation with token: {token[:10]}...")
        try:
            invitations = self.db.collection('quiz_invitations').where(filter=firestore.FieldFilter('token', '==', token)).limit(1).stream()
            for invitation in invitations:
                invitation_data = invitation.to_dict()
                invitation_data['id'] = invitation.id
                print(f"✅ Firebase: Found invitation for student {invitation_data.get('student_id', 'Unknown')}")
                print(f"   Quiz ID: {invitation_data.get('quiz_id', 'Unknown')}")
                print(f"   Is Used: {invitation_data.get('is_used', False)}")
                return invitation_data
            
            print(f"❌ Firebase: No invitation found for token {token[:10]}...")
            return None
        except Exception as e:
            print(f"❌ Firebase: Error getting invitation by token: {e}")
            return None
    
    async def update_invitation(self, invitation_id: str, update_data: Dict[str, Any]) -> bool:
        """Update invitation"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            self.db.collection('quiz_invitations').document(invitation_id).update(update_data)
            return True
        except Exception:
            return False
    
    # Quiz answer operations
    async def create_quiz_answer(self, answer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new quiz answer"""
        answer_id = str(uuid.uuid4())
        answer_data.update({
            'id': answer_id,
            'submitted_at': datetime.utcnow()
        })
        
        self.db.collection('quiz_answers').document(answer_id).set(answer_data)
        return answer_data
    
    async def get_answers_by_invitation(self, invitation_id: str) -> List[Dict[str, Any]]:
        """Get all answers for an invitation"""
        answers = []
        for doc in self.db.collection('quiz_answers').where(filter=firestore.FieldFilter('invitation_id', '==', invitation_id)).stream():
            answers.append(doc.to_dict())
        return answers
    
    # Quiz result operations
    async def create_quiz_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new quiz result"""
        result_id = str(uuid.uuid4())
        result_data.update({
            'id': result_id,
            'completed_at': datetime.utcnow()
        })
        
        self.db.collection('quiz_results').document(result_id).set(result_data)
        return result_data
    
    async def get_quiz_results_by_quiz(self, quiz_id: str) -> List[Dict[str, Any]]:
        """Get all results for a quiz"""
        try:
            results = []
            # Remove order_by to avoid index requirement, sort in Python instead
            for doc in self.db.collection('quiz_results').where(filter=firestore.FieldFilter('quiz_id', '==', quiz_id)).stream():
                result_data = doc.to_dict()
                result_data['id'] = doc.id
                results.append(result_data)
            
            # Sort by percentage in Python (descending order)
            results.sort(key=lambda x: x.get('percentage', 0), reverse=True)
            return results
        except Exception as e:
            print(f"❌ Firebase: Error fetching results for quiz {quiz_id}: {e}")
            return []
    
    async def update_quiz_result(self, result_id: str, update_data: Dict[str, Any]) -> bool:
        """Update quiz result"""
        try:
            self.db.collection('quiz_results').document(result_id).update(update_data)
            return True
        except Exception:
            return False
    
    # Video submission operations
    async def create_video_submission(self, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new video submission"""
        submission_id = str(uuid.uuid4())
        submission_data.update({
            'id': submission_id,
            'submitted_at': datetime.utcnow()
        })
        
        self.db.collection('video_submissions').document(submission_id).set(submission_data)
        return submission_data
    
    async def get_video_submission_by_id(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get video submission by ID"""
        submission_doc = self.db.collection('video_submissions').document(submission_id).get()
        if submission_doc.exists:
            return submission_doc.to_dict()
        return None
    
    async def get_all_video_submissions(self) -> List[Dict[str, Any]]:
        """Get all video submissions"""
        submissions = []
        for doc in self.db.collection('video_submissions').order_by('submitted_at', direction=firestore.Query.DESCENDING).stream():
            submissions.append(doc.to_dict())
        return submissions
    
    async def get_pending_video_submissions(self) -> List[Dict[str, Any]]:
        """Get all pending video submissions"""
        submissions = []
        for doc in self.db.collection('video_submissions').where(filter=firestore.FieldFilter('is_processed', '==', False)).stream():
            submissions.append(doc.to_dict())
        return submissions
    
    async def update_video_submission(self, submission_id: str, update_data: Dict[str, Any]) -> bool:
        """Update video submission"""
        try:
            self.db.collection('video_submissions').document(submission_id).update(update_data)
            return True
        except Exception:
            return False
    
    # Video transcript operations
    async def create_video_transcript(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new video transcript"""
        transcript_id = str(uuid.uuid4())
        transcript_data.update({
            'id': transcript_id,
            'created_at': datetime.utcnow()
        })
        
        self.db.collection('video_transcripts').document(transcript_id).set(transcript_data)
        return transcript_data
    
    async def get_transcript_by_submission(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get transcript by submission ID"""
        transcripts = self.db.collection('video_transcripts').where(filter=firestore.FieldFilter('video_submission_id', '==', submission_id)).limit(1).stream()
        for transcript in transcripts:
            return transcript.to_dict()
        return None
    
    async def get_processed_submissions_with_transcripts(self) -> List[Dict[str, Any]]:
        """Get all processed submissions with their transcripts"""
        submissions = []
        for doc in self.db.collection('video_submissions').where(filter=firestore.FieldFilter('is_processed', '==', True)).stream():
            submission_data = doc.to_dict()
            # Get transcript
            transcript = await self.get_transcript_by_submission(doc.id)
            if transcript:
                submission_data['transcript'] = transcript
            submissions.append(submission_data)
        
        # Sort by topic coverage
        submissions.sort(key=lambda x: x.get('transcript', {}).get('topic_coverage', 0), reverse=True)
        return submissions
    
    # Quiz results operations
    async def get_all_quiz_results(self) -> List[Dict[str, Any]]:
        """Get all quiz results"""
        results = []
        for doc in self.db.collection('quiz_results').order_by('completed_at', direction=firestore.Query.DESCENDING).stream():
            result_data = doc.to_dict()
            result_data['id'] = doc.id
            results.append(result_data)
        return results
    
    # Quiz invitation operations
    async def get_all_invitations(self) -> List[Dict[str, Any]]:
        """Get all quiz invitations"""
        invitations = []
        for doc in self.db.collection('quiz_invitations').order_by('created_at', direction=firestore.Query.DESCENDING).stream():
            invitation_data = doc.to_dict()
            invitation_data['id'] = doc.id
            invitations.append(invitation_data)
        return invitations
    
    async def get_invitations_by_quiz(self, quiz_id: str) -> List[Dict[str, Any]]:
        """Get all invitations for a specific quiz"""
        invitations = []
        for doc in self.db.collection('quiz_invitations').where(filter=firestore.FieldFilter('quiz_id', '==', quiz_id)).stream():
            invitation_data = doc.to_dict()
            invitation_data['id'] = doc.id
            invitations.append(invitation_data)
        return invitations
    
    async def get_invitations_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all invitations for a specific student"""
        invitations = []
        for doc in self.db.collection('quiz_invitations').where(filter=firestore.FieldFilter('student_id', '==', student_id)).stream():
            invitation_data = doc.to_dict()
            invitation_data['id'] = doc.id
            invitations.append(invitation_data)
        return invitations
    
    async def mark_invitation_as_used(self, invitation_id: str) -> bool:
        """Mark an invitation as used"""
        try:
            self.db.collection('quiz_invitations').document(invitation_id).update({
                'is_used': True,
                'used_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            return True
        except Exception as e:
            print(f"Error marking invitation as used: {e}")
            return False
    
    async def resend_invitation(self, invitation_id: str) -> bool:
        """Resend an invitation (reset sent_at timestamp)"""
        try:
            self.db.collection('quiz_invitations').document(invitation_id).update({
                'sent_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            return True
        except Exception as e:
            print(f"Error resending invitation: {e}")
            return False
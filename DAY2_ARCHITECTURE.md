# Day 2 Architecture: Service Boundaries, Database Schema, API Contracts

## Repository
`Study_Assistant_RAG` — AI-powered study assistant (FastAPI + React + MySQL + Pinecone)

## Proposed Concept
Interactive code learning platform with in-browser playground, auto-graded challenges, progress tracking, badges, certificates, project paths, peer code review, and instructor course authoring (DevAcademy).

## Service Boundaries
| Service | Responsibility | Technology |
|---------|---------------|------------|
| Content Service | Course management, lesson structure, markdown rendering, video embedding | FastAPI, PostgreSQL |
| Playground Service | In-browser code editor, execution sandbox, output capture | FastAPI, Docker, Python/JavaScript/Java/Go |
| Progress Service | Lesson completion, course progress, streaks, analytics | FastAPI, PostgreSQL |
| Assessment Service | Quiz creation, auto-grading, test cases, scoring | FastAPI, PostgreSQL, sandbox |
| Auth Service | Student/educator/admin roles, OAuth2, JWT, MFA | FastAPI, PostgreSQL |
| Collaboration Service | Peer code review, discussions, shared annotations | FastAPI, PostgreSQL, WebSockets |
| Certificate Service | PDF generation, verification URLs, download | FastAPI, reportlab |
| Frontend | React + TypeScript, Vite, Tailwind CSS | React, TypeScript, Vite |

## Database Schema (MySQL 8.0+)
- `users` — id, email, password_hash, role (student/educator/admin), learning_preferences, timezone, created_at
- `courses` — id, title, description, level, topic, duration, instructor_id, status (draft/published), created_at
- `lessons` — id, course_id, title, content (markdown), video_url, order_index, created_at
- `course_enrollments` — id, user_id, course_id, enrolled_at, completed_at, progress_pct
- `lesson_progress` — id, user_id, lesson_id, completed, last_accessed_position, created_at
- `code_submissions` — id, user_id, challenge_id, code, language, test_results, score, created_at
- `challenges` — id, lesson_id, type (multiple_choice/coding/fill_in_blank), test_cases, solution, created_at
- `badges` — id, name, description, criteria, rarity_tier, created_at
- `user_badges` — id, user_id, badge_id, earned_at
- `certificates` — id, user_id, course_id, pdf_url, verification_url, issued_at
- `learning_paths` — id, name, description, course_ids, created_at
- `path_enrollments` — id, user_id, path_id, progress_pct, created_at
- `projects` — id, user_id, title, requirements, rubric, status, grade, created_at
- `peer_reviews` — id, project_id, reviewer_id, rubric_scores, comments, created_at
- `discussions` — id, course_id, thread_id, user_id, content, created_at
- `flashcards` — id, user_id, lesson_id, front, back, next_review, interval, created_at
- `study_notes` — id, user_id, lesson_id, content, created_at

## API Contracts
### Content
- `GET /api/v1/courses` → list (filters: level, topic, duration)
- `GET /api/v1/courses/{id}` → {course, lessons}
- `GET /api/v1/lessons/{id}` → {lesson, content}
- `POST /api/v1/lessons/{id}/complete` → {progress}

### Playground
- `POST /api/v1/playground/execute` — {code, language} → {output, error, executionTime}
- `POST /api/v1/playground/validate` — {code, testCases} → {passed, failed}
- `GET /api/v1/playground/sandbox-status` → {available, limits}

### Progress
- `GET /api/v1/progress` → {courses, completion, streaks}
- `GET /api/v1/progress/{courseId}` → {lessons, completionPct}
- `GET /api/v1/progress/analytics` → {weeklyTrends, subjectMastery}

### Assessment
- `POST /api/v1/assessments/challenges` — {lessonId, type, testCases} → {challenge}
- `POST /api/v1/assessments/submit` — {challengeId, code} → {score, results, feedback}
- `GET /api/v1/assessments/{id}/results` → {score, breakdown}

### Badges & Certificates
- `GET /api/v1/badges` → list
- `GET /api/v1/users/{id}/badges` → list
- `POST /api/v1/certificates/{courseId}/generate` → {pdfUrl, verificationUrl}
- `GET /api/v1/certificates/{verificationUrl}` → {valid, user, course}

### Collaboration
- `POST /api/v1/discussions` — {courseId, content} → {thread}
- `GET /api/v1/discussions/{courseId}` → list
- `POST /api/v1/projects/{id}/review` — {rubricScores, comments} → {review}

## Technical Notes
- Currently FastAPI backend + React frontend; MySQL + Pinecone
- RAG pipeline: document upload → text extraction → chunking → embeddings → Pinecone → semantic search → Gemini generation
- Rate limiting: login 10/min, registration 5/hour, upload 10/hour, chat 30/min
- No multi-document synthesis, flashcards, spaced repetition, quizzes, progress analytics, or collaboration yet
- No AI tutor, no learning style detection, no adaptive difficulty, no exam prep
- No mobile app, no SSO for institutions, no LMS integration

## Day 2 Outcome
Architecture design documented. No code changes. 0 PRs. Ready for Day 3 (CI/CD pipeline).
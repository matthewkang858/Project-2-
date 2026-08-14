# Coursera Feature Verification — "Features v2" tab

Source workbook: `COUR4_Competitive_Research_v3_4.xlsx`, sheet **Features v2**, Coursera section (rows 6–39, 34 features).
Verification date: **2026-08-14**. Method: live web-search evidence (official coursera.org pages, Coursera Help Center, Coursera Blog, investor releases, and reputable third parties).

**Result: 33/34 VERIFIED, 1/34 PARTIALLY VERIFIED.** No feature was found to be retired or fabricated.

## Why there are no screenshots (yet)

This session's network egress policy blocks direct access to coursera.org (proxy returns `403` on CONNECT), for both the headless browser and page fetches, so screenshots could not be captured here. `capture_screenshots.mjs` + `screenshot_manifest.json` are ready to run: from any machine with normal internet access (or a Claude Code environment whose network policy allows coursera.org), run:

```bash
npm install playwright && npx playwright install chromium   # once
node capture_screenshots.mjs screenshot_manifest.json screenshots/
```

It loads each feature's proof URL, scrolls to and outlines the proof text, and saves viewport + full-page PNGs per feature, plus a `capture_results.json` log flagging any page where the proof text was not found.

## Verification matrix

| Row | Feature | Status | Confidence | Evidence (summary) | Proof URL for screenshot |
|---|---|---|---|---|---|
| 6 | Coursera Coach — in-course Q&A | VERIFIED | high | Coursera Coach answers learner questions about course content inside courses; official help-center article "Advance your learning with Coursera AI" describes on-demand Q&A, and third-party reviews confirm Content Q&A ... | https://www.coursera.org/explore/coach |
| 7 | Coursera Coach — video & reading summaries | VERIFIED | high | Coach "provides quick video lecture summaries and resources"; help center: ask Coursera AI to "summarize key points from lectures or readings you've completed". | https://www.coursera.org/explore/coach |
| 8 | Coursera Coach — assignment feedback | VERIFIED | medium | Coach reviews describe "personalized feedback on assignments"; Coursera blog documents AI Grading in Peer Reviews giving immediate rubric-based feedback; Role Play activities end with feedback from Coursera AI. | https://www.coursera.org/explore/coach |
| 9 | Coursera Coach — next-skill suggestions | VERIFIED | medium | Coach "suggests related skills to build" (Skills suggestions listed as a core Coach capability); Coursera blog: Coach identifies transferable skills and recommends tailored learning paths. | https://www.coursera.org/explore/coach |
| 10 | Coach interactive instruction — Socratic dialogue mode | VERIFIED | high | Coursera blog announcement: educators use Coach (Gemini-powered) for immersive activities "starting with Socratic dialogue"; U-M launched the first such course; dialogues trained on course material with instructor-con... | https://blog.coursera.org/announcing-ai-powered-capabilities-enabling-educators-to-use-coursera-coach-to-deliver-interactive-personalized-instruction |
| 11 | Coach interactive instruction — role-based practice | VERIFIED | high | Official help article "Practice your skills with Role Play": ungraded conversational practice with an AI persona (sales pitch, client consultation, job interview) with AI feedback afterward. | https://www.coursera.support/s/article/learner-000002340 |
| 12 | Coach interactive instruction — career-guidance conversations | VERIFIED | medium | Coursera blog/news: Coach helps learners explore career paths, identify transferable skills, and get tailored learning-path recommendations; "Why was this recommended for me" opens a Coach conversation. | https://blog.coursera.org/from-catalog-to-compass |
| 13 | AI-graded assignments | VERIFIED | high | Live course pages display an "AI Graded — see disclaimer" tag in the Assessments section (e.g. "Integrate AI Insights", "AI for Education" courses); Coursera blog documents AI Grading in Peer Reviews using instructor ... | https://www.coursera.org/learn/ai-for-education-advanced |
| 14 | AI-translated courses & subtitles | VERIFIED | high | Coursera blogs: AI-powered translations expanded to 17 popular languages covering 4,000+ courses/600+ Specializations; ~4,000 courses translated into Hindi; nearly 3M learners across 5,000+ courses in 25 languages; Ge... | https://blog.coursera.org/coursera-expands-ai-powered-translations-to-17-popular-languages |
| 15 | Personalized recommendations | VERIFIED | high | Coursera blog "From catalog to compass": sign-up career quiz drives personalized content recommendations plus a top recommendation, with Coach explaining why; learners receiving personalized recommendations enroll more. | https://blog.coursera.org/from-catalog-to-compass |
| 16 | Guided Projects | VERIFIED | high | Learn a job-relevant skill in under 2 hours in a split-screen interface with a pre-configured cloud desktop in the browser; priced from $9.99; live catalog page on coursera.org. | https://www.coursera.org/courses?query=guided+projects |
| 17 | Specializations (multi-course series) | VERIFIED | high | 3–6 course series building to a capstone/hands-on project; most run on subscription with a 7-day free trial; capstone typically gated on completing the other courses. | https://www.coursera.org/articles/what-is-coursera |
| 18 | Professional Certificates (industry-built programs) | VERIFIED | high | Job-ready credentials built by Google, IBM, Meta, Microsoft; 150+ programs; designed to take beginners to entry-level employment in 3–8 months; 30+ carry ACE/ECTS/NSQF credit recommendations. | https://www.coursera.org/professional-certificates/google-it-support |
| 19 | Graded quizzes | VERIFIED | high | Audit mode excludes graded items; quizzes counting toward completion and certificates unlock with paid enrollment/Plus — matches sheet tiering ("Audit = view materials only"). | https://www.coursera.org/learn/machine-learning |
| 20 | Auto-graded programming assignments | VERIFIED | medium | Programming assignments auto-graded in-platform (standard on programming courses; e.g. DeepLearning.AI publishes its dlai-grader autograder); paid-tier gating same as quizzes. | https://www.coursera.org/learn/python |
| 21 | Peer-reviewed assignments | VERIFIED | high | Class Central (2026): 3,302 of 13,346 active Coursera courses (25%) include peer-reviewed assessments; learners grade ~3 peer submissions against instructor rubrics. | https://www.classcentral.com/report/courses-with-peer-reviews/ |
| 22 | Discussion forums | VERIFIED | high | Per-course discussion boards are a documented core feature (threads with posts and comments); audit learners get some forum access. | https://www.coursera.support/s/community |
| 23 | Shareable course certificates | VERIFIED | high | Digital credential with unique verification URL and one-click "Add to LinkedIn" into Licenses & Certifications; paid enrollments only (audits earn none) — matches sheet tiering. | https://www.coursera.org/courseraplus |
| 24 | MasterTrack certificates | VERIFIED | high | Still live in 2026: coursera.org/mastertrack active, dedicated help-center topic exists, and 6 new MasterTracks from Indian universities launched Jan 27, 2026. Caveat: some legacy programs migrated/renamed (e.g. U-M S... | https://www.coursera.org/mastertrack |
| 25 | Online degrees | VERIFIED | high | Full online bachelor's/master's from accredited universities with separate admission and tuition (e.g. UIUC MS Management $13,644; pay-as-you-go options) — coursera.org/degrees is live. | https://www.coursera.org/degrees |
| 26 | Weekly learning goals | VERIFIED | high | Official Coursera Help Center topic "Weekly goal" exists; app supports daily/weekly goal setting with a progress tracker in the dashboard. | https://www.coursera.support/s/topic/0TOVH0000009Cuo4AE |
| 27 | Streaks | PARTIALLY VERIFIED | low | Weekly-goal tracking is confirmed (official help topic), but no public Coursera page naming a "streak" mechanic was found in this run — the streak UI appears inside the logged-in app experience. Needs an in-app screen... | https://www.coursera.support/s/topic/0TOVH0000009Cuo4AE |
| 28 | Study reminders | VERIFIED | medium | Coursera blog announced mobile learning reminders (transcripts/notes/reminders release); the app lets users schedule a time to learn with reminder notifications. | https://blog.coursera.org/new-mobile-features-transcripts-notes-reminders |
| 29 | Mobile apps (iOS/Android) | VERIFIED | high | Official Coursera apps on the Apple App Store and Google Play with the full course experience. | https://apps.apple.com/us/app/coursera-build-new-skills/id736535961 |
| 30 | Offline downloads | VERIFIED | high | Course videos downloadable for offline viewing on iOS ("Download Videos") and Android ("Save for Offline"); graded quizzes, peer reviews, proctored exams, and labs excluded. | https://blog.coursera.org/mobile-offline-features |
| 31 | Course library & catalog | VERIFIED | high | coursera.org/courseraplus page title: "Unlimited Access to 10000+ Online Courses"; 350+ university/company partners; Plus covers 90%+ of courses, Projects, Specializations and Professional Certificates — matches the s... | https://www.coursera.org/courseraplus |
| 32 | Career Academy (role explorer) | VERIFIED | high | coursera.org/career-academy is live; salary and job-opening data sourced from the US Lightcast Job Postings Report per the official Career Academy FAQ (e.g. $90,500 median / 82,489 openings for data analytics). Role c... | https://www.coursera.org/career-academy |
| 33 | Career Academy (sponsored catalog) | VERIFIED | high | Official FAQ: "Career Academy is for learners who are part of a learning program that is sponsored by your company or institution", granting entry-level Professional Certificates; numerous sponsor pages (Chico State, ... | https://www.coursera.support/s/article/learner-000001684 |
| 34 | Career resource hub & aptitude test | VERIFIED | high | coursera.org/resources ("Career Resource Hub: Free Tools to Shape Your Career") and the free career quiz at coursera.org/resources/career-quiz (aptitude test across six professional domains) are both live and public. | https://www.coursera.org/resources/career-quiz |
| 35 | Third-party cert alignment & exam discounts | VERIFIED | medium | Google IT Support ↔ CompTIA A+ alignment with 30% exam discount confirmed (Coursera blog, grow.google, live support threads; discounted price $177.10 matches the sheet). Caveat: sources differ on the base price ($253 ... | https://www.coursera.org/professional-certificates/google-it-support |
| 36 | Partner-funded scholarships | VERIFIED | high | Universal Access to Microsoft Skills Scholarship with Women in Cloud confirmed: 5,000 recipients, all Microsoft Specializations & Professional Certificates ($6,000 stated value), complimentary Microsoft certification ... | https://blog.coursera.org/announcing-four-new-entry-level-certificates-and-universal-skills-scholarship-program-from-microsoft-to-help-learners-land-in-demand-jobs |
| 37 | Learner community (standalone) | VERIFIED | high | Platform-wide Coursera Community (launched late 2018) exists separately from per-course forums, with subject boards and Common Rooms; official community pages live on coursera.support. | https://www.coursera.support/s/community |
| 38 | Accessibility statement | VERIFIED | high | Official "Coursera's accessibility policy" help article: commitment to access for learners with disabilities, WCAG 2.2 AA target, captioning on all lecture videos, accessibility email alias, plus a separate accommodat... | https://www.coursera.support/s/article/learner-000001351 |
| 39 | Coursera Podcast | VERIFIED | high | "The Coursera Podcast" is live on Spotify and Apple Podcasts with recent episodes (guests incl. Moderna's Chief Learning Officer, Class Central's CEO, Dr. Barbara Oakley). | https://podcasts.apple.com/us/podcast/the-coursera-podcast/id1708599019 |

## Findings that need attention

1. **Row 27 — Streaks (PARTIALLY VERIFIED).** Weekly-goal tracking is officially documented, but no public page names a "streak" mechanic — it lives inside the logged-in app. Capture the mobile-app home screen (streak widget) to close this.
2. **Row 32 — Career Academy role count.** Sources disagree: 52 roles in one 2026 snapshot vs 60 in Coursera's blog (and the sheet). Re-count on the live page when capturing screenshots.
3. **Row 35 — Exam discounts.** The 30% CompTIA A+ discount and $177.10 price are confirmed; the *base* price differs across sources ($253 older vs $274 in the sheet's 8/3/26 article — CompTIA price increases). The Microsoft 50%-off voucher sub-claim was not directly confirmed; verify against the msfthub page cited in the sheet.
4. **Row 36 — Microsoft/Women in Cloud scholarship.** Program fully confirmed, but the application portal is labeled 2024–25; confirm the window is still open before citing "applications open".
5. **Row 24 — MasterTrack churn.** The product line is alive (6 new MasterTracks launched Jan 2026), but individual programs migrate off-platform (e.g. U-M Social Work). Verify any specific program you cite.
6. **Rows 17/18 — Plus exclusions.** The sheet's own "TO CONFIRM" note (some Google Professional Certificates excluded from Coursera Plus) still needs an on-platform enrollment check; public sources only say Plus covers "90%+" of the catalog.

## Per-feature evidence and sources

### Row 6 — Coursera Coach — in-course Q&A

**Status:** VERIFIED (confidence: high)

Coursera Coach answers learner questions about course content inside courses; official help-center article "Advance your learning with Coursera AI" describes on-demand Q&A, and third-party reviews confirm Content Q&A across 7,000+ courses.

Sources:
- https://www.coursera.support/s/article/learner-000002224
- https://aisuggests.ai/tool/coursera-coach
- https://skillsetcourse.com/tools/coursera-coach

Screenshot target: `https://www.coursera.org/explore/coach` — look for “Coursera Coach”

### Row 7 — Coursera Coach — video & reading summaries

**Status:** VERIFIED (confidence: high)

Coach "provides quick video lecture summaries and resources"; help center: ask Coursera AI to "summarize key points from lectures or readings you've completed".

Sources:
- https://www.coursera.support/s/article/learner-000002224
- https://blog.coursera.org/new-products-tools-and-features-2023

Screenshot target: `https://www.coursera.org/explore/coach` — look for “summar”

### Row 8 — Coursera Coach — assignment feedback

**Status:** VERIFIED (confidence: medium)

Coach reviews describe "personalized feedback on assignments"; Coursera blog documents AI Grading in Peer Reviews giving immediate rubric-based feedback; Role Play activities end with feedback from Coursera AI.

Sources:
- https://aisuggests.ai/tool/coursera-coach
- https://blog.coursera.org/ai-grading-in-peer-reviews-enhancing-courseras-learning-experience-with-faster-high-quality-feedback/
- https://www.coursera.support/s/article/learner-000002340

Screenshot target: `https://www.coursera.org/explore/coach` — look for “feedback”

### Row 9 — Coursera Coach — next-skill suggestions

**Status:** VERIFIED (confidence: medium)

Coach "suggests related skills to build" (Skills suggestions listed as a core Coach capability); Coursera blog: Coach identifies transferable skills and recommends tailored learning paths.

Sources:
- https://aisuggests.ai/tool/coursera-coach
- https://blog.coursera.org/announcing-ai-powered-capabilities-enabling-educators-to-use-coursera-coach-to-deliver-interactive-personalized-instruction

Screenshot target: `https://www.coursera.org/explore/coach` — look for “skills”

### Row 10 — Coach interactive instruction — Socratic dialogue mode

**Status:** VERIFIED (confidence: high)

Coursera blog announcement: educators use Coach (Gemini-powered) for immersive activities "starting with Socratic dialogue"; U-M launched the first such course; dialogues trained on course material with instructor-configured rubrics.

Sources:
- https://blog.coursera.org/announcing-ai-powered-capabilities-enabling-educators-to-use-coursera-coach-to-deliver-interactive-personalized-instruction
- https://news.umich.edu/u-m-launches-ai-powered-coursera-coach-for-interactive-instruction

Screenshot target: `https://blog.coursera.org/announcing-ai-powered-capabilities-enabling-educators-to-use-coursera-coach-to-deliver-interactive-personalized-instruction` — look for “Socratic”

### Row 11 — Coach interactive instruction — role-based practice

**Status:** VERIFIED (confidence: high)

Official help article "Practice your skills with Role Play": ungraded conversational practice with an AI persona (sales pitch, client consultation, job interview) with AI feedback afterward.

Sources:
- https://www.coursera.support/s/article/learner-000002340
- https://www.edtechinnovationhub.com/news/coursera-unveils-new-ai-tools-designed-to-boost-workforce-and-campus-learning

Screenshot target: `https://www.coursera.support/s/article/learner-000002340` — look for “Role Play”

### Row 12 — Coach interactive instruction — career-guidance conversations

**Status:** VERIFIED (confidence: medium)

Coursera blog/news: Coach helps learners explore career paths, identify transferable skills, and get tailored learning-path recommendations; "Why was this recommended for me" opens a Coach conversation.

Sources:
- https://blog.coursera.org/announcing-ai-powered-capabilities-enabling-educators-to-use-coursera-coach-to-deliver-interactive-personalized-instruction
- https://blog.coursera.org/from-catalog-to-compass

Screenshot target: `https://blog.coursera.org/from-catalog-to-compass` — look for “career”

### Row 13 — AI-graded assignments

**Status:** VERIFIED (confidence: high)

Live course pages display an "AI Graded — see disclaimer" tag in the Assessments section (e.g. "Integrate AI Insights", "AI for Education" courses); Coursera blog documents AI Grading in Peer Reviews using instructor rubrics.

Sources:
- https://blog.coursera.org/ai-grading-in-peer-reviews-enhancing-courseras-learning-experience-with-faster-high-quality-feedback/
- https://www.coursera.org/learn/ai-for-education-advanced

Screenshot target: `https://www.coursera.org/learn/ai-for-education-advanced` — look for “AI Graded”

### Row 14 — AI-translated courses & subtitles

**Status:** VERIFIED (confidence: high)

Coursera blogs: AI-powered translations expanded to 17 popular languages covering 4,000+ courses/600+ Specializations; ~4,000 courses translated into Hindi; nearly 3M learners across 5,000+ courses in 25 languages; GenAI dubbing for 100+ courses. Sheet's "20+ languages, thousands of courses" is consistent.

Sources:
- https://blog.coursera.org/coursera-expands-ai-powered-translations-to-17-popular-languages
- https://blog.coursera.org/coursera-launches-ai-dubbed-courses-in-spanish-french-brazilian-portuguese-and-german
- https://indiaai.gov.in/news/coursera-translates-4-000-courses-in-hindi-using-generative-ai

Screenshot target: `https://blog.coursera.org/coursera-expands-ai-powered-translations-to-17-popular-languages` — look for “languages”

### Row 15 — Personalized recommendations

**Status:** VERIFIED (confidence: high)

Coursera blog "From catalog to compass": sign-up career quiz drives personalized content recommendations plus a top recommendation, with Coach explaining why; learners receiving personalized recommendations enroll more.

Sources:
- https://blog.coursera.org/from-catalog-to-compass
- https://www.coursera.org/resources/career-quiz

Screenshot target: `https://blog.coursera.org/from-catalog-to-compass` — look for “recommend”

### Row 16 — Guided Projects

**Status:** VERIFIED (confidence: high)

Learn a job-relevant skill in under 2 hours in a split-screen interface with a pre-configured cloud desktop in the browser; priced from $9.99; live catalog page on coursera.org.

Sources:
- https://www.coursera.org/courses?query=guided+projects
- https://medium.com/@cyril_anderson/hands-on-with-coursera-guided-projects-53dd056daa66

Screenshot target: `https://www.coursera.org/courses?query=guided+projects` — look for “Guided Project”

### Row 17 — Specializations (multi-course series)

**Status:** VERIFIED (confidence: high)

3–6 course series building to a capstone/hands-on project; most run on subscription with a 7-day free trial; capstone typically gated on completing the other courses.

*Caveat:* Sheet "TO CONFIRM" note on some Google Prof Certs excluded from Plus remains open — needs an on-platform enrollment check.

Sources:
- https://www.coursera.org/articles/what-is-coursera
- https://www.classcentral.com/help/what-are-coursera-specializations

Screenshot target: `https://www.coursera.org/articles/what-is-coursera` — look for “Specialization”

### Row 18 — Professional Certificates (industry-built programs)

**Status:** VERIFIED (confidence: high)

Job-ready credentials built by Google, IBM, Meta, Microsoft; 150+ programs; designed to take beginners to entry-level employment in 3–8 months; 30+ carry ACE/ECTS/NSQF credit recommendations.

Sources:
- https://www.coursera.org/certificates/prepare-for-a-certification
- https://investor.coursera.com/news/news-details/2024/Twelve-Google-and-IBM-Professional-Certificates-on-Coursera-Receive-ECTS-Credit-Recommendations/default.aspx
- https://blog.coursera.org/coursera-microcredential-momentum

Screenshot target: `https://www.coursera.org/professional-certificates/google-it-support` — look for “Professional Certificate”

### Row 19 — Graded quizzes

**Status:** VERIFIED (confidence: high)

Audit mode excludes graded items; quizzes counting toward completion and certificates unlock with paid enrollment/Plus — matches sheet tiering ("Audit = view materials only").

Sources:
- https://www.coursmos.com/audit-coursera-courses/
- https://www.classcentral.com/report/coursera-signup-for-free/

Screenshot target: `https://www.coursera.org/learn/machine-learning` — look for “quiz”

### Row 20 — Auto-graded programming assignments

**Status:** VERIFIED (confidence: medium)

Programming assignments auto-graded in-platform (standard on programming courses; e.g. DeepLearning.AI publishes its dlai-grader autograder); paid-tier gating same as quizzes.

Sources:
- https://www.quora.com/How-are-assigments-and-assessments-on-Coursera-graded
- https://pypi.org/project/dlai-grader/1.2.0

Screenshot target: `https://www.coursera.org/learn/python` — look for “assignment”

### Row 21 — Peer-reviewed assignments

**Status:** VERIFIED (confidence: high)

Class Central (2026): 3,302 of 13,346 active Coursera courses (25%) include peer-reviewed assessments; learners grade ~3 peer submissions against instructor rubrics.

Sources:
- https://www.classcentral.com/report/courses-with-peer-reviews/
- https://blog.coursera.org/ai-grading-in-peer-reviews-enhancing-courseras-learning-experience-with-faster-high-quality-feedback/

Screenshot target: `https://www.classcentral.com/report/courses-with-peer-reviews/` — look for “peer”

### Row 22 — Discussion forums

**Status:** VERIFIED (confidence: high)

Per-course discussion boards are a documented core feature (threads with posts and comments); audit learners get some forum access.

Sources:
- https://www.andrewhuwong.com/coursera-discussion-board-evaluation
- https://online.duke.edu/coursera-forums-why-students-dont-like-to-have-graded-discussions-4/

Screenshot target: `https://www.coursera.support/s/community` — look for “discussion”

### Row 23 — Shareable course certificates

**Status:** VERIFIED (confidence: high)

Digital credential with unique verification URL and one-click "Add to LinkedIn" into Licenses & Certifications; paid enrollments only (audits earn none) — matches sheet tiering.

Sources:
- https://blog.coursera.org/add-coursera-accomplishments-to-your-linkedin
- https://certfusion.com/r/coursera-shareable-certificates-explained-everything-you-need-to-know

Screenshot target: `https://www.coursera.org/courseraplus` — look for “certificate”

### Row 24 — MasterTrack certificates

**Status:** VERIFIED (confidence: high)

Still live in 2026: coursera.org/mastertrack active, dedicated help-center topic exists, and 6 new MasterTracks from Indian universities launched Jan 27, 2026. Caveat: some legacy programs migrated/renamed (e.g. U-M Social Work MasterTrack closed to new registration Oct 2024, relaunched off-platform Jan 2025).

*Caveat:* Program churn: verify the specific MasterTracks you cite are still enrolling.

Sources:
- https://www.coursera.org/mastertrack
- https://www.coursera.support/s/topic/0TO8W000000y5ycWAA/mastertrack-certificate
- https://www.classcentral.com/microcredentials/coursera-master-track

Screenshot target: `https://www.coursera.org/mastertrack` — look for “MasterTrack”

### Row 25 — Online degrees

**Status:** VERIFIED (confidence: high)

Full online bachelor's/master's from accredited universities with separate admission and tuition (e.g. UIUC MS Management $13,644; pay-as-you-go options) — coursera.org/degrees is live.

Sources:
- https://www.coursera.org/degrees
- https://www.coursera.org/degrees/masters

Screenshot target: `https://www.coursera.org/degrees` — look for “degree”

### Row 26 — Weekly learning goals

**Status:** VERIFIED (confidence: high)

Official Coursera Help Center topic "Weekly goal" exists; app supports daily/weekly goal setting with a progress tracker in the dashboard.

Sources:
- https://www.coursera.support/s/topic/0TOVH0000009Cuo4AE
- https://www.entrepreneursera.com/coursera-app/

Screenshot target: `https://www.coursera.support/s/topic/0TOVH0000009Cuo4AE` — look for “Weekly goal”

### Row 27 — Streaks

**Status:** PARTIALLY VERIFIED (confidence: low)

Weekly-goal tracking is confirmed (official help topic), but no public Coursera page naming a "streak" mechanic was found in this run — the streak UI appears inside the logged-in app experience. Needs an in-app screenshot to close.

*Caveat:* Could not verify from public web; check the mobile app home screen (streak widget) when capturing screenshots.

Sources:
- https://www.coursera.support/s/topic/0TOVH0000009Cuo4AE

Screenshot target: `https://www.coursera.support/s/topic/0TOVH0000009Cuo4AE` — look for “streak”

### Row 28 — Study reminders

**Status:** VERIFIED (confidence: medium)

Coursera blog announced mobile learning reminders (transcripts/notes/reminders release); the app lets users schedule a time to learn with reminder notifications.

Sources:
- https://blog.coursera.org/new-mobile-features-transcripts-notes-reminders
- https://emmardesigns.com/coursera-case-study/

Screenshot target: `https://blog.coursera.org/new-mobile-features-transcripts-notes-reminders` — look for “reminder”

### Row 29 — Mobile apps (iOS/Android)

**Status:** VERIFIED (confidence: high)

Official Coursera apps on the Apple App Store and Google Play with the full course experience.

Sources:
- https://podcasts.apple.com/us/podcast/the-coursera-podcast/id1708599019
- https://blog.coursera.org/this-holiday-season-learn-on-the-go-with-the-new/
- https://www.classcentral.com/help/coursera-mobile-app

Screenshot target: `https://apps.apple.com/us/app/coursera-build-new-skills/id736535961` — look for “Coursera”

### Row 30 — Offline downloads

**Status:** VERIFIED (confidence: high)

Course videos downloadable for offline viewing on iOS ("Download Videos") and Android ("Save for Offline"); graded quizzes, peer reviews, proctored exams, and labs excluded.

Sources:
- https://blog.coursera.org/mobile-offline-features
- https://www.classcentral.com/help/coursera-mobile-app

Screenshot target: `https://blog.coursera.org/mobile-offline-features` — look for “offline”

### Row 31 — Course library & catalog

**Status:** VERIFIED (confidence: high)

coursera.org/courseraplus page title: "Unlimited Access to 10000+ Online Courses"; 350+ university/company partners; Plus covers 90%+ of courses, Projects, Specializations and Professional Certificates — matches the sheet's updated 10,000+/350+/90% figures.

Sources:
- https://www.coursera.org/courseraplus
- https://www.coursera.org/articles/what-is-coursera

Screenshot target: `https://www.coursera.org/courseraplus` — look for “10,000”

### Row 32 — Career Academy (role explorer)

**Status:** VERIFIED (confidence: high)

coursera.org/career-academy is live; salary and job-opening data sourced from the US Lightcast Job Postings Report per the official Career Academy FAQ (e.g. $90,500 median / 82,489 openings for data analytics). Role count discrepancy: one snapshot shows 52 career options vs the sheet's 60 (blog said "60 in-demand roles") — count drifts over time.

*Caveat:* Role count varies by snapshot (52 vs 60); re-count on screenshot day.

Sources:
- https://www.coursera.org/career-academy
- https://www.coursera.support/s/article/learner-000001684

Screenshot target: `https://www.coursera.org/career-academy` — look for “salary”

### Row 33 — Career Academy (sponsored catalog)

**Status:** VERIFIED (confidence: high)

Official FAQ: "Career Academy is for learners who are part of a learning program that is sponsored by your company or institution", granting entry-level Professional Certificates; numerous sponsor pages (Chico State, UTRGV, SJSU, LSU, UTEP) confirm free access is gated to sponsored populations — confirms the sheet's "not available to direct consumers" flag.

Sources:
- https://www.coursera.support/s/article/learner-000001684
- https://link.utrgv.edu/career-academy/
- https://www.csuchico.edu/alumni/coursera-career-academy/index.shtml

Screenshot target: `https://www.coursera.support/s/article/learner-000001684` — look for “sponsored”

### Row 34 — Career resource hub & aptitude test

**Status:** VERIFIED (confidence: high)

coursera.org/resources ("Career Resource Hub: Free Tools to Shape Your Career") and the free career quiz at coursera.org/resources/career-quiz (aptitude test across six professional domains) are both live and public.

Sources:
- https://www.coursera.org/resources
- https://www.coursera.org/resources/career-quiz

Screenshot target: `https://www.coursera.org/resources/career-quiz` — look for “career”

### Row 35 — Third-party cert alignment & exam discounts

**Status:** VERIFIED (confidence: medium)

Google IT Support ↔ CompTIA A+ alignment with 30% exam discount confirmed (Coursera blog, grow.google, live support threads; discounted price $177.10 matches the sheet). Caveat: sources differ on the base price ($253 vs sheet's $274 from the 8/3/26 article — CompTIA raised prices). The Microsoft 50%-off voucher sub-claim was not directly confirmed this run.

*Caveat:* Microsoft 50% voucher: verify against the msfthub page cited in the sheet.

Sources:
- https://blog.coursera.org/get-ready-to-launch-a-career-in-it-support-with-google-and-comptia
- https://grow.google/certificates/it-support/
- https://www.coursera.org/professional-certificates/google-it-support

Screenshot target: `https://www.coursera.org/professional-certificates/google-it-support` — look for “CompTIA”

### Row 36 — Partner-funded scholarships

**Status:** VERIFIED (confidence: high)

Universal Access to Microsoft Skills Scholarship with Women in Cloud confirmed: 5,000 recipients, all Microsoft Specializations & Professional Certificates ($6,000 stated value), complimentary Microsoft certification exam voucher on completing a full Professional Certificate (businesswire, Coursera blog, Women in Cloud application portal). Caveat: application portal is labeled 2024–25; whether applications remain open in Aug 2026 unconfirmed.

*Caveat:* Confirm the application window is still open before citing "applications open".

Sources:
- https://www.businesswire.com/news/home/20240520977028/en/
- https://blog.coursera.org/announcing-four-new-entry-level-certificates-and-universal-skills-scholarship-program-from-microsoft-to-help-learners-land-in-demand-jobs
- https://skills.womenincloud.com/apply/2024-25-global-microsoft-scholarship

Screenshot target: `https://blog.coursera.org/announcing-four-new-entry-level-certificates-and-universal-skills-scholarship-program-from-microsoft-to-help-learners-land-in-demand-jobs` — look for “scholarship”

### Row 37 — Learner community (standalone)

**Status:** VERIFIED (confidence: high)

Platform-wide Coursera Community (launched late 2018) exists separately from per-course forums, with subject boards and Common Rooms; official community pages live on coursera.support.

Sources:
- https://www.coursera.support/s/community
- https://www.classcentral.com/report/coursera-community/
- https://blog.coursera.org/join-courseras-new-community

Screenshot target: `https://www.coursera.support/s/community` — look for “Community”

### Row 38 — Accessibility statement

**Status:** VERIFIED (confidence: high)

Official "Coursera's accessibility policy" help article: commitment to access for learners with disabilities, WCAG 2.2 AA target, captioning on all lecture videos, accessibility email alias, plus a separate accommodations-request article.

Sources:
- https://www.coursera.support/s/article/learner-000001351
- https://www.coursera.support/s/article/learner-000001416

Screenshot target: `https://www.coursera.support/s/article/learner-000001351` — look for “accessibility”

### Row 39 — Coursera Podcast

**Status:** VERIFIED (confidence: high)

"The Coursera Podcast" is live on Spotify and Apple Podcasts with recent episodes (guests incl. Moderna's Chief Learning Officer, Class Central's CEO, Dr. Barbara Oakley).

Sources:
- https://podcasts.apple.com/us/podcast/the-coursera-podcast/id1708599019
- https://creators.spotify.com/pod/profile/the-coursera-podcast/episodes/Learning-About-Learning-with-Barbara-Oakley-e2adfbs

Screenshot target: `https://podcasts.apple.com/us/podcast/the-coursera-podcast/id1708599019` — look for “The Coursera Podcast”

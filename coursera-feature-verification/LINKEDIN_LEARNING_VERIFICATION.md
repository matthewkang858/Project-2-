# LinkedIn Learning Feature Verification — "Features v2" tab

Source workbook: `COUR4_Competitive_Research_v3_4.xlsx`, sheet **Features v2**, LinkedIn Learning section (rows 71–101, 31 features).
Verification date: **2026-08-14**. Method: live web-search evidence — LinkedIn help center (linkedin.com/help), learning.linkedin.com product pages, LinkedIn official blogs, partner announcements, and reputable press.

**Result: 29/31 VERIFIED, 2/31 PARTIALLY VERIFIED.** No feature was found to be retired or fabricated.

Screenshots: same constraint as the other platforms — run the capture script from a machine with normal internet access. Note that several LinkedIn URLs (help pages, learning catalog) may require being logged in; the capture log will flag those.

```bash
node capture_screenshots.mjs linkedin_learning_screenshot_manifest.json screenshots-linkedin/
```

## Verification matrix

| Row | Feature | Status | Confidence | Evidence (summary) | Proof URL for screenshot |
|---|---|---|---|---|---|
| 71 | AI coaching — conversational career & management advice | VERIFIED | high | Official LinkedIn Learning page "Introducing LinkedIn Learning's AI-Powered Coaching": conversational chatbot giving personalized real-time advice and content recommendations based on job title, career goals and follo... | https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching |
| 72 | AI coaching — in-course Q&A | VERIFIED | high | Learners "pose clarifying questions directly within the course, receiving real-time insights and takeaways on the course pages" (official coaching page and university deployment guides). | https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching |
| 73 | AI coaching — content summaries | VERIFIED | high | "Learners can ask for content summaries" inside courses — documented on the official AI-powered coaching page and university library guides for the feature. | https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching |
| 74 | AI coaching — practice scenarios with AI feedback | VERIFIED | high | Interactive practice/role-play with AI-powered coaching: speak or type with a customizable AI personality that responds dynamically; after each session learners receive feedback grounded in the transcript plus tailore... | https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching |
| 75 | Personalized recommendations (Skills Graph) | VERIFIED | high | LinkedIn Engineering blog documents the Skills Graph (39,000-skill taxonomy on the Economic Graph) powering personalization; recommendations driven by profile data, stated goals, followed skills and behavior, with que... | https://www.linkedin.com/learning/ |
| 76 | Full course library (25,000+ courses) | VERIFIED | high | Official linkedin.com/learning states 26,100+ courses and Learning Paths with dozens added weekly — consistent with (slightly above) the sheet's 25,000+ figure. Free LinkedIn gets only limited/promotional access; the ... | https://www.linkedin.com/learning/ |
| 77 | Learning paths & role-based content | VERIFIED | high | Learning Paths (curated course sequences) are a core catalog object (linkedin.com/learning/paths); Role Guides cover 35+ roles with 1,300+ hand-curated pathways mapping content to job roles. | https://www.linkedin.com/learning/paths |
| 78 | Localized course libraries | PARTIALLY VERIFIED | medium | Localized libraries are real — 90%+ original native-speaker courses with localized UI — but LinkedIn's own help doc lists 13 course languages (English, German, Spanish, French, Brazilian Portuguese, Japanese, Mandarin... | https://www.linkedin.com/help/learning/answer/a702837/supported-languages-for-linkedin-learning-course-videos |
| 79 | Certificates of completion (profile-integrated) | VERIFIED | high | Official help: completed courses/paths add a Certificate of Completion and associated skills directly to the LinkedIn profile from Learning History ("Add to profile"), with optional network sharing — the deep profile ... | https://www.linkedin.com/help/linkedin/answer/a704787/add-learning-certificates-of-completion-and-skills-to-your-linkedin-profile |
| 80 | CEU/CPE credits (select courses) | VERIFIED | high | Official continuing-education program: NASBA-registered CPE sponsor, PMI Authorized Training Partner (600+ courses, 650+ PDUs), SHRM-recognized PDC provider (60 activities); dedicated CEU topic page and partner direct... | https://learning.linkedin.com/certifications-and-credentials |
| 81 | Exercise files | VERIFIED | high | Official help: downloadable exercise files (project files/documents) under the course Overview tab, on desktop and mobile app; included at author discretion, so not on every course. | https://www.linkedin.com/help/learning/answer/a702845/downloading-linkedin-learning-exercise-files |
| 82 | Chapter quizzes | VERIFIED | high | Official help and course tutorials: optional multiple-choice chapter quizzes ("Chapter Quiz" section) with unlimited retakes and wrong-answer pointers back to the relevant video; not present in all courses. | https://www.linkedin.com/help/learning/answer/a702857 |
| 83 | In-course Q&A & community | VERIFIED | high | Official Q&A FAQ: real-time, timestamped course Q&A tab with @-tagging of instructors/connections, answered by instructors or fellow learners; separate Learning Groups continue discussion beyond the course. | https://www.linkedin.com/help/learning/answer/a703896 |
| 84 | AI profile writing assistant | VERIFIED | high | Official help "Enhance your profile with LinkedIn's AI-powered writing assistant": personalized Headline/About suggestions for Premium subscribers. Caveat: currently limited to a select group of Premium subscribers in... | https://www.linkedin.com/help/linkedin/answer/a1444194 |
| 85 | AI interview prep with feedback | VERIFIED | high | Official help "Get instant AI feedback to improve your interview answers": record video/written practice answers and get AI feedback on pace, filler words, sensitive phrases and answer tips; expert sample answers for ... | https://www.linkedin.com/help/linkedin/answer/a549539 |
| 86 | Jobseeker Coach (conversational) | VERIFIED | high | GPT-4-powered conversational job-search coach for Premium: chat about open roles, fit vs. your profile, skills to close gaps, and company background (launched Nov 2023 with LinkedIn's 1B-member announcement; expanded ... | https://premium.linkedin.com/careers/career |
| 87 | AI job-match insights | VERIFIED | high | Job Match (launched early 2025): LLM-based match score on every job listing with qualification breakdown; Premium adds High/Medium/Low ratings, applicant comparison, and "Top Applicant" placement — the AI fit-read the... | https://premium.linkedin.com/careers/career |
| 88 | Offline viewing (mobile) | VERIFIED | high | Official help: download courses/videos in the mobile app for offline viewing (app-only, active subscription required; 30-day re-authentication window). | https://www.linkedin.com/help/learning/answer/a703775/downloading-and-viewing-learning-videos-offline |
| 89 | Audio-only mode | VERIFIED | high | Audio-only toggle in the mobile app plus a dedicated audio course format (Type > Audio filter), including book summaries and podcast-style content — podcast-style playback as the sheet describes. | https://www.linkedin.com/learning/ |
| 90 | LinkedIn Skill Assessments & verified skill badges | VERIFIED | high | Official help page live; timed multiple-choice tests tied to profile Skills; pass (top 30% threshold) earns a verified badge, private by default, free of charge; 2026 guides confirm the program is active with new asse... | https://www.linkedin.com/help/linkedin/answer/a507663 |
| 91 | Professional Certificates | VERIFIED | high | Official Professional Certificates program with partner-built credentials (Microsoft, Zendesk, Twilio and more): courses + assessment, shareable credential; dedicated catalog topic page and help FAQ — matches the shee... | https://www.linkedin.com/learning/topics/professional-certificates |
| 92 | Certification prep (120+ external credentials) | VERIFIED | high | Official Certifications & Credentials program: 2,000+ courses preparing learners for 120+ off-platform exams across four credential types (500+ dedicated cert-prep courses), with a public partner directory — matches t... | https://learning.linkedin.com/certifications-and-credentials |
| 93 | Code Challenges (CoderPad) | VERIFIED | high | CoderPad partnership live since fall 2023: 30+ interactive code-challenge courses (Python, Java, SQL, JavaScript, C#, Go) with in-browser execution, auto-feedback and hints; official topic page and learner/admin FAQs. | https://www.linkedin.com/learning/topics/hands-on-practice-with-code-challenges |
| 94 | GitHub Codespaces & GitHub Models integration | PARTIALLY VERIFIED | medium | GitHub Codespaces integration fully confirmed: 50+ courses with real dev environments across 3 practice tiers (Hands-On Introduction, Practice It, Level Up), official topic page + admin FAQ. The "GitHub Models" half o... | https://www.linkedin.com/learning/topics/hands-on-practice-with-github-codespaces |
| 95 | Cybersecurity Training Labs (Hack the Box) | VERIFIED | high | Announced Nov 2025: Hack The Box is LinkedIn Learning's first cybersecurity training-labs partner; curated threat-informed HTB Academy labs embedded directly in LinkedIn Learning with no extra logins or software. | https://www.hackthebox.com/blog/hack-the-box-linkedin-learning-cybersecurity-labs |
| 96 | AI role-play scenarios | VERIFIED | high | AI Role Play confirmed on consumer Premium (official coaching page) and widely deployed via universities/enterprise: 9 workplace scenarios, customizable AI persona (tone/attitude/difficulty), voice or text, private tr... | https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching |
| 97 | Authors' Office Hours (live) | VERIFIED | high | Official LinkedIn blog + Learning help FAQ: Office Hours are live instructor-hosted events with real-time Q&A, comments and reactions, plus on-demand replays of past events. | https://www.linkedin.com/help/learning/answer/a707102 |
| 98 | Learning path completion badges | VERIFIED | medium | A badge is awarded on completing a learning path, but LinkedIn's help notes the badge itself cannot be shared — the shareable artifact is the path's Certificate of Completion (downloadable, addable to profile). The sh... | https://www.linkedin.com/help/learning/answer/a700836 |
| 99 | Multi-format content (text, audio, nano) | VERIFIED | medium | Confirmed formats beyond video: 450+ Nano Tips micro-videos, audio-only courses (Type > Audio filter), and text-based learning alongside long-form video, per LinkedIn Learning catalog and product-overview materials. | https://www.linkedin.com/learning/ |
| 100 | Free access via public libraries | VERIFIED | high | Hundreds of US library systems (NYPL, LAPL, Cleveland, Las Vegas-Clark County, etc.) offer full LinkedIn Learning access with a library card number + PIN, no LinkedIn account required; LinkedIn maintains an official "... | https://www.linkedin.com/help/learning/answer/a705966 |
| 101 | Notes, playlists & interactive transcripts | VERIFIED | high | Notebook tab with video-timestamped notes exportable as .txt; Saved courses and Collections; interactive transcripts beside the player with clickable sentences that jump the video, plus transcript keyword search. | https://www.linkedin.com/learning/ |

## Findings that need attention

1. **Row 78 — Localized course libraries (PARTIALLY VERIFIED).** The sheet says "20+ languages"; LinkedIn's own help doc lists **13** course video/audio languages. Machine-translated *subtitles* cover more languages and may be where 20+ came from — recheck which number the sheet intends.
2. **Row 94 — GitHub Codespaces & GitHub Models (PARTIALLY VERIFIED).** Codespaces integration (50+ courses) is solid and official; no evidence found for the "GitHub Models" half of the claim — verify it on the live catalog or drop it from the sheet.
3. **Row 76 — Library size.** Official count is now "26,100+ courses and Learning Paths" — above the sheet's 25,000+; also note the official number mixes courses and paths.
4. **Row 84 — AI profile writing assistant.** Real, but rollout-gated: "select group" of Premium subscribers, Headline/About sections only, 5 languages — worth a caveat next to the ✓.
5. **Row 98 — Path completion badges.** The badge exists but cannot be shared; the shareable artifact is the path's Certificate of Completion.
6. **Row 96 — AI role-play.** The sheet's "verify consumer availability" note is resolved: LinkedIn's own AI-coaching page lists role play as a Premium subscriber feature.

## Per-feature evidence and sources

### Row 71 — AI coaching — conversational career & management advice

**Status:** VERIFIED (confidence: high)

Official LinkedIn Learning page "Introducing LinkedIn Learning's AI-Powered Coaching": conversational chatbot giving personalized real-time advice and content recommendations based on job title, career goals and followed skills; available to all Premium subscribers in English. 76% of learners report it helped build marketable skills.

Sources:
- https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching
- https://www.fastcompany.com/91140100/linkedin-learning-adds-more-ai-powered-coaching-features
- https://www.forbes.com/sites/ruthgotian/2024/06/16/linkedin-and-ai-powered-coaching/

Screenshot target: `https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching` — look for “AI-powered coaching”

### Row 72 — AI coaching — in-course Q&A

**Status:** VERIFIED (confidence: high)

Learners "pose clarifying questions directly within the course, receiving real-time insights and takeaways on the course pages" (official coaching page and university deployment guides).

Sources:
- https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching
- https://ai.uc.edu/ai-tools/linkedin-learning-ai-powered-tools

Screenshot target: `https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching` — look for “clarifying questions”

### Row 73 — AI coaching — content summaries

**Status:** VERIFIED (confidence: high)

"Learners can ask for content summaries" inside courses — documented on the official AI-powered coaching page and university library guides for the feature.

Sources:
- https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching
- https://guides.library.uq.edu.au/tools-and-techniques/linkedin-learning/using-ai-features

Screenshot target: `https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching` — look for “summaries”

### Row 74 — AI coaching — practice scenarios with AI feedback

**Status:** VERIFIED (confidence: high)

Interactive practice/role-play with AI-powered coaching: speak or type with a customizable AI personality that responds dynamically; after each session learners receive feedback grounded in the transcript plus tailored content.

Sources:
- https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching
- https://hr.arizona.edu/news/2025/master-difficult-workplace-conversations-linkedin-learnings-ai-coaching

Screenshot target: `https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching` — look for “practice”

### Row 75 — Personalized recommendations (Skills Graph)

**Status:** VERIFIED (confidence: high)

LinkedIn Engineering blog documents the Skills Graph (39,000-skill taxonomy on the Economic Graph) powering personalization; recommendations driven by profile data, stated goals, followed skills and behavior, with questionnaire/inferred-skills cold-start handling.

Sources:
- https://engineering.linkedin.com/blog/2023/extracting-skills-from-content-to-fuel-the-linkedin-skills-graph
- https://engineering.linkedin.com/blog/2016/12/personalized-recommendations-in-linkedin-learning

Screenshot target: `https://www.linkedin.com/learning/` — look for “Recommended”

### Row 76 — Full course library (25,000+ courses)

**Status:** VERIFIED (confidence: high)

Official linkedin.com/learning states 26,100+ courses and Learning Paths with dozens added weekly — consistent with (slightly above) the sheet's 25,000+ figure. Free LinkedIn gets only limited/promotional access; the library is a Premium/Learning-subscription feature.

*Caveat:* Official count is now 26,100+ (includes Learning Paths); refresh the sheet number.

Sources:
- https://www.linkedin.com/learning/
- https://learning.linkedin.com/content-library

Screenshot target: `https://www.linkedin.com/learning/` — look for “courses”

### Row 77 — Learning paths & role-based content

**Status:** VERIFIED (confidence: high)

Learning Paths (curated course sequences) are a core catalog object (linkedin.com/learning/paths); Role Guides cover 35+ roles with 1,300+ hand-curated pathways mapping content to job roles.

Sources:
- https://www.linkedin.com/learning/paths
- https://www.cu.edu/blog/work-life/new-linkedin-learning-role-guides-lay-out-learning-paths-career-advancement

Screenshot target: `https://www.linkedin.com/learning/paths` — look for “Learning Path”

### Row 78 — Localized course libraries

**Status:** PARTIALLY VERIFIED (confidence: medium)

Localized libraries are real — 90%+ original native-speaker courses with localized UI — but LinkedIn's own help doc lists 13 course languages (English, German, Spanish, French, Brazilian Portuguese, Japanese, Mandarin, Dutch, Italian, Turkish, Polish, Korean, Bahasa Indonesia), not the sheet's "20+". Machine-translated subtitles extend beyond 13, which may be the source of the higher count.

*Caveat:* Sheet says 20+ languages; official course-language list is 13. Recheck what the 20+ referred to (likely subtitle languages).

Sources:
- https://www.linkedin.com/help/learning/answer/a702837/supported-languages-for-linkedin-learning-course-videos
- https://www.linkedin.com/business/learning/blog/new-courses/linkedin-learnings-newest-addition-4-000-new-courses-across-4-l

Screenshot target: `https://www.linkedin.com/help/learning/answer/a702837/supported-languages-for-linkedin-learning-course-videos` — look for “languages”

### Row 79 — Certificates of completion (profile-integrated)

**Status:** VERIFIED (confidence: high)

Official help: completed courses/paths add a Certificate of Completion and associated skills directly to the LinkedIn profile from Learning History ("Add to profile"), with optional network sharing — the deep profile integration the sheet highlights.

Sources:
- https://www.linkedin.com/help/linkedin/answer/a704787/add-learning-certificates-of-completion-and-skills-to-your-linkedin-profile
- https://www.linkedin.com/help/learning/answer/a700836

Screenshot target: `https://www.linkedin.com/help/linkedin/answer/a704787/add-learning-certificates-of-completion-and-skills-to-your-linkedin-profile` — look for “Add to profile”

### Row 80 — CEU/CPE credits (select courses)

**Status:** VERIFIED (confidence: high)

Official continuing-education program: NASBA-registered CPE sponsor, PMI Authorized Training Partner (600+ courses, 650+ PDUs), SHRM-recognized PDC provider (60 activities); dedicated CEU topic page and partner directory.

Sources:
- https://learning.linkedin.com/certifications-and-credentials
- https://www.linkedin.com/help/learning/answer/a598950/
- https://www.linkedin.com/help/learning/answer/a706053/

Screenshot target: `https://learning.linkedin.com/certifications-and-credentials` — look for “Continuing Education”

### Row 81 — Exercise files

**Status:** VERIFIED (confidence: high)

Official help: downloadable exercise files (project files/documents) under the course Overview tab, on desktop and mobile app; included at author discretion, so not on every course.

Sources:
- https://www.linkedin.com/help/learning/answer/a702845/downloading-linkedin-learning-exercise-files
- https://www.linkedin.com/help/learning/answer/a704766/linkedin-learning-exercise-files-faq

Screenshot target: `https://www.linkedin.com/help/learning/answer/a702845/downloading-linkedin-learning-exercise-files` — look for “Exercise Files”

### Row 82 — Chapter quizzes

**Status:** VERIFIED (confidence: high)

Official help and course tutorials: optional multiple-choice chapter quizzes ("Chapter Quiz" section) with unlimited retakes and wrong-answer pointers back to the relevant video; not present in all courses.

Sources:
- https://www.linkedin.com/help/learning/answer/a702857
- https://www.linkedin.com/help/learning/answer/a701847/

Screenshot target: `https://www.linkedin.com/help/learning/answer/a702857` — look for “quiz”

### Row 83 — In-course Q&A & community

**Status:** VERIFIED (confidence: high)

Official Q&A FAQ: real-time, timestamped course Q&A tab with @-tagging of instructors/connections, answered by instructors or fellow learners; separate Learning Groups continue discussion beyond the course.

Sources:
- https://www.linkedin.com/help/learning/answer/a703896
- https://www.linkedin.com/business/learning/blog/new-courses/announcing-question-and-answer-feature-on-linkedin-learning
- https://www.linkedin.com/help/learning/answer/a700990/linkedin-learning-groups-faq

Screenshot target: `https://www.linkedin.com/help/learning/answer/a703896` — look for “Q&A”

### Row 84 — AI profile writing assistant

**Status:** VERIFIED (confidence: high)

Official help "Enhance your profile with LinkedIn's AI-powered writing assistant": personalized Headline/About suggestions for Premium subscribers. Caveat: currently limited to a select group of Premium subscribers in 5 languages.

*Caveat:* Rollout-gated: "select group" of Premium subscribers; Headline and About sections only.

Sources:
- https://www.linkedin.com/help/linkedin/answer/a1444194
- https://www.linkedin.com/help/linkedin/answer/a7146413

Screenshot target: `https://www.linkedin.com/help/linkedin/answer/a1444194` — look for “writing assistant”

### Row 85 — AI interview prep with feedback

**Status:** VERIFIED (confidence: high)

Official help "Get instant AI feedback to improve your interview answers": record video/written practice answers and get AI feedback on pace, filler words, sensitive phrases and answer tips; expert sample answers for Premium members; private unless shared.

Sources:
- https://www.linkedin.com/help/linkedin/answer/a549539
- https://www.makeuseof.com/use-linkedin-interview-prep/

Screenshot target: `https://www.linkedin.com/help/linkedin/answer/a549539` — look for “interview”

### Row 86 — Jobseeker Coach (conversational)

**Status:** VERIFIED (confidence: high)

GPT-4-powered conversational job-search coach for Premium: chat about open roles, fit vs. your profile, skills to close gaps, and company background (launched Nov 2023 with LinkedIn's 1B-member announcement; expanded with AI job search tools in 2025).

Sources:
- https://www.cnbc.com/2023/11/01/linkedins-new-ai-chatbot-wants-to-help-you-get-a-job-.html
- https://premium.linkedin.com/careers/career
- https://www.forbes.com/sites/torconstantino/2025/06/02/linkedin-launches-ai-job-search-tool-for-premium-users/

Screenshot target: `https://premium.linkedin.com/careers/career` — look for “job”

### Row 87 — AI job-match insights

**Status:** VERIFIED (confidence: high)

Job Match (launched early 2025): LLM-based match score on every job listing with qualification breakdown; Premium adds High/Medium/Low ratings, applicant comparison, and "Top Applicant" placement — the AI fit-read the sheet describes.

Sources:
- https://premium.linkedin.com/careers/career
- https://blog.theinterviewguys.com/linkedins-new-ai-job-match-tool/

Screenshot target: `https://premium.linkedin.com/careers/career` — look for “Job Match”

### Row 88 — Offline viewing (mobile)

**Status:** VERIFIED (confidence: high)

Official help: download courses/videos in the mobile app for offline viewing (app-only, active subscription required; 30-day re-authentication window).

Sources:
- https://www.linkedin.com/help/learning/answer/a703775/downloading-and-viewing-learning-videos-offline

Screenshot target: `https://www.linkedin.com/help/learning/answer/a703775/downloading-and-viewing-learning-videos-offline` — look for “offline”

### Row 89 — Audio-only mode

**Status:** VERIFIED (confidence: high)

Audio-only toggle in the mobile app plus a dedicated audio course format (Type > Audio filter), including book summaries and podcast-style content — podcast-style playback as the sheet describes.

Sources:
- https://blog.smu.edu/itconnect/2026/01/22/commute-linkedin-learning-audio-only-courses/
- https://link.ucop.edu/2021/07/13/tune-in-to-professional-development-audio-content-from-linkedin-learning/

Screenshot target: `https://www.linkedin.com/learning/` — look for “Audio”

### Row 90 — LinkedIn Skill Assessments & verified skill badges

**Status:** VERIFIED (confidence: high)

Official help page live; timed multiple-choice tests tied to profile Skills; pass (top 30% threshold) earns a verified badge, private by default, free of charge; 2026 guides confirm the program is active with new assessment categories added.

Sources:
- https://www.linkedin.com/help/linkedin/answer/a507663
- https://jobright.ai/blog/linkedin-learning-certifications-guide/

Screenshot target: `https://www.linkedin.com/help/linkedin/answer/a507663` — look for “Skill Assessment”

### Row 91 — Professional Certificates

**Status:** VERIFIED (confidence: high)

Official Professional Certificates program with partner-built credentials (Microsoft, Zendesk, Twilio and more): courses + assessment, shareable credential; dedicated catalog topic page and help FAQ — matches the sheet's partner list.

Sources:
- https://www.linkedin.com/learning/topics/professional-certificates
- https://www.linkedin.com/help/learning/answer/a1433885
- https://www.zendesk.com/newsroom/articles/zendesk-and-linkedin-learning/

Screenshot target: `https://www.linkedin.com/learning/topics/professional-certificates` — look for “Professional Certificate”

### Row 92 — Certification prep (120+ external credentials)

**Status:** VERIFIED (confidence: high)

Official Certifications & Credentials program: 2,000+ courses preparing learners for 120+ off-platform exams across four credential types (500+ dedicated cert-prep courses), with a public partner directory — matches the sheet's figures.

Sources:
- https://learning.linkedin.com/certifications-and-credentials
- https://business.linkedin.com/learn/certifications-and-credentials

Screenshot target: `https://learning.linkedin.com/certifications-and-credentials` — look for “120”

### Row 93 — Code Challenges (CoderPad)

**Status:** VERIFIED (confidence: high)

CoderPad partnership live since fall 2023: 30+ interactive code-challenge courses (Python, Java, SQL, JavaScript, C#, Go) with in-browser execution, auto-feedback and hints; official topic page and learner/admin FAQs.

Sources:
- https://www.linkedin.com/learning/topics/hands-on-practice-with-code-challenges
- https://www.linkedin.com/help/learning/answer/a1649756
- https://coderpad.io/blog/announcements/coderpad-partners-with-linkedin-learning-to-offer-learners-interactive-hands-on-coding-practice/

Screenshot target: `https://www.linkedin.com/learning/topics/hands-on-practice-with-code-challenges` — look for “Code Challenge”

### Row 94 — GitHub Codespaces & GitHub Models integration

**Status:** PARTIALLY VERIFIED (confidence: medium)

GitHub Codespaces integration fully confirmed: 50+ courses with real dev environments across 3 practice tiers (Hands-On Introduction, Practice It, Level Up), official topic page + admin FAQ. The "GitHub Models" half of the claim was NOT independently confirmed in this run — no official page found tying GitHub Models to LinkedIn Learning courses.

*Caveat:* Verify the GitHub Models sub-claim on the live catalog; Codespaces alone is solid.

Sources:
- https://www.linkedin.com/learning/topics/hands-on-practice-with-github-codespaces
- https://www.linkedin.com/help/learning/answer/a1351348
- https://www.linkedin.com/business/learning/blog/productivity-tips/introducing-new-ways-you-can-accelerate-your-career-in-tech-with-linkedin-learning-and-github-codespaces

Screenshot target: `https://www.linkedin.com/learning/topics/hands-on-practice-with-github-codespaces` — look for “GitHub Codespaces”

### Row 95 — Cybersecurity Training Labs (Hack the Box)

**Status:** VERIFIED (confidence: high)

Announced Nov 2025: Hack The Box is LinkedIn Learning's first cybersecurity training-labs partner; curated threat-informed HTB Academy labs embedded directly in LinkedIn Learning with no extra logins or software.

Sources:
- https://www.businesswire.com/news/home/20251105904582/en/Hack-The-Box-Powers-First-Cybersecurity-Training-Labs-in-LinkedIn-Learning-to-Close-Workforce-Readiness-Gap
- https://www.hackthebox.com/blog/hack-the-box-linkedin-learning-cybersecurity-labs

Screenshot target: `https://www.hackthebox.com/blog/hack-the-box-linkedin-learning-cybersecurity-labs` — look for “LinkedIn Learning”

### Row 96 — AI role-play scenarios

**Status:** VERIFIED (confidence: high)

AI Role Play confirmed on consumer Premium (official coaching page) and widely deployed via universities/enterprise: 9 workplace scenarios, customizable AI persona (tone/attitude/difficulty), voice or text, private transcripts, post-session feedback.

*Caveat:* Sheet's "verify consumer availability" note: resolved — Premium subscribers get it per LinkedIn's own coaching page.

Sources:
- https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching
- https://link.ucop.edu/2025/04/22/practice-tough-conversations-with-ai-powered-role-play/
- https://learn.microsoft.com/en-us/viva/learning/learning-agent-roleplay-linkedin

Screenshot target: `https://learning.linkedin.com/resources/learner-engagement/linkedin-learning-ai-powered-coaching` — look for “role play”

### Row 97 — Authors' Office Hours (live)

**Status:** VERIFIED (confidence: high)

Official LinkedIn blog + Learning help FAQ: Office Hours are live instructor-hosted events with real-time Q&A, comments and reactions, plus on-demand replays of past events.

Sources:
- https://blog.linkedin.com/2021/september/1/learn-from-experts-in-real-time-with-office-hours
- https://www.linkedin.com/help/learning/answer/a707102

Screenshot target: `https://www.linkedin.com/help/learning/answer/a707102` — look for “Office Hours”

### Row 98 — Learning path completion badges

**Status:** VERIFIED (confidence: medium)

A badge is awarded on completing a learning path, but LinkedIn's help notes the badge itself cannot be shared — the shareable artifact is the path's Certificate of Completion (downloadable, addable to profile). The sheet's claim is accurate as stated; add the non-shareable caveat.

*Caveat:* Badge is not shareable; certificates are.

Sources:
- https://www.linkedin.com/help/learning/answer/a700836
- https://www.linkedin.com/help/linkedin/answer/a704787/add-learning-certificates-of-completion-and-skills-to-your-linkedin-profile

Screenshot target: `https://www.linkedin.com/help/learning/answer/a700836` — look for “learning path”

### Row 99 — Multi-format content (text, audio, nano)

**Status:** VERIFIED (confidence: medium)

Confirmed formats beyond video: 450+ Nano Tips micro-videos, audio-only courses (Type > Audio filter), and text-based learning alongside long-form video, per LinkedIn Learning catalog and product-overview materials.

Sources:
- https://www.linkedin.com/learning/
- https://business.linkedin.com/learn/content-library

Screenshot target: `https://www.linkedin.com/learning/` — look for “Nano”

### Row 100 — Free access via public libraries

**Status:** VERIFIED (confidence: high)

Hundreds of US library systems (NYPL, LAPL, Cleveland, Las Vegas-Clark County, etc.) offer full LinkedIn Learning access with a library card number + PIN, no LinkedIn account required; LinkedIn maintains an official "Learning for Library patrons" help page.

Sources:
- https://www.linkedin.com/help/learning/answer/a705966
- https://www.nypl.org/collections/articles-databases/lyndacom
- https://www.lapl.org/linkedin-learning

Screenshot target: `https://www.linkedin.com/help/learning/answer/a705966` — look for “library”

### Row 101 — Notes, playlists & interactive transcripts

**Status:** VERIFIED (confidence: high)

Notebook tab with video-timestamped notes exportable as .txt; Saved courses and Collections; interactive transcripts beside the player with clickable sentences that jump the video, plus transcript keyword search.

Sources:
- https://www.linkedin.com/learning/how-to-use-linkedin-learning/taking-notes-14577532
- https://libguides.mcmaster.ca/linkedinlearning/features

Screenshot target: `https://www.linkedin.com/learning/` — look for “Transcript”

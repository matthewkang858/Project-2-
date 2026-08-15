# Udemy Feature Verification — "Features v2" tab

Source workbook: `COUR4_Competitive_Research_v3_4.xlsx`, sheet **Features v2**, Udemy section (rows 43–67, 25 features).
Verification date: **2026-08-14**. Method: live web-search evidence — nearly every feature is documented by an official Udemy source (support.udemy.com, business-support.udemy.com, udemy.com product pages, about.udemy.com, teach.udemy.com).

**Result: 24/25 VERIFIED, 1/25 PARTIALLY VERIFIED.** No feature was found to be retired or fabricated.

Screenshots: same situation as the Coursera report — this session's network egress policy blocks udemy.com, so run `capture_screenshots.mjs` with `udemy_screenshot_manifest.json` from a machine with normal internet access:

```bash
node capture_screenshots.mjs udemy_screenshot_manifest.json screenshots-udemy/
```

## Verification matrix

| Row | Feature | Status | Confidence | Evidence (summary) | Proof URL for screenshot |
|---|---|---|---|---|---|
| 43 | Udemy AI Assistant — content discovery chat | VERIFIED | high | Official support FAQ and Personal Plan page: the AI Assistant "personalizes and streamlines the learning process by recommending course content through guided conversations", included with Personal Plan (and Business ... | https://www.udemy.com/personal-plan/ |
| 44 | Udemy AI Assistant — in-course Q&A | VERIFIED | high | Official docs: in-course support with real-time answers to course-related questions, concept explanations, summaries, practice scenarios and code examples, grounded in the course. | https://support.udemy.com/hc/en-us/articles/27554582323863-Udemy-AI-Assistant-Frequently-Asked-Questions |
| 45 | AI Role Play | VERIFIED | high | Official "How to use the Role Play feature" articles (consumer + Business): conversational practice with an AI character against meeting goals, ending with a strengths/improvements report; flagged on course landing pa... | https://support.udemy.com/hc/en-us/articles/31522529224343-How-to-use-the-Role-Play-feature |
| 46 | Personalized recommendations | VERIFIED | high | Official "Personalize Your Learning Experience" article: occupation-and-interests onboarding drives role/interest-based course recommendations on the home page; algorithm adapts to engagement behavior. | https://support.udemy.com/hc/en-us/articles/17015232224023-Personalize-Your-Learning-Experience-on-Udemy |
| 47 | Career Accelerators | VERIFIED | high | about.udemy.com launch post ("Reimagine your career with Career Accelerators", launched with 6 programs) and live program pages (Full-Stack Web Developer, Software Engineer, Game Developer at udemy.com/career/...); co... | https://www.udemy.com/career/full-stack-web-developer/ |
| 48 | Labs | VERIFIED | high | Official Personal Plan docs: in-course labs are guided hands-on tasks in secure pre-configured environments with a companion workspace, available to eligible subscriptions (Personal Plan) — confirming the subscription... | https://support.udemy.com/hc/en-us/articles/36212876902679-In-course-labs |
| 49 | Coding exercises | VERIFIED | high | Official "Learning With Coding Exercises" article: interactive in-browser coding practice inside programming courses; many languages (C++, C#, Java, Python, Ruby, Swift, PHP, React 18) with a "Run code" button in Python. | https://support.udemy.com/hc/en-us/articles/229606768-Learning-With-Coding-Exercises |
| 50 | Quizzes (in-course) | VERIFIED | high | Official instructor docs: multiple-choice/multiple-selection/fill-in-the-blank quizzes instructors build per course for self-assessment — course-dependent, as the sheet says. | https://support.udemy.com/hc/en-us/articles/229231627-Create-a-Multiple-Choice-Quiz |
| 51 | Assignments (in-course) | VERIFIED | high | Official docs: instructor-built assignments with text/video instructions, downloadable resources, draft saving, instructor feedback and peer comparison — course-dependent. | https://support.udemy.com/hc/en-us/articles/115000340668-Assignments-Apply-Your-Knowledge-and-Improve-the-Skills-You-ve-Learned-With-Udemy |
| 52 | Certification exam practice tests | VERIFIED | high | Official docs: practice tests mirror certification exams with untimed Practice mode and timed Exam mode; sold as standalone practice-test courses (AWS, Azure, CompTIA pages live) and included in Personal Plan — matchi... | https://www.udemy.com/browse/certification/ |
| 53 | Certificate of completion | VERIFIED | high | Official FAQ: completion certificate on finished paid courses (PDF/JPG download); free courses and practice-test-only courses get no certificate (except pre-March-2020 free enrollments) — exactly matches the sheet's "... | https://support.udemy.com/hc/en-us/articles/14291607637015-Certificates-of-Completion-Frequently-Asked-Questions |
| 54 | Course Q&A board | VERIFIED | high | Official docs: per-course Q&A below the player with instructor/TA answers, Featured Questions, upvote-based prioritization; free-course changes (2020) limited Q&A on free tier — matches "Limited" tiering. | https://support.udemy.com/hc/en-us/articles/229233387-How-to-Ask-a-Question-About-a-Course-You-re-Taking |
| 55 | Direct instructor messaging | VERIFIED | high | Official docs: only enrolled students on paid courses can DM the instructor (if the instructor has messaging enabled); not available on free courses or in the mobile app — matches sheet tiering. | https://support.udemy.com/hc/en-us/articles/229232987-Direct-Messages-Rules-and-Guidelines |
| 56 | Closed captions & auto-subtitles | VERIFIED | high | Official docs: CC icon in the player with caption settings; auto-generated subtitles (speech recognition) in English, Spanish, Portuguese, marked "auto-generated"; instructors can upload/edit .vtt captions. | https://support.udemy.com/hc/en-us/articles/229605028-How-to-Use-Subtitles-Transcripts-on-a-Browser |
| 57 | Searchable transcripts | VERIFIED | high | Official docs: Transcripts button at the bottom of the player opens the full text in a side panel with highlighted, auto-scrolling current sentence, easing navigation to relevant content; language follows the selected... | https://support.udemy.com/hc/en-us/articles/229605028-How-to-Use-Subtitles-Transcripts-on-a-Browser |
| 58 | Lifetime access | VERIFIED | high | Official "Lifetime access" article: purchased courses stay accessible for life while the account is in good standing and Udemy retains the course license (rare removals for policy/legal/instructor reasons); Personal P... | https://support.udemy.com/hc/en-us/articles/229603708-Lifetime-access |
| 59 | Offline viewing (mobile) | VERIFIED | high | Official iOS and Android articles: download entire courses, sections, or lectures in the app; downloads are encrypted, app-only, and refresh after ~30 days online; practice tests and some resources excluded. | https://support.udemy.com/hc/en-us/articles/229603928-Downloading-Courses-for-Offline-Viewing-on-The-iOS-App |
| 60 | Downloadable instructor resources | VERIFIED | high | Official docs: lectures with resources show a folder icon in the player; instructors attach any filetype (PDF, ZIP, XLS, source code, templates) up to 1 GB per file. | https://support.udemy.com/hc/en-us/articles/229604708-How-to-access-course-resources-on-a-browser |
| 61 | Marketplace catalog & UGC supply model | VERIFIED | high | Official Personal Plan FAQ: "The 26,000 courses included in Personal Plan are curated by Udemy's content experts from our catalog of 250,000 courses" — matches the sheet's 250,000 marketplace / curated 26k Personal Pl... | https://www.udemy.com/personal-plan/ |
| 62 | Ratings, reviews & searchable feedback | VERIFIED | high | 5-star ratings (half-stars supported) prompted mid-course; written reviews optional and editable; review section supports keyword search ("Search reviews") and filtering by star level — including the keyword search th... | https://support.udemy.com/hc/en-us/articles/229231027-How-to-preview-and-compare-courses |
| 63 | Instructor profiles & direct contact | VERIFIED | high | Official docs: instructor bio section on every course landing page; clicking the name opens a profile page with their other courses, aggregate ratings, and (if enabled) a Send message option; Instructor Partner badge ... | https://support.udemy.com/hc/en-us/articles/229231027-How-to-Preview-And-Compare-Courses |
| 64 | Learning reminders | VERIFIED | high | Official articles for browser and mobile app: schedule once/daily/weekly reminders with time-of-day, push/email delivery, and Google/Apple/Outlook calendar export; reminders manageable on the Learning tools page. | https://support.udemy.com/hc/en-us/articles/4501093209367-How-to-Schedule-Learning-Reminders-on-a-Browser |
| 65 | Course gifting | VERIFIED | high | Official "How to send a Udemy gift" + gifting FAQ: "Gift this course" flow with recipient email, send date and message. Caveats match the sheet: subscriptions (Personal Plan) cannot be gifted; gifting unavailable in t... | https://support.udemy.com/hc/en-us/articles/229231187-How-to-send-a-Udemy-gift |
| 66 | Mobile + connected-TV apps | PARTIALLY VERIFIED | medium | iOS/Android apps fully confirmed (offline downloads, course player). The connected-TV half is weaker: Udemy's own docs only document casting from the mobile app to Chromecast, Apple TV, and AirPlay-2 smart TVs; no Rok... | https://support.udemy.com/hc/en-us/articles/360005889053-How-to-Cast-Udemy-Courses-Via-Your-Mobile-Device |
| 67 | 30-day money-back guarantee | VERIFIED | high | Official refund policy: all eligible course purchases refundable within 30 days (original payment method or credits; not after completing a significant amount). Subscriptions explicitly carry no 30-day guarantee — can... | https://support.udemy.com/hc/en-us/articles/360050856093-Udemy-s-Refund-Policy |

## Findings that need attention

1. **Row 66 — Mobile + connected-TV apps (PARTIALLY VERIFIED).** Mobile apps are solid; but Udemy's own documentation only supports *casting* to TVs (Chromecast, Apple TV, AirPlay-2 smart TVs — no Roku, no dedicated Fire TV app found). Suggest rewording the sheet to "mobile apps + TV casting" rather than "connected-TV apps".
2. **Rows 43–44 — AI Assistant scope.** Confirmed in Personal Plan, but it only works in courses whose instructors opted into Udemy's GenAI program, in supported languages — worth a coverage caveat next to the ✓.
3. **Row 45 — AI Role Play.** Confirmed; note the enhanced/customizable version is an Enterprise add-on, and availability is flagged per-course ("This course includes → Role Play").
4. **Row 47 — Career Accelerators count.** Launched with 6 programs, a community post now says 13 — the number moves; re-count when screenshotting.
5. **Row 52 — Practice tests in Personal Plan.** Confirmed included, but Personal Plan's catalog is curated — a specific practice-test course may or may not be in it; the sheet's "Varies (per course)" for individual purchase is accurate.
6. **Row 53 — Certificates.** The free-course exclusion has an edge case: free enrollments made before March 17, 2020 kept certificate access.

## Per-feature evidence and sources

### Row 43 — Udemy AI Assistant — content discovery chat

**Status:** VERIFIED (confidence: high)

Official support FAQ and Personal Plan page: the AI Assistant "personalizes and streamlines the learning process by recommending course content through guided conversations", included with Personal Plan (and Business tiers).

*Caveat:* Only active in courses whose instructors joined Udemy's GenAI program.

Sources:
- https://support.udemy.com/hc/en-us/articles/27554582323863-Udemy-AI-Assistant-Frequently-Asked-Questions
- https://www.udemy.com/personal-plan/
- https://support.udemy.com/hc/en-us/articles/27554487131671-How-to-Access-and-Use-the-Udemy-AI-Assistant

Screenshot target: `https://www.udemy.com/personal-plan/` — look for “AI Assistant”

### Row 44 — Udemy AI Assistant — in-course Q&A

**Status:** VERIFIED (confidence: high)

Official docs: in-course support with real-time answers to course-related questions, concept explanations, summaries, practice scenarios and code examples, grounded in the course.

*Caveat:* Availability limited to GenAI-program courses in supported languages.

Sources:
- https://support.udemy.com/hc/en-us/articles/27554582323863-Udemy-AI-Assistant-Frequently-Asked-Questions
- https://support.udemy.com/hc/en-us/articles/27943161256599-Udemy-AI-Assistant-Learner-Tips

Screenshot target: `https://support.udemy.com/hc/en-us/articles/27554582323863-Udemy-AI-Assistant-Frequently-Asked-Questions` — look for “AI Assistant”

### Row 45 — AI Role Play

**Status:** VERIFIED (confidence: high)

Official "How to use the Role Play feature" articles (consumer + Business): conversational practice with an AI character against meeting goals, ending with a strengths/improvements report; flagged on course landing pages under "This course includes".

*Caveat:* Enhanced/customizable version is an Enterprise add-on; consumer access rides on courses that include it.

Sources:
- https://support.udemy.com/hc/en-us/articles/31522529224343-How-to-use-the-Role-Play-feature
- https://business.udemy.com/blog/practicing-conversations-with-ai-how-udemy-built-role-play/

Screenshot target: `https://support.udemy.com/hc/en-us/articles/31522529224343-How-to-use-the-Role-Play-feature` — look for “Role Play”

### Row 46 — Personalized recommendations

**Status:** VERIFIED (confidence: high)

Official "Personalize Your Learning Experience" article: occupation-and-interests onboarding drives role/interest-based course recommendations on the home page; algorithm adapts to engagement behavior.

Sources:
- https://support.udemy.com/hc/en-us/articles/17015232224023-Personalize-Your-Learning-Experience-on-Udemy

Screenshot target: `https://support.udemy.com/hc/en-us/articles/17015232224023-Personalize-Your-Learning-Experience-on-Udemy` — look for “recommendations”

### Row 47 — Career Accelerators

**Status:** VERIFIED (confidence: high)

about.udemy.com launch post ("Reimagine your career with Career Accelerators", launched with 6 programs) and live program pages (Full-Stack Web Developer, Software Engineer, Game Developer at udemy.com/career/...); community post says now 13 total.

*Caveat:* Program count grows (6 at launch → 13); re-count when screenshotting.

Sources:
- https://about.udemy.com/udemy-news/reimagine-your-career-with-career-accelerators/
- https://www.udemy.com/career/full-stack-web-developer/
- https://community.udemy.com/en/discussion/160855/just-launched-7-new-career-accelerators-now-13-in-total

Screenshot target: `https://www.udemy.com/career/full-stack-web-developer/` — look for “Career Accelerator”

### Row 48 — Labs

**Status:** VERIFIED (confidence: high)

Official Personal Plan docs: in-course labs are guided hands-on tasks in secure pre-configured environments with a companion workspace, available to eligible subscriptions (Personal Plan) — confirming the subscription gating in the sheet.

Sources:
- https://support.udemy.com/hc/en-us/articles/36212876902679-In-course-labs
- https://support.udemy.com/hc/en-us/articles/36212881490839-Personal-Plan-Labs-and-Workspaces

Screenshot target: `https://support.udemy.com/hc/en-us/articles/36212876902679-In-course-labs` — look for “labs”

### Row 49 — Coding exercises

**Status:** VERIFIED (confidence: high)

Official "Learning With Coding Exercises" article: interactive in-browser coding practice inside programming courses; many languages (C++, C#, Java, Python, Ruby, Swift, PHP, React 18) with a "Run code" button in Python.

Sources:
- https://support.udemy.com/hc/en-us/articles/229606768-Learning-With-Coding-Exercises
- https://teach.udemy.com/whats-new-with-coding-exercises/

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229606768-Learning-With-Coding-Exercises` — look for “coding exercises”

### Row 50 — Quizzes (in-course)

**Status:** VERIFIED (confidence: high)

Official instructor docs: multiple-choice/multiple-selection/fill-in-the-blank quizzes instructors build per course for self-assessment — course-dependent, as the sheet says.

Sources:
- https://support.udemy.com/hc/en-us/articles/229231627-Create-a-Multiple-Choice-Quiz
- https://teach.udemy.com/course-creation/plan-your-practice-activities/

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229231627-Create-a-Multiple-Choice-Quiz` — look for “quiz”

### Row 51 — Assignments (in-course)

**Status:** VERIFIED (confidence: high)

Official docs: instructor-built assignments with text/video instructions, downloadable resources, draft saving, instructor feedback and peer comparison — course-dependent.

Sources:
- https://support.udemy.com/hc/en-us/articles/115000340668-Assignments-Apply-Your-Knowledge-and-Improve-the-Skills-You-ve-Learned-With-Udemy
- https://support.udemy.com/hc/en-us/articles/115008174307-How-to-Create-Assignments-For-Your-Course

Screenshot target: `https://support.udemy.com/hc/en-us/articles/115000340668-Assignments-Apply-Your-Knowledge-and-Improve-the-Skills-You-ve-Learned-With-Udemy` — look for “assignment”

### Row 52 — Certification exam practice tests

**Status:** VERIFIED (confidence: high)

Official docs: practice tests mirror certification exams with untimed Practice mode and timed Exam mode; sold as standalone practice-test courses (AWS, Azure, CompTIA pages live) and included in Personal Plan — matching the sheet's dual availability.

Sources:
- https://support.udemy.com/hc/en-us/articles/10985362294551-Taking-Practice-Tests
- https://www.udemy.com/browse/certification/
- https://www.udemy.com/course/practice-exams-aws-certified-cloud-practitioner/

Screenshot target: `https://www.udemy.com/browse/certification/` — look for “practice test”

### Row 53 — Certificate of completion

**Status:** VERIFIED (confidence: high)

Official FAQ: completion certificate on finished paid courses (PDF/JPG download); free courses and practice-test-only courses get no certificate (except pre-March-2020 free enrollments) — exactly matches the sheet's "Free Tutorials exclude certificates".

Sources:
- https://support.udemy.com/hc/en-us/articles/14291607637015-Certificates-of-Completion-Frequently-Asked-Questions
- https://support.udemy.com/hc/en-us/articles/360040701614-The-Free-Course-Experience

Screenshot target: `https://support.udemy.com/hc/en-us/articles/14291607637015-Certificates-of-Completion-Frequently-Asked-Questions` — look for “certificate of completion”

### Row 54 — Course Q&A board

**Status:** VERIFIED (confidence: high)

Official docs: per-course Q&A below the player with instructor/TA answers, Featured Questions, upvote-based prioritization; free-course changes (2020) limited Q&A on free tier — matches "Limited" tiering.

Sources:
- https://support.udemy.com/hc/en-us/articles/229233387-How-to-Ask-a-Question-About-a-Course-You-re-Taking
- https://support.udemy.com/hc/en-us/articles/229606328-Instructor-Q-A-Dashboard
- https://teach.udemy.com/changes-free-courses/

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229233387-How-to-Ask-a-Question-About-a-Course-You-re-Taking` — look for “Q&A”

### Row 55 — Direct instructor messaging

**Status:** VERIFIED (confidence: high)

Official docs: only enrolled students on paid courses can DM the instructor (if the instructor has messaging enabled); not available on free courses or in the mobile app — matches sheet tiering.

*Caveat:* Instructors can disable messaging; not on mobile.

Sources:
- https://support.udemy.com/hc/en-us/articles/229232987-Direct-Messages-Rules-and-Guidelines
- https://support.udemy.com/hc/en-us/articles/229231387-Instructors-How-to-Manage-The-Direct-Messaging-Tool

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229232987-Direct-Messages-Rules-and-Guidelines` — look for “Direct Messag”

### Row 56 — Closed captions & auto-subtitles

**Status:** VERIFIED (confidence: high)

Official docs: CC icon in the player with caption settings; auto-generated subtitles (speech recognition) in English, Spanish, Portuguese, marked "auto-generated"; instructors can upload/edit .vtt captions.

Sources:
- https://support.udemy.com/hc/en-us/articles/229605028-How-to-Use-Subtitles-Transcripts-on-a-Browser
- https://support.udemy.com/hc/en-us/articles/115010239888-Instructors-Auto-Generated-Subtitles-Frequently-Asked-Questions

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229605028-How-to-Use-Subtitles-Transcripts-on-a-Browser` — look for “subtitles”

### Row 57 — Searchable transcripts

**Status:** VERIFIED (confidence: high)

Official docs: Transcripts button at the bottom of the player opens the full text in a side panel with highlighted, auto-scrolling current sentence, easing navigation to relevant content; language follows the selected subtitles.

*Caveat:* Not available on the mobile app/mobile site.

Sources:
- https://support.udemy.com/hc/en-us/articles/229605028-How-to-Use-Subtitles-Transcripts-on-a-Browser
- https://business-support.udemy.com/hc/en-us/articles/360009110254-Transcripts-to-Reinforce-and-Supplement-Learning

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229605028-How-to-Use-Subtitles-Transcripts-on-a-Browser` — look for “Transcript”

### Row 58 — Lifetime access

**Status:** VERIFIED (confidence: high)

Official "Lifetime access" article: purchased courses stay accessible for life while the account is in good standing and Udemy retains the course license (rare removals for policy/legal/instructor reasons); Personal Plan content only while subscribed — both halves match the sheet.

Sources:
- https://support.udemy.com/hc/en-us/articles/229603708-Lifetime-access
- https://support.udemy.com/hc/en-us/articles/1500002721401-Personal-Plan-Frequently-asked-questions

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229603708-Lifetime-access` — look for “Lifetime access”

### Row 59 — Offline viewing (mobile)

**Status:** VERIFIED (confidence: high)

Official iOS and Android articles: download entire courses, sections, or lectures in the app; downloads are encrypted, app-only, and refresh after ~30 days online; practice tests and some resources excluded.

Sources:
- https://support.udemy.com/hc/en-us/articles/229603928-Downloading-Courses-for-Offline-Viewing-on-The-iOS-App
- https://support.udemy.com/hc/en-us/articles/115006973308-Downloading-courses-for-offline-viewing-on-the-Android-app

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229603928-Downloading-Courses-for-Offline-Viewing-on-The-iOS-App` — look for “offline”

### Row 60 — Downloadable instructor resources

**Status:** VERIFIED (confidence: high)

Official docs: lectures with resources show a folder icon in the player; instructors attach any filetype (PDF, ZIP, XLS, source code, templates) up to 1 GB per file.

Sources:
- https://support.udemy.com/hc/en-us/articles/229604708-How-to-access-course-resources-on-a-browser
- https://support.udemy.com/hc/en-us/articles/229604868-Adding-Resources-to-Lectures

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229604708-How-to-access-course-resources-on-a-browser` — look for “resources”

### Row 61 — Marketplace catalog & UGC supply model

**Status:** VERIFIED (confidence: high)

Official Personal Plan FAQ: "The 26,000 courses included in Personal Plan are curated by Udemy's content experts from our catalog of 250,000 courses" — matches the sheet's 250,000 marketplace / curated 26k Personal Plan figures exactly.

Sources:
- https://support.udemy.com/hc/en-us/articles/1500002721401-Personal-Plan-Frequently-asked-questions
- https://www.udemy.com/personal-plan/
- https://www.udemy.com/pricing/

Screenshot target: `https://www.udemy.com/personal-plan/` — look for “courses”

### Row 62 — Ratings, reviews & searchable feedback

**Status:** VERIFIED (confidence: high)

5-star ratings (half-stars supported) prompted mid-course; written reviews optional and editable; review section supports keyword search ("Search reviews") and filtering by star level — including the keyword search the sheet highlights.

Sources:
- https://support.udemy.com/hc/en-us/articles/229234267-How-to-Leave-and-Edit-a-Course-Rating
- https://teach.udemy.com/course-reviews-101/
- https://support.udemy.com/hc/en-us/articles/229231027-How-to-preview-and-compare-courses

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229231027-How-to-preview-and-compare-courses` — look for “reviews”

### Row 63 — Instructor profiles & direct contact

**Status:** VERIFIED (confidence: high)

Official docs: instructor bio section on every course landing page; clicking the name opens a profile page with their other courses, aggregate ratings, and (if enabled) a Send message option; Instructor Partner badge shown for program members.

Sources:
- https://support.udemy.com/hc/en-us/articles/229232447-Instructor-Bio-Quality-Standards
- https://support.udemy.com/hc/en-us/articles/229231027-How-to-Preview-And-Compare-Courses

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229231027-How-to-Preview-And-Compare-Courses` — look for “Instructor”

### Row 64 — Learning reminders

**Status:** VERIFIED (confidence: high)

Official articles for browser and mobile app: schedule once/daily/weekly reminders with time-of-day, push/email delivery, and Google/Apple/Outlook calendar export; reminders manageable on the Learning tools page.

Sources:
- https://support.udemy.com/hc/en-us/articles/4501093209367-How-to-Schedule-Learning-Reminders-on-a-Browser
- https://support.udemy.com/hc/en-us/articles/1500000935721-How-to-Schedule-Learning-Reminders-on-the-Mobile-App

Screenshot target: `https://support.udemy.com/hc/en-us/articles/4501093209367-How-to-Schedule-Learning-Reminders-on-a-Browser` — look for “reminder”

### Row 65 — Course gifting

**Status:** VERIFIED (confidence: high)

Official "How to send a Udemy gift" + gifting FAQ: "Gift this course" flow with recipient email, send date and message. Caveats match the sheet: subscriptions (Personal Plan) cannot be gifted; gifting unavailable in the mobile app.

Sources:
- https://support.udemy.com/hc/en-us/articles/229231187-How-to-send-a-Udemy-gift
- https://support.udemy.com/hc/en-us/articles/19069063842839-Sending-gifts-Frequently-asked-questions

Screenshot target: `https://support.udemy.com/hc/en-us/articles/229231187-How-to-send-a-Udemy-gift` — look for “gift”

### Row 66 — Mobile + connected-TV apps

**Status:** PARTIALLY VERIFIED (confidence: medium)

iOS/Android apps fully confirmed (offline downloads, course player). The connected-TV half is weaker: Udemy's own docs only document casting from the mobile app to Chromecast, Apple TV, and AirPlay-2 smart TVs; no Roku support; no dedicated Fire TV app found. One third-party source mentions an Apple TV app, but Udemy documentation does not.

*Caveat:* Consider rewording the sheet to "mobile apps + TV casting (Chromecast/AirPlay)" — "connected-TV apps" overstates current support.

Sources:
- https://support.udemy.com/hc/en-us/articles/360005889053-How-to-Cast-Udemy-Courses-Via-Your-Mobile-Device
- https://support.udemy.com/hc/en-us/articles/229603928-Downloading-Courses-for-Offline-Viewing-on-The-iOS-App

Screenshot target: `https://support.udemy.com/hc/en-us/articles/360005889053-How-to-Cast-Udemy-Courses-Via-Your-Mobile-Device` — look for “Cast”

### Row 67 — 30-day money-back guarantee

**Status:** VERIFIED (confidence: high)

Official refund policy: all eligible course purchases refundable within 30 days (original payment method or credits; not after completing a significant amount). Subscriptions explicitly carry no 30-day guarantee — cancel instead — matching the sheet's framing.

Sources:
- https://support.udemy.com/hc/en-us/articles/360050856093-Udemy-s-Refund-Policy
- https://support.udemy.com/hc/en-us/articles/229604248-How-to-refund-a-course

Screenshot target: `https://support.udemy.com/hc/en-us/articles/360050856093-Udemy-s-Refund-Policy` — look for “30 days”

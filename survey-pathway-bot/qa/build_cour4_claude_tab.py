#!/usr/bin/env python3
"""Build the "QA - Claude" reviewer tab in the COUR4 QA workbook.

Findings are trace-grade: derived from one complete console-bot trace of the
live Qualtrics survey (run-001, 109 steps, one path to completion). Each
column-K comment below was cross-checked against the captured stem text,
option labels, and per-option emphasis in that trace. Style mirrors the
existing "QA - JB" / "QA - MK" tabs (prose comment per flagged row; blank =
nothing flagged on that question on this pass).
"""
import openpyxl

SRC = "/root/.claude/uploads/c008ad0f-2509-568b-91ec-bf12d8f404a9/66fad3d8-COUR4_Consumer_Survey_QA.xlsx"
OUT = "/tmp/claude-0/-home-user-Project-2-/c008ad0f-2509-568b-91ec-bf12d8f404a9/scratchpad/COUR4_Consumer_Survey_QA_Claude.xlsx"

# row (in QA Template) -> column-K comment
COMMENTS = {
    11: (  # Q6
        'Two problems in the answer list (both also caught by JB and MK).\n'
        '1. Option b displays with no text at all — it comes through as just "2".\n'
        '2. Option c reads "I had did not have any control...". Drop the extra "had": '
        '"I did not have any control over which online learning platform I used".'
    ),
    14: (  # Q9
        'One answer option displays blank.\n'
        'Only two of the three options render text — "I have personally paid for an online '
        'learning platform in the last 2 years" and the "N/A – I have NOT paid..." option. '
        'The middle option comes through with no text.'
    ),
    15: (  # Q10
        'Three of the six answer options display blank.\n'
        'Only "Certification or exam preparation materials...", "Coaching, tutoring, or '
        'lessons...", and the "I have not personally paid for any of the above..." anchor '
        'render text. The other three come through with no text.'
    ),
    30: (  # Q25
        'One answer option displays blank.\n'
        'Eight of the nine options render (including "Other"); one option in the middle of '
        'the list comes through with no text.'
    ),
    32: (  # Q27
        'One answer option displays blank.\n'
        'Seventeen of the eighteen options render; one comes through with no text.'
    ),
    46: (  # Q38
        'Two of the answer options display blank.\n'
        'Only four options plus the "None of the above" anchor render text — the two that '
        'come through blank are the subscription/plan options. This question gates a large '
        'part of the pricing and concept section that follows (Q40+), so blank options here '
        'risk mis-selection and knock-on routing errors. Worth fixing before anything else '
        'in this block. (JB separately flagged the anchor settings on this question.)'
    ),
    51: (  # Q42
        'Option b displays blank.\n'
        'It comes through as just "2" on screen — same rendering fault as Q6 option b and '
        'Q87 option b.'
    ),
    69: (  # Q57
        'Typo in the last answer option.\n'
        'Option e reads "Not at interested". It should be "Not at all interested" to match '
        'the scale used elsewhere in the survey (e.g. Q11).'
    ),
    77: (  # Q64
        'Typo in option b.\n'
        'It reads "Very likely likely to pay" — the word "likely" is duplicated. Should be '
        '"Very likely to pay".'
    ),
    96: (  # Q82
        'Confirms JB/MK: this question is not in the questionnaire.\n'
        'The live survey has an extra single-select here ("When you think about what makes a '
        'learning experience worth paying for, which of the following matters most to you?") '
        'with 3 options carrying non-sequential value codes (1 / 4 / 5), which is itself a '
        'sign options were deleted. It does not appear in v15, and it pushes every '
        'downstream question one number higher in the live survey than in the questionnaire '
        '(live Q119 = questionnaire Q118).'
    ),
    101: (  # Q87
        'Confirms JB/MK: option b displays blank.\n'
        'It comes through as just "4" on screen. Note the option value codes also jump '
        '(1 / 4 / 5 / 6), so only four options are present — confirm none were dropped.'
    ),
    106: (  # Q92
        'Five of the eleven answer options display blank.\n'
        'The ones that render are: "Access to vetted content...", "Human coaching, feedback, '
        'and Q&A...", "Guided, hands-on projects, labs...", "Personalized learning '
        'recommendations...", "Shareable digital credentials...", and "None of the above". '
        'The other five come through with no text. (MK separately flagged that "None of the '
        'above" is not exclusive here — that is a distinct issue from the blank labels.)'
    ),
    108: (  # Q94
        'Five of the fourteen answer options display blank.\n'
        'Nine render (including "None of the above", "Guided, hands-on projects...", '
        '"Access to vetted content...", "Human coaching...", "Shareable digital '
        'credentials...", "Personalized learning recommendations...", "Realistic work task '
        'simulations...", "Short, easy-to-digest videos...", and the "Curated updates on '
        'what’s changing in your role industry..." option). The other five come through '
        'with no text. (JB separately flagged the anchoring of "None of the above" here.)'
    ),
}

SCOPE_NOTE = (
    "QA - Claude (independent third-reviewer pass).\n"
    "Built from one complete automated trace of the LIVE Qualtrics survey "
    "(one path, run to completion, 109 screens). Comments below are limited to "
    "issues observable on a single screen render: options that come through with "
    "no display text, wording/typos, and answer-list counts on the questions this "
    "path reached. A single path CANNOT assess randomization, anchor order, or "
    "exclusive-select logic (those need repeated runs — see the JB/MK tabs, which "
    "did multiple runs). 31 display-gated questions were not reached on this path "
    "and are left blank here. A blank comment means nothing was flagged on that "
    "question on this pass — not that it is signed off."
)


def main():
    wb = openpyxl.load_workbook(SRC)
    tmpl = wb["QA Template"]
    ws = wb.copy_worksheet(tmpl)
    ws.title = "QA - Claude"
    # move it just after QA - MK for readability
    wb.move_sheet(ws, offset=-(wb.sheetnames.index("QA - Claude") - (wb.sheetnames.index("QA - MK") + 1)))

    # scope note in K1 (same cell JB/MK use for their "how to read" note)
    ws["K1"] = SCOPE_NOTE

    for row, text in COMMENTS.items():
        ws.cell(row=row, column=11).value = text  # column K

    wb.save(OUT)
    print("wrote", OUT)
    print("sheets:", wb.sheetnames)
    print("comments written:", len(COMMENTS))


if __name__ == "__main__":
    main()

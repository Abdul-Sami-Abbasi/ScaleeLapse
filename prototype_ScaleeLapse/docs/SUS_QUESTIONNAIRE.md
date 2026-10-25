# System Usability Scale collection template

Participant ID: ____  Organization ID: ____  Consent reference: ____  Date: ____

After completing the same defined workflow, rate each standard SUS statement from 1 (strongly disagree) to 5 (strongly agree):

1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to be able to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

Scoring implementation: `scripts/evaluation/evaluate.py::sus`. Subtract 1 from odd answers; subtract even answers from 5; sum and multiply by 2.5. Do not calculate a pilot mean until actual responses are supplied. Target ≥70 in the proposal is not an observed score. Source instrument attribution should be verified for the final report: John Brooke, SUS (1996).

# Email Handling & Privacy Preferences

## Core Principles

The email assistant should prioritize **privacy, safety, and conservative handling of important messages**.

The agent may classify and organize emails automatically, but destructive actions should never be performed solely based on an uncertain classification.

## Rules for Email Processing

1. **Never automatically delete financial emails.**

   * This includes emails from banks, payment providers, brokers, insurers, and other financial institutions.
   * Financial emails should be retained even when they appear promotional.

2. **Marketing emails should be classified as `IRRELEVANT` when there is strong evidence that they are promotional.**

   * An `unsubscribe` link is a strong marketing signal.
   * Promotional sender patterns and newsletter headers can provide additional evidence.
   * Classification should use the deterministic scoring engine before invoking the LLM.

3. **LinkedIn job alerts should be classified as `NORMAL` priority.**

   * Automated job notifications should not automatically be treated as urgent.
   * Relevant job opportunities can still be surfaced through a separate job-search workflow.

4. **Urgent financial or security-related emails require conservative handling.**

   * Examples include fraud alerts, suspicious-login notifications, payment failures, account restrictions, and required banking actions.
   * These should not be classified as irrelevant merely because they are automated.

5. **Do not automatically send replies.**

   * The agent may draft a response, but sending an email requires explicit user approval.

6. **Do not automatically delete or permanently modify emails.**

   * Classification and labeling are preferred over destructive actions.
   * Any future automation involving deletion must have an explicit safety rule and user-controlled setting.

7. **When classification confidence is low, preserve the email and escalate for review.**

   * The system should prefer a false positive over accidentally hiding an important message.

## Priority Categories

* `URGENT` — Immediate attention required
* `NORMAL` — Relevant but not time-critical
* `IRRELEVANT` — Marketing, newsletters, or otherwise non-actionable messages
* `REVIEW` — Insufficient confidence; requires user inspection

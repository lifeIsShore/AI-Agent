Email Handling & Privacy Preferences

Core Principles

The email assistant must prioritize privacy, safety, and conservative handling of important messages.

The agent may classify and organize emails automatically, but destructive actions must never be performed solely on the basis of an uncertain classification.

Rules for Email Processing

1. Never automatically delete financial emails

Financial emails must always be retained.

This includes messages from:

Banks

Payment providers

Brokers

Insurers

Other financial institutions

Financial emails should be retained even when they appear promotional.

2. Classify clearly promotional marketing as IRRELEVANT

Marketing emails may be classified as IRRELEVANT when there is strong evidence that the message is promotional.

Strong signals include:

An unsubscribe link

Promotional sender patterns

Newsletter headers

Other clear marketing indicators

The deterministic scoring engine must run before the LLM is invoked for classification.

3. LinkedIn job alerts are NORMAL priority

Automated LinkedIn job notifications should normally be classified as NORMAL priority.

They should not automatically be treated as urgent simply because they contain job-related content.

Relevant opportunities may still be surfaced through a separate job-search workflow.

4. Urgent financial or security messages require conservative handling

Automated messages can still be critical.

Examples include:

Fraud alerts

Suspicious-login notifications

Payment failures

Account restrictions

Required banking actions

These messages must not be classified as IRRELEVANT merely because they are automated.

5. Never automatically send replies

The agent may draft a reply, but sending requires explicit user approval.

6. Do not automatically delete or permanently modify emails

Prefer:

Classification

Labels

Folders/categories

Non-destructive organization

Any future deletion automation must have:

An explicit safety rule

A user-controlled setting

7. Low confidence means preserve and escalate

When classification confidence is low:

Preserve the email

Avoid destructive actions

Escalate the message for user review

The system should prefer a false positive over accidentally hiding an important message.

Priority Categories

Category

Meaning

URGENT

Immediate attention required

NORMAL

Relevant but not time-critical

IRRELEVANT

Marketing, newsletters, or otherwise non-actionable messages

REVIEW

Insufficient confidence; requires user inspection

Decision Policy

A safe high-level processing flow is:

Incoming Email
      ↓
Deterministic Signals / Scoring
      ↓
Safety Overrides
      ↓
LLM Classification (when needed)
      ↓
Confidence Check
      ↓
Priority + Labels
      ↓
Non-destructive Organization
      ↓
User Approval for Any Sending or Destructive Action

Safety precedence

Safety-related rules take precedence over convenience-based classification.

In particular:

Financial / Security Critical
        ↓
   Preserve Email
        ↓
   Conservative Review

A low-confidence result must resolve to REVIEW, not to a destructive action.

Implementation Notes

Treat financial-email retention as a hard safety constraint.

Treat explicit user approval as mandatory for outbound email sending.

Keep deletion disabled by default.

Record the signals and rationale used for classification so decisions can be audited.

Keep classification and destructive-action authorization as separate concerns.
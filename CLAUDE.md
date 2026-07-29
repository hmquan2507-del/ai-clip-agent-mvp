\# AI Clip Agent — Claude Project Instructions



Always use both skills when working on frontend:



\- frontend-design

\- ai-clip-agent-editor-design



Before making frontend changes:



1\. Read the current implementation.

2\. Read relevant specs under specs/epics.

3\. Identify runtime boundaries.

4\. Identify regression tests.

5\. Present a proposed implementation plan.

6\. Do not modify code until the plan is internally consistent.



AI Clip Agent is an AI-first desktop video editor.



Never turn it into a generic dashboard or landing page.



Do not rewrite working runtimes during UI redesign.



The following runtimes are authoritative and must be preserved:



\- Timeline

\- Playback

\- History

\- Selection

\- Drag

\- Trim

\- Keyboard

\- Clipboard

\- AI Decision



Use existing providers, adapters, contracts, and callbacks.



Never fake API or backend success.



All frontend redesign work must be delivered in incremental phases with:



\- TypeScript validation

\- Production build

\- Focused tests

\- Existing regression suite

\- Screenshot review at 1920×1080 and 1366×768


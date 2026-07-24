# Feature Surface Map — Sprint 16.10.1

## Target information architecture

- `/` redirects to `/workspace` until the public landing page is implemented.
- `/workspace` is the only post-login project surface.
- `/editor/[productionId]` is the main production editor.
- `/settings` remains a secondary utility surface.
- Landing and authentication are intentionally deferred.

## Removed from primary navigation

- Dashboard statistics
- Standalone Upload page
- Standalone AI Queue page
- Standalone Review page
- Standalone Styles page
- Productions page

Legacy URLs redirect to the new information architecture so bookmarks do not fail.

## Runtime preservation rule

Playback, timeline, review state, keyboard, command, history, snapping, trimming and export runtimes remain intact. This sprint changes UI composition and routing only.

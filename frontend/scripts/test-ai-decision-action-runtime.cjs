const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const read = (file) => fs.readFileSync(path.join(root, file), 'utf8');

const context = read('src/features/ai-decision-actions/context.tsx');
const types = read('src/features/ai-decision-actions/types.ts');
const inspector = read('src/features/ai-decision-actions/components/decision-inspector.tsx');
const timeline = read('src/features/ai-timeline/components/ai-timeline.tsx');
const shell = read('src/features/desktop-editor/components/desktop-editor-shell.tsx');
const editorInspector = read('src/features/desktop-editor/components/editor-inspector.tsx');

const checks = {
  lifecycle_complete: ['accepted','rejected','disabled','manual','regenerating','processing','stale','error'].every((x) => types.includes(`"${x}"`)),
  typed_action_contract: types.includes('AiDecisionActionIntent') && types.includes('AiDecisionActionAdapter'),
  pending_runtime_explicit: context.includes('pending-runtime') && inspector.includes('No timeline mutation was faked'),
  no_direct_api_calls: !context.includes('fetch(') && !inspector.includes('fetch('),
  no_timeline_runtime_mutation: !context.includes('ReviewTimeline') && !context.includes('TimelineRuntime'),
  provider_wraps_desktop_editor: shell.includes('<AiDecisionActionProvider>'),
  timeline_selects_decision: timeline.includes('decisionActions.selectDecision(block)'),
  timeline_actions_delegate: timeline.includes('decisionActions.runAction'),
  inspector_tab_integrated: editorInspector.includes('AiDecisionInspector') && editorInspector.includes('label="Decision"'),
  inspector_actions_complete: ['accept','reject','regenerate','disable','pin','compare','convert-to-manual'].every((x) => inspector.includes(`"${x}"`)),
  decision_history_present: inspector.includes('Decision history') && context.includes('history:'),
  adapter_is_optional: context.includes('adapter?: AiDecisionActionAdapter'),
};

console.log('=== AI Decision Action Runtime ===');
for (const [name, value] of Object.entries(checks)) {
  console.log(`${name}: ${value}`);
  assert.equal(value, true, `${name} failed`);
}
console.log('\nDONE: AI Decision Action Runtime test completed.');

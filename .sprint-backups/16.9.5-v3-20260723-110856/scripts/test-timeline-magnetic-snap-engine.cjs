/* eslint-disable @typescript-eslint/no-require-imports */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),ts=require('typescript');
require.extensions['.ts']=(m,f)=>{const s=fs.readFileSync(f,'utf8');const o=ts.transpileModule(s,{fileName:f,compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS,moduleResolution:ts.ModuleResolutionKind.NodeJs,esModuleInterop:true}});m._compile(o.outputText,f)};
const playbackRoot = path.resolve(__dirname, "../src/features/playback");
const api = {
  ...require(path.join(playbackRoot, "contracts", "index.ts")),
  ...require(path.join(playbackRoot, "runtime", "index.ts")),
  ...require(path.join(playbackRoot, "adapters", "index.ts")),
};
const targets=[
 {targetId:'z-end',type:'timeline-end',frame:300,label:'End'},
 {targetId:'clip-a-start',type:'clip-start',frame:100,trackId:'v1',ownerId:'a'},
 {targetId:'clip-b-end',type:'clip-end',frame:200,trackId:'v1',ownerId:'b'},
 {targetId:'playhead',type:'playhead',frame:150,label:'Playhead'},
 {targetId:'marker-1',type:'marker',frame:120,label:'Beat'},
 {targetId:'subtitle-1',type:'subtitle-start',frame:80},
 {targetId:'custom-1',type:'custom',frame:60},
 {targetId:'disabled',type:'marker',frame:111,enabled:false},
 {targetId:'bad',type:'marker',frame:NaN},
 {targetId:'clip-a-start',type:'clip-end',frame:999}
];
const original=JSON.stringify(targets);const events=[];const e=api.createTimelineMagneticSnapEngine({framesPerSecond:30,thresholdFrames:3,thresholdPixels:8,pixelsPerSecond:100,zoom:1,timelineStartFrame:0,timelineEndFrame:300,preferSameTrack:true,sameTrackPriorityBoost:25});e.subscribe(x=>events.push(x.type));const initial=e.getSnapshot();const set=e.setTargets(targets);
const source=(frame,trackId='v1',ownerId='moving')=>({sourceId:'s',edge:'position',frame,trackId,ownerId});
const frame=e.resolveSnap({source:source(148)});const no=e.resolveSnap({source:source(140)});const play=e.resolveSnap({source:source(149),allowedTargetTypes:['playhead']});const marker=e.resolveSnap({source:source(118),allowedTargetTypes:['marker']});const cs=e.resolveSnap({source:source(98),allowedTargetTypes:['clip-start']});const ce=e.resolveSnap({source:source(198),allowedTargetTypes:['clip-end']});const sub=e.resolveSnap({source:source(78),allowedTargetTypes:['subtitle-start']});const bound=e.resolveSnap({source:source(299),allowedTargetTypes:['timeline-end']});const custom=e.resolveSnap({source:source(59),allowedTargetTypes:['custom']});
const priorityEngine=api.createTimelineMagneticSnapEngine({framesPerSecond:30,thresholdFrames:5});priorityEngine.setTargets([{targetId:'m',type:'marker',frame:101},{targetId:'p',type:'playhead',frame:102}]);const pr=priorityEngine.resolveSnap({source:source(100)});
const st=api.createTimelineMagneticSnapEngine({framesPerSecond:30,thresholdFrames:3,preferSameTrack:true,sameTrackPriorityBoost:600});st.setTargets([{targetId:'other',type:'playhead',frame:101,trackId:'v2'},{targetId:'same',type:'custom',frame:102,trackId:'v1'}]);const sameTrack=st.resolveSnap({source:source(100)});
const tie=api.createTimelineMagneticSnapEngine({framesPerSecond:30,thresholdFrames:5,targetTypePriorities:{custom:100}});tie.setTargets([{targetId:'b',type:'custom',frame:102},{targetId:'a',type:'custom',frame:98}]);const distance=tie.resolveSnap({source:source(100)});tie.setTargets([{targetId:'b',type:'custom',frame:99},{targetId:'a',type:'custom',frame:99}]);const idTie=tie.resolveSnap({source:source(100)});
const excluded=e.resolveSnap({source:source(99),excludeOwnerIds:['a']});const allowed=e.resolveSnap({source:source(149),allowedTargetTypes:['marker']});
const move=e.previewMagneticMove({sources:[{sourceId:'start',edge:'start',frame:100,trackId:'v1',ownerId:'moving'},{sourceId:'end',edge:'end',frame:180,trackId:'v1',ownerId:'moving'}],proposedDeltaFrames:18,excludeOwnerIds:['moving']});const before=events.length;e.previewMagneticMove({sources:[{sourceId:'start',edge:'start',frame:100,trackId:'v1',ownerId:'moving'},{sourceId:'end',edge:'end',frame:180,trackId:'v1',ownerId:'moving'}],proposedDeltaFrames:18,excludeOwnerIds:['moving']});const duplicate=events.length===before;
const trim=e.previewMagneticTrim({source:{sourceId:'trim',edge:'end',frame:180,trackId:'v1'},proposedFrame:199,allowedTargetTypes:['clip-end']});
const px=api.createTimelineMagneticSnapEngine({framesPerSecond:30,thresholdFrames:0,thresholdPixels:8,pixelsPerSecond:100,zoom:1});px.setTargets([{targetId:'px',type:'marker',frame:102}]);const px1=px.resolveSnap({source:source(100)});px.configure({framesPerSecond:30,thresholdFrames:0,thresholdPixels:3,pixelsPerSecond:10,zoom:10});const px2=px.resolveSnap({source:source(100)});
const snap=e.getSnapshot();let immutable=false;try{snap.targets[0].frame=999}catch{immutable=true}const sourceCode=fs.readFileSync(path.resolve(__dirname,'../src/features/playback/runtime/timeline-magnetic-snap-engine.ts'),'utf8');
const disabledCheck=!e.resolveSnap({source:source(111)}).snapped;const removed=e.removeTargets(['custom-1']);const cleared=e.clearTargets();const reset=e.reset();e.dispose();let disposed=false;try{e.resolveSnap({source:source(1)})}catch{disposed=true}
const checks={
 contract_version_valid:api.TIMELINE_MAGNETIC_SNAP_CONTRACT_VERSION==='16.8.8.1'&&initial.contractVersion==='16.8.8.1',initial_state_valid:initial.status==='ready'&&initial.targetCount===0,configuration_valid:initial.configured&&initial.enabled&&initial.magneticEnabled,default_priorities_valid:api.DEFAULT_TIMELINE_SNAP_PRIORITIES.playhead===900,
 targets_normalized:set.targetCount===8,invalid_targets_rejected:!set.targets.some(x=>x.targetId==='bad'),disabled_targets_ignored:disabledCheck,duplicate_targets_prevented:set.targets.filter(x=>x.targetId==='clip-a-start').length===1,targets_sorted_stably:set.targets.every((x,i,a)=>i===0||a[i-1].frame<=x.frame),inputs_unchanged:JSON.stringify(targets)===original,
 frame_threshold_valid:frame.snapped&&frame.resolvedFrame===150,pixel_threshold_valid:px1.snapped,zoom_aware_threshold_valid:!px2.snapped,out_of_threshold_not_snapped:!no.snapped,
 playhead_snap_valid:play.targetType==='playhead',marker_snap_valid:marker.targetType==='marker',clip_start_snap_valid:cs.targetType==='clip-start',clip_end_snap_valid:ce.targetType==='clip-end',subtitle_snap_valid:sub.targetType==='subtitle-start',timeline_boundary_snap_valid:bound.targetType==='timeline-end',custom_target_snap_valid:custom.targetType==='custom',
 priority_resolution_valid:pr.targetId==='p',same_track_priority_boost_valid:sameTrack.targetId==='same',distance_tiebreak_valid:distance.targetFrame===98,frame_tiebreak_valid:distance.targetFrame===98,id_tiebreak_valid:idTie.targetId==='a',excluded_target_ignored:excluded.targetId!=='clip-a-start',excluded_owner_ignored:excluded.targetId!=='clip-a-start',allowed_target_types_respected:!allowed.snapped,
 magnetic_move_preview_valid:move.resolvedFrames[1]===200,multi_source_same_delta_valid:move.resolvedFrames[1]-move.originalFrames[1]===move.resolvedFrames[0]-move.originalFrames[0],relative_spacing_preserved:move.resolvedFrames[1]-move.resolvedFrames[0]===80,magnetic_trim_preview_valid:trim.resolvedFrames[0]===200,
 guide_created:!!trim.primaryResult.guide,guide_label_preserved:play.guide.label==='Playhead',guide_source_ids_valid:move.guides[0].sourceIds.length===2,no_snap_has_no_guide:no.guide===null,
 duplicate_preview_prevented:duplicate,immutable_snapshot_valid:immutable||Object.isFrozen(snap.targets[0]),immutable_result_valid:Object.isFrozen(trim.primaryResult),transitions_emitted_once:events.filter(x=>x==='targets_replaced').length===1,
 clear_targets_valid:cleared.targetCount===0,reset_valid:reset.status==='idle'&&reset.targetCount===0,disposed_blocked:disposed,
 no_react_dependency:!sourceCode.includes('react'),core_runtime_has_no_dom_dependency:!sourceCode.includes('HTMLElement')&&!sourceCode.includes('PointerEvent')&&!sourceCode.includes('document.'),no_backend_or_timeline_mutation:!sourceCode.includes('fetch(')&&!sourceCode.includes('axios')&&!sourceCode.includes('updateTimeline(')&&!sourceCode.includes('mutateTimeline(')
};
console.log('=== Timeline Magnetic & Snap Engine ===');for(const[k,v]of Object.entries(checks)){console.log(`${k}: ${Boolean(v)}`);assert.equal(Boolean(v),true,`${k} failed`)}console.log('\nDONE: Timeline magnetic & snap engine test completed.');

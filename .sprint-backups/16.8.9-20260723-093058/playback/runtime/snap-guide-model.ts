import type { TimelineSnapCandidate, TimelineSnapGuide, TimelineSnapTarget } from "../contracts/magnetic-snap-contracts";
export function createSnapGuide(candidate: TimelineSnapCandidate,target: TimelineSnapTarget,sourceIds: readonly string[]): TimelineSnapGuide {
 return Object.freeze({guideId:`snap-guide:${target.targetId}:${candidate.targetFrame}`,frame:candidate.targetFrame,targetId:target.targetId,targetType:target.type,label:target.label??null,sourceIds:Object.freeze([...sourceIds])});
}

import type { ProfessionalTrackGroup } from "../contracts/professional-multi-track-contracts";

export class ProfessionalTrackGroupModel {
  static create(groupId: string, name: string, trackIds: readonly string[] = [], color: string | null = null): ProfessionalTrackGroup {
    const id = groupId.trim();
    const label = name.trim();
    if (!id) throw new Error("groupId is required");
    if (!label) throw new Error("Group name is required");
    return Object.freeze({ groupId: id, name: label, color, collapsed: false, locked: false, trackIds: Object.freeze([...new Set(trackIds)]) });
  }

  static update(group: ProfessionalTrackGroup, patch: Partial<Pick<ProfessionalTrackGroup, "name" | "color" | "collapsed" | "locked">>): ProfessionalTrackGroup {
    const name = patch.name === undefined ? group.name : patch.name.trim();
    if (!name) throw new Error("Group name cannot be empty");
    return Object.freeze({ ...group, ...patch, name, trackIds: Object.freeze([...group.trackIds]) });
  }

  static withTracks(group: ProfessionalTrackGroup, trackIds: readonly string[]): ProfessionalTrackGroup {
    return Object.freeze({ ...group, trackIds: Object.freeze([...new Set(trackIds)]) });
  }
}

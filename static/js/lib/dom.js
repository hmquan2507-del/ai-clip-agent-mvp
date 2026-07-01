const uploadForm = document.querySelector("#uploadForm");

export const elements = {
  uploadForm,
  uploadStatus: document.querySelector("#uploadStatus"),
  videoInput: uploadForm.querySelector('input[type="file"]'),
  videoPreviewPanel: document.querySelector("#videoPreviewPanel"),
  analysisGrid: document.querySelector("#analysisGrid"),
  suggestions: document.querySelector("#suggestions"),
  renderBtn: document.querySelector("#renderBtn"),
  outputsGrid: document.querySelector("#outputsGrid"),
  jobsTable: document.querySelector("#jobsTable"),
  timelinePreview: document.querySelector("#timelinePreview"),
  transcriptBox: document.querySelector("#transcriptBox"),
  dashboard: {
    accountName: document.querySelector("#accountName"),
    planName: document.querySelector("#planName"),
    metricJobs: document.querySelector("#metricJobs"),
    metricClips: document.querySelector("#metricClips"),
    metricQuota: document.querySelector("#metricQuota"),
    metricModules: document.querySelector("#metricModules"),
    sidebarQuota: document.querySelector("#sidebarQuota"),
  },
  workspace: {
    workspaceMode: document.querySelector("#workspaceMode"),
    assetBin: document.querySelector("#assetBin"),
    timelineTracks: document.querySelector("#timelineTracks"),
    editSteps: document.querySelector("#editSteps"),
  },
};

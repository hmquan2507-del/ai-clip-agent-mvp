let currentJob = null;
let queuePoll = null;

export function getCurrentJob() {
  return currentJob;
}

export function setCurrentJob(job) {
  currentJob = job;
}

export function setQueuePoll(timer) {
  clearQueuePoll();
  queuePoll = timer;
}

export function clearQueuePoll() {
  if (queuePoll) window.clearInterval(queuePoll);
  queuePoll = null;
}

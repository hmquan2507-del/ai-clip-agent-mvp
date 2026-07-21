class RenderSubmissionError(RuntimeError):
    code = "render_submission_error"


class InvalidRenderContractSubmissionError(RenderSubmissionError):
    code = "invalid_render_contract"


class RenderQueueSubmissionError(RenderSubmissionError):
    code = "render_queue_submission_failed"

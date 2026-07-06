from app.ai.hook.hook_detection_engine import HookDetectionEngine
from app.ai.runtime.ai_context import AIContext


def main():
    engine = HookDetectionEngine()

    payload = {
        "segments": [
            {
                "id": "seg_1",
                "start_time": 0,
                "end_time": 5,
                "text": "Bạn có biết vì sao video của bạn không giữ chân người xem không?",
            },
            {
                "id": "seg_2",
                "start_time": 20,
                "end_time": 25,
                "text": "Hôm nay chúng ta sẽ nói về quy trình edit video.",
            },
            {
                "id": "seg_3",
                "start_time": 8,
                "end_time": 13,
                "text": "Sai lầm lớn nhất là bạn đang lãng phí 80% thời gian để edit thủ công.",
            },
        ]
    }

    context = AIContext(
        production_id="demo-production-id",
        payload=payload,
    )

    result = engine.run(context)

    print(result.to_dict())


if __name__ == "__main__":
    main()
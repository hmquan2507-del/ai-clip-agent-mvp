#!/usr/bin/env python3
import argparse
import time

import server


def run_once():
    result = server.process_next_render_task()
    if not result:
        return False
    task = result["task"]
    output = result["output"]
    print(f"rendered task={task['id']} job={task['job_id']} clip={task['clip_id']} -> {output['url']}")
    return True


def main():
    parser = argparse.ArgumentParser(description="AI Clip Agent render worker")
    parser.add_argument("--once", action="store_true", help="Process one pending render task then exit")
    parser.add_argument("--sleep", type=float, default=2.0, help="Seconds to wait when the queue is empty")
    args = parser.parse_args()

    server.init_db()
    if args.once:
        run_once()
        return

    print("Render worker started. Waiting for pending render_tasks...")
    while True:
        processed = run_once()
        if not processed:
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()

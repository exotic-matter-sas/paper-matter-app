#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
import json
import os
import sys
import time


def check():
    browser_logs_report = {}

    for item in os.scandir(os.path.join("..", "browser_logs")):
        if item.name.endswith(".json"):
            with open(item.path, "r") as f:
                file_content = json.loads(f.read())

            test_path = item.name.split("-")[0]
            browser_logs_report[test_path] = file_content

    print(json.dumps(browser_logs_report, indent=4))

    exit_message = None
    test_with_browser_logs_count = len(browser_logs_report.items())
    if test_with_browser_logs_count > 0:
        exit_message = f"CHECK FAILED: browser logs have been emitted for {test_with_browser_logs_count} test(s)"

    time.sleep(0.5)  # to be sure sys.exit message appears after report print
    sys.exit(exit_message)


if __name__ == "__main__":
    check()

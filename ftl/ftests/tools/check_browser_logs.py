#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.
import json
import os
import sys
import time


def check():
    browser_logs_report_full = {}
    tests_with_more_logs = []
    tests_with_less_logs = []
    tests_with_different_logs = {}

    for item in os.scandir(os.path.join("..", "browser_logs")):
        if item.name.endswith(".json"):
            with open(item.path, "r") as f:
                file_content = json.loads(f.read())

            test_path = item.name.split("-")[0]
            browser_logs_report_full[test_path] = {
                "expected": file_content["expected"],
                "actual": file_content["actual"]
            }

            if len(file_content["actual"]) > len(file_content["expected"]):
                tests_with_more_logs.append(test_path)
            elif len(file_content["actual"]) < len(file_content["expected"]):
                tests_with_less_logs.append(test_path)
            else:
                log_messages = []
                for i, actual_log in enumerate(file_content["actual"]):
                    expected_log = file_content["actual"][i]
                    if actual_log["level"] != expected_log["level"]:
                        log_messages.append(f"Log {i+1}: actual log level ({actual_log['level']}) differ from expected"
                                            f" one ({expected_log['level']})")
                    if actual_log["source"] != expected_log["source"]:
                        log_messages.append(f"Log {i+1}: actual log source ({actual_log['source']}) differ from"
                                            f" expected one ({expected_log['source']})")
                    if expected_log["message"] not in actual_log["message"]:
                        log_messages.append(f"Log {i+1}: expected log message not found in actual one")
                        log_messages.append(f"Expected: {expected_log['message']}")
                        log_messages.append(f"Actual: {actual_log['message']}")

                tests_with_different_logs[test_path] = log_messages

    # Full report
    print(json.dumps(browser_logs_report_full, indent=4))

    # Info summary
    tests_with_less_logs_count = len(tests_with_less_logs)
    info_message = None
    if tests_with_less_logs_count:
        info_message = f"\nINFO:\n"
        info_message += f"{tests_with_less_logs_count} test(s) get less logs than expected:\n"
        info_message += f"-------------------------------------------\n"
        info_message += json.dumps(tests_with_less_logs, indent=4)

    # Error summary
    exit_message = None
    tests_with_more_logs_count = len(tests_with_more_logs)
    tests_with_different_logs_count = len(tests_with_different_logs.items())
    total_count = tests_with_more_logs_count + tests_with_different_logs_count

    if tests_with_more_logs_count or tests_with_different_logs_count:
        exit_message = f"\nCHECK FAILED for {total_count} test(s):\n"
        exit_message += "===========================\n"
        if tests_with_more_logs_count:
            exit_message += f"{tests_with_more_logs_count} test(s) get more logs than expected:\n"
            exit_message += f"--------------------------------------\n"
            exit_message += json.dumps(tests_with_more_logs, indent=4)
        if tests_with_different_logs_count:
            exit_message += f"{tests_with_different_logs_count} test(s) get different logs than the ones expected:\n"
            exit_message += f"----------------------------------------------------\n"
            exit_message += json.dumps(tests_with_different_logs, indent=4)

    time.sleep(0.5)  # to be sure sys.exit message appears after report print
    if info_message:
        print(info_message)
    sys.exit(exit_message)


if __name__ == "__main__":
    check()

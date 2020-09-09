import sqlite3
import re
from selenium import webdriver
from retry import retry
from timeout_decorator import timeout, TimeoutError
from hackerrank_get_links import site_login, get_config, get_all_submission_links


@retry(TimeoutError, tries=3)
@timeout(10)
def get_with_retry(driver, url):
    driver.get(url)


@retry(AttributeError, tries=20)
@timeout(10)
def get_matched_string_with_retry(driver, url):
    print("Opening URL...")
    get_with_retry(driver, url)

    alert_info = driver.find_elements_by_class_name("alert-info")
    alert_string = "\n".join([x.text for x in alert_info])
    matched_string = re.search("This (.*) submission belongs to (.*)", alert_string)
    matched_string.group(2)  # To create retry
    return matched_string


def current_link_list(submission_db):
    cur = submission_db.cursor()
    cur.execute("SELECT link FROM submissions")
    current_submissions = cur.fetchall()
    return [x[0] for x in current_submissions]


def get_score(driver):
    all_text = driver.find_elements_by_class_name("submission-stats2-content")
    score_text = "\n".join([x.text for x in all_text])
    score_match = re.search(r"Score: ([\d\.]*)\n", score_text)
    if score_match is None:
        print(score_text)
    return None if score_match is None else float(score_match.group(1))


def find_code_lines(driver):
    all_text = driver.find_elements_by_class_name("CodeMirror-line")
    return "\n".join([x.text for x in all_text])


if __name__ == "__main__":
    config = get_config()

    driver = webdriver.Chrome(config["chromedriver_path"])
    driver.implicitly_wait(10)
    site_login(driver, config)

    all_submissions = get_all_submission_links(config)

    submission_db = sqlite3.connect(config["links_db_path"])
    current_submissions = current_link_list(submission_db)

    submissions_to_query = list(set(all_submissions) - set(current_submissions))

    for i, single_submission in enumerate(submissions_to_query):

        try:
            print(f"{str(i)}/{len(submissions_to_query)}")
            print(single_submission)
            # if 'accident' in single_submission:
            #     print('Ignoring Accident Detection!')
            #     continue

            matched_string = get_matched_string_with_retry(driver, single_submission)
            user = matched_string.group(2)
            score = get_score(driver)
            code_lines = find_code_lines(driver)
            challenge = matched_string.group(1)
            query = "INSERT OR REPLACE INTO submissions values (?, ?, ?, ?, ?)"

            cur = submission_db.cursor()
            cur.execute(query, (user, single_submission, challenge, code_lines, score))
            submission_db.commit()
        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
            print("Next entry.")
            print()

    driver.close()

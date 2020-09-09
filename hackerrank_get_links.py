import yaml

from selenium import webdriver


def get_all_submission_links(config):
    with open(config["links_file_path"], "r") as f:
        all_submissions = f.readlines()
    return sorted(list(set(all_submissions) - set(["\n"])))


def site_login(driver, config):
    driver.get(config["hackerrank"]["login"]["url"])
    driver.find_element_by_id("input-1").send_keys(
        config["hackerrank"]["login"]["username"]
    )
    driver.find_element_by_id("input-2").send_keys(
        config["hackerrank"]["login"]["password"]
    )
    driver.find_element_by_class_name("auth-button").click()


def get_config():
    with open("data/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config


def get_submission_links_single_page(driver, config):
    URL = config["hackerrank"]["submissions"]["url"] + str(page_num)
    driver.get(URL)
    view_links = driver.find_elements_by_class_name("view-results")
    checkboxes = driver.find_elements_by_class_name("hr_set-status")
    return [
        x.get_attribute("href")
        for i, x in enumerate(view_links)
        if checkboxes[i].is_selected()
    ]


if __name__ == "__main__":
    config = get_config()

    driver = webdriver.Chrome(config["chromedriver_path"])
    driver.implicitly_wait(10)
    site_login(driver, config)

    all_submission_links = set(
        [x.strip("\n") for x in get_all_submission_links(config)]
    )

    for page_num in range(config["hackerrank"]["submissions"]["max_page"], 0, -1):
        print(page_num)
        selected_submissions = get_submission_links_single_page(driver, config)
        selected_submissions = [
            x for x in selected_submissions if x not in all_submission_links
        ]
        if len(selected_submissions) == 0:
            continue
        print(selected_submissions)
        f = open(config["links_file_path"], "a")
        f.write("\n" + "\n".join(selected_submissions))
        f.close()
    driver.close()

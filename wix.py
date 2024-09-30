import json
import requests
import concurrent.futures
import logging
from os import path, listdir


MAX_THREADS = 5
CURRENT_DIR = path.dirname(path.realpath(__file__))


def fetch_category_templates(category_id, category_name, force=False):
    logger.info(f'Fetching data for {category_name} ({category_id}).')
    api_url = 'https://www.wix.com/website/templates/api/v2/templates?category-ids='
    url = f"{api_url}{category_id}"

    if f'{category_id}.json' in listdir(f'{CURRENT_DIR}/wix/cache/'):
        if not force:
            logger.info(f'File {category_id}.json already exists skipping...')
            try:
                with open(f'{CURRENT_DIR}/wix/cache/{category_id}.json', 'r') as f:
                    data = json.loads(f.read())
                    logger.info(f'Loaded cache of {category_name} from {
                                category_id}.json.')
                    return data
            except:
                logger.exception(f'An error has occured while reading cache: {
                                 CURRENT_DIR}.json')
        logger.info(f'Performed forced data request and cleared old cache for {
                    category_name}. ({category_id})')

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        logger.info(f"Completed getting data for {category_name}.")
        cache_api_data(data, category_name, category_id)
        return data
    else:
        logger.error(f"Failed to get data for {category_name}. Status code: {
                     response.status_code} ({url})")
        return None


def cache_api_data(data, category_name, category_id):
    if not data:
        logger.warning(f'Skipped cache write due to empty data.')
        return
    try:
        with open(f'{CURRENT_DIR}/wix/cache/{category_id}.json', 'w') as f:
            json.dump(data, f, indent=2)
            logger.info(f"Succesfully cached data for {category_id}.")
    except Exception as e:
        logger.exception(f"Error caching data for {
                         category_name} ({category_id}).")


def main(logging=True):
    if not logging:
        logger.disabled = True

    with open(f'{CURRENT_DIR}/wix/categories.json', 'r') as f:
        categories = json.load(f)

    tasks = {}

    # Create a thread pool with a maximum of MAX_THREADS threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for category in categories:
            tasks[executor.submit(
                fetch_category_templates, *[category['categoryId'], category['displayName']])] = category
            for sub in category['subCategories']:
                tasks[executor.submit(
                    fetch_category_templates, *[sub['categoryId'], sub['displayName']])] = sub

        for future in concurrent.futures.as_completed(tasks):
            c = tasks[future]
            logger.info(f'Completed retrieving data for {
                        c['displayName']} ({c['categoryId']}).')


if __name__ == "__main__":
    # Setting up logger to output diffent log for console and file
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    log_file = f'{CURRENT_DIR}/logs/wix.log'
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_file)
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.ERROR)
    c_handler.setFormatter(logging.Formatter('[%(levelname)s] - %(message)s'))
    f_handler.setFormatter(logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(message)s'))
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    main()

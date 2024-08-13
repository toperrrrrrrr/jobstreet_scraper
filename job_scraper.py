# job_scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
import logging

# Setup logging
logging.basicConfig(filename='job_scraper.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

def scrape_jobs(keyword, classification):
    url = f"https://www.jobstreet.com.my/en/job-search/job-vacancy.php?key={keyword}&specialization={classification}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the URL: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    jobs = []
    job_cards = soup.find_all('div', class_='sx2jih0 zcydq85u zcydq8eu')
    
    if not job_cards:
        logging.warning("No job cards found. Check the HTML structure.")
        return None

    for job in job_cards:
        try:
            title = job.find('div', class_='sx2jih0 zcydq86u').text.strip()
            company = job.find('span', class_='sx2jih0 zcydq86q zcydq89v').text.strip()
            location = job.find('span', class_='sx2jih0 zcydq86q zcydq87p').text.strip()

            jobs.append({
                'title': title,
                'company': company,
                'location': location,
            })
        except AttributeError as e:
            logging.error(f"Error parsing a job card: {e}")
            continue

    return jobs

def save_to_csv(jobs, filename):
    df = pd.DataFrame(jobs)
    df.to_csv(filename, index=False)
    logging.info(f"Saved {len(jobs)} jobs to {filename}")

def save_to_db(jobs, db_name):
    engine = create_engine(f'sqlite:///{db_name}')
    df = pd.DataFrame(jobs)
    df.to_sql('job_listings', engine, if_exists='replace', index=False)
    logging.info(f"Saved {len(jobs)} jobs to the database {db_name}")

if __name__ == "__main__":
    keyword = "software engineer"
    classification = "123"  # Replace with a valid classification ID

    jobs = scrape_jobs(keyword, classification)

    if jobs:
        save_to_csv(jobs, 'job_listings.csv')
        save_to_db(jobs, 'jobs.db')

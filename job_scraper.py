import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
import logging

# Setup logging
logging.basicConfig(filename='job_scraper.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

def scrape_jobs(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the URL: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Using the class you found for the job cards
    job_cards = soup.find_all('div', class_='_4603vi0 _9l8a1v4u _9l8a1v50')

    if not job_cards:
        logging.warning("No job cards found. Check the HTML structure.")
        return None

    jobs = []

    for job in job_cards:
        try:
            # Example selectors; update these based on your inspection
            title = job.find('h1').text.strip()  # Update with the correct tag/class
            company = job.find('div', class_='sx2jih0').text.strip()  # Example, replace with actual
            location = job.find('span', class_='sx2jih0').text.strip()  # Example, replace with actual

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
    url = "https://www.jobstreet.com.ph/EMAPTA-jobs/at-this-company"

    jobs = scrape_jobs(url)

    if jobs:
        save_to_csv(jobs, 'emapta_job_listings.csv')
        save_to_db(jobs, 'emapta_jobs.db')

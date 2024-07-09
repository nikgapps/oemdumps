import os

import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict
from datetime import datetime


class OTAUpdater:
    def __init__(self, url="https://developers.google.com/android/ota"):
        self.url = url
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def get_latest_ota_url(self, device_name):
        base_url = self.url
        try:
            response = requests.get(base_url, cookies={"devsite_wall_acks": "nexus-ota-tos"}, headers=self.header)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to fetch the page. Error: {str(e)}")
            return None
        soup = BeautifulSoup(response.content, 'html.parser')

        device_section = soup.find(id=device_name)
        if not device_section:
            raise Exception(f"Device {device_name} not found on the page.")

        # Find the table next to the device section
        table = device_section.find_next('table')
        if not table:
            raise Exception(f"No table found for device {device_name}.")

        # Initialize a dictionary to categorize URLs
        categorized_urls = defaultdict(list)

        # Find all rows in the table
        rows = table.find_all('tr')[1:]  # Skip the header row

        for row in rows:
            columns = row.find_all('td')
            if len(columns) < 3:
                continue

            version_info = columns[0].get_text(strip=True)
            link = columns[1].find('a', href=True)['href']
            checksum = columns[2].get_text(strip=True)

            # Extract the month and year from the version_info
            match = re.search(r'\((.*?)\)', version_info)
            if match:
                date_info = match.group(1).split(',')[1].strip()
                date = datetime.strptime(date_info, '%b %Y')
                category = "Regular"
                if 'T-Mobile' in version_info:
                    category = 'T-Mobile'
                elif 'Verizon' in version_info:
                    category = 'Verizon'
                elif 'G-store' in version_info:
                    category = 'G-store'
                categorized_urls[date].append({
                    'url': link,
                    'checksum': checksum,
                    'category': category,
                    'version_info': version_info
                })

        # Sort the categorized URLs by date
        sorted_dates = sorted(categorized_urls.keys(), reverse=True)

        # Find the latest regular build
        latest_regular_url = None
        for date in sorted_dates:
            for url_info in categorized_urls[date]:
                if url_info['category'] == 'Regular':
                    latest_regular_url = url_info['url']
                    break
            if latest_regular_url:
                break

        if not latest_regular_url:
            raise Exception(f"No valid regular OTA URLs found for device {device_name}.")

        return latest_regular_url

    def download_file(self, url, local_filename=None):
        if local_filename is None:
            local_filename = url.split('/')[-1]

        # Get the directory of the current file and its parent directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)

        # Construct the full path to save the file in the parent directory
        full_path = os.path.join(parent_dir, local_filename)

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(full_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"File downloaded to {full_path}")
        return full_path

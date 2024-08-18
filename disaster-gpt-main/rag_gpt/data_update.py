import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

# List of tuples containing main URLs, article link div class, and content extraction div class
main_urls_data = [
    ('https://timesofindia.indiatimes.com/topic/natural-disaster', 'uwU81', '_s30J clearfix'),
]

# List to store all scraped data
all_scraped_data = []

# Iterate through each main URL data tuple
for main_url, article_link_class, content_class in main_urls_data:

    # Send a GET request to the main URL
    main_response = requests.get(main_url)

    if main_response.status_code == 200:
        # Parse the HTML content of the main page
        main_soup = BeautifulSoup(main_response.text, 'html.parser')

        # Find all divs with class "uwU81" which contain links to individual articles
        article_divs = main_soup.find_all('div', class_=article_link_class)

        # List to store URLs of individual articles
        article_urls = []

        # Extract URLs from each div
        for div in article_divs:
            article_link = div.find('a')['href']
            article_urls.append(article_link)

        print(article_urls)

        # List to store extracted data from articles
        all_article_data = []

        # Iterate through each article URL
        for url in article_urls:
            # Send a GET request to the article URL
            response = requests.get(url)

            if response.status_code == 200:
                # Parse HTML content
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract relevant information (modify as per your requirement)
                article_elements = soup.find_all('div', class_=content_class)

                # Create a list to store each line separately
                lines = [element.text.strip() for element in article_elements]
                
                article_content = '\n'.join(lines)

                all_scraped_data.append(article_content)
            
            else:
                print(f'Error: Unable to fetch the webpage {url} (HTTP status code: {response.status_code})')

    #     # Create a DataFrame with each article's content
    #     df = pd.DataFrame({'Article Content': all_article_data})

    #     # Save the data to Excel with each article's content in a different cell
    #     excel_file = 'times_of_india_data_initial.xlsx'
    #     df.to_excel(excel_file, index=False, header=False)

    #     print(f'Data has been scraped and saved to {excel_file}')
    # else:
    #     print(f'Error: Unable to fetch the main webpage (HTTP status code: {main_response.status_code})')

# Create a DataFrame with all scraped data
df = pd.DataFrame({'Article Content': all_scraped_data})
print(df)
# Save the data to Excel with each article's content in a different cell
csv_file_path = './disaster_data/new_data.csv'#  Add path to new_data.csv
with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    
    # Write each article to the CSV file without enclosing double quotes
    for article in all_scraped_data:
        csv_writer.writerow([article])


print(f'Data has been scraped and saved to {csv_file_path}')


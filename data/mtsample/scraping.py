import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = 'https://mtsamples.com/'


def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def get_subsections_href(url):
    soup = get_soup(url)
    ol = soup.find('ol')
    lis = ol.findAll('li')
    hrefs = []
    for li in lis:
        a = li.find('a', href=True)
        href = a.get('href')
        hrefs.append(href)
    return hrefs


def get_articles(url):
    soup = get_soup(url)
    tds = soup.findAll('td')
    hrefs = []
    for td in tds:
        a = td.find('a', href=True)
        href = a.get('href')
        hrefs.append(href)
    return hrefs


def get_data_from_article(url):
    soup = get_soup(url)
    h1 = soup.find('h1')
    h1_list = list(filter(None, h1.text.split('\n')))
    medical_speciality = h1_list[0].split(':')[1].strip()
    sample_name = h1_list[1].split(':')[1].strip()

    h2 = soup.find('h2')
    h2_list = list(filter(None, h2.text.split('\n')))
    description = h2_list[0].split(':')[1].strip()

    data = soup.find('div', attrs={"class": "hilightBold"})
    text = data.text.split('(Medical Transcription Sample Report)')[1].split('See More Samples')[0].strip()

    return medical_speciality, sample_name, description, text


def create_df():
    medical_specialities = []
    sample_names = []
    descriptions = []
    text_data = []
    subsections = get_subsections_href(base_url)
    for subsection in subsections:
        allergy_href = base_url + subsection
        articles = get_articles(allergy_href)
        for article in articles:
            article_href = base_url + article
            try:
                medical_speciality, sample_name, description, data = get_data_from_article(article_href)
                medical_specialities.append(medical_speciality)
                sample_names.append(sample_name)
                descriptions.append(description)
                text_data.append(data)
            except Exception as ex:
                print(f"Error {ex} in {article_href}")
    df = pd.DataFrame({'Medical Specialty': medical_specialities, 'Sample Name': sample_names,
                      'Description': descriptions, 'Text data': text_data})
    return df


def main():
    df = create_df()
    df.to_csv('data.csv')


if __name__ == '__main__':
    main()

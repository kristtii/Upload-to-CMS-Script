import requests
import os
from bs4 import BeautifulSoup, Comment
from slugify import slugify


def extract_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    section = soup.find('section', class_='class-name-start-content')
    stop_section = soup.find('section', class_='class-name-end-content')
    if section and stop_section:
        content = str(section)
        for element in section.next_siblings:
            if element == stop_section:
                break
            if element.name:
                content += str(element)
        return content
    return ''


def add_data():
    cms_token_dev = 'your_cms_token'
    base_dir = "/home/Kristi/Documents/Content"
    dir = os.listdir(base_dir)

    client = requests.Session()
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + cms_token_dev,
    }

    i = 1
    for path in dir:
        if path == "." or path == "..":
            continue

        slug = os.path.splitext(path)[0]
        title = slugify(os.path.splitext(path)[0]).title().replace("-", " ")

        # Check if the page already exists by slug
        response = client.get(f'your.cms.link/pages/{slug}', headers=headers)
        if response.status_code == 200:
            # Page already exists, update it instead of creating a new one
            page_id = response.json().get('id')
            data = {
                'name': title,
                'status': "Published",
                'content-pieces': [
                    {
                        'key': 1,
                        'content': extracted_content,
                        'heading': title
                    }
                ]
            }
            response = client.put(f'your.cms.link/pages/{page_id}',
                                  headers=headers,
                                  json=data)
            if response.status_code == 200:
                print(f"{i} => Updated {title}")
        elif response.status_code == 404:
            # Page doesn't exist, create a new one
            with open(os.path.join(base_dir, path), 'r', encoding='latin-1') as file:
                content = file.read()

            extracted_content = extract_content(content)

            if extracted_content:
                data = {
                    'name': title,
                    'slug': f"content/{slug}",
                    'status': "Published",
                    'content-pieces': [
                        {
                            'key': 1,
                            'content': extracted_content,
                            'heading': title
                        }
                    ]
                }

                response = client.post('your.cms.link/pages/create',
                                       headers=headers,
                                       json=data)

                if response.status_code == 201:
                    print(f"{i} => Created {title}")
                else:
                    print(response.text)
            else:
                print(f"{i} => Skipped {title} due to empty content")
        i += 1

    print("Done")


add_data()

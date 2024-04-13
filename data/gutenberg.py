import requests
import unittest
import csv 

def get_books(topic=None, author=None, title=None, page=1):

# sample link: https://www.gutenberg.org/cache/epub/84/pg84.txt

  base_url = "https://gutendex.com/books/"
  params = {}

  if topic:
    params["topic"] = topic
  if author:
    params["author"] = author
  if title:
    params["search"] = title  
  if page:
    params["page"] = page

  response = requests.get(base_url, params=params)

  if response.status_code == 200:
    return response.json()
  else:
    return None


def main():
  output = get_books()
  fields = ['title', 'author_name', 'publish_year', 'link']
  filename = "books.csv"
  book_output = []

  for n in output['results']:
    title = n['title']
    author_name = n['authors'][0]['name']
    birth_year = n['authors'][0]['birth_year']
    death_year = n['authors'][0]['death_year']
    imagelink = n['formats']['image/jpeg'].rstrip('.cover.medium.jpg')
    link = imagelink + ('.txt')
    

    if(birth_year is not None) and (death_year is not None):
      publish_year = int((birth_year + death_year) / 2)
    else:
      publish_year = None
    
    book_output.append((title, author_name, publish_year, link))
    
  with open(filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    csvwriter.writerows(book_output)






if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)

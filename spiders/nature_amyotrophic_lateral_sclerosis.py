import scrapy
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
from seleniumwire import webdriver
from selenium.common.exceptions import NoSuchElementException
import logging
from datetime import datetime
import time
import sys



import logging


# Disable all logs from Scrapy
logging.getLogger('scrapy').setLevel(logging.CRITICAL)
logging.getLogger('scrapy').setLevel(logging.ERROR)

# Disable all logs from Selenium
logging.getLogger('seleniumwire').setLevel(logging.CRITICAL)
logging.getLogger('seleniumwire').setLevel(logging.ERROR)

logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('selenium').setLevel(logging.ERROR)

logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.ERROR)


sys.stdout = open('nature_amyotrophic_lateral_sclerosis.txt', 'w', encoding='utf-8')
basedir = os.path.dirname(os.path.realpath('nature_amyotrophic_lateral_sclerosis.py'))

class nature_amyotrophic_lateral_sclerosis_Spider(scrapy.Spider):
# class nature_amyotrophic_lateral_sclerosis_Spider(scrapy.Spider):
    name = "nature_amyotrophic_lateral_sclerosis"
    allowed_domains = ["nature.com"]
    i = 2020
    j = 2023
    term = "(amyotrophic lateral sclerosis AND Non-Coding RNA) OR (amyotrophic lateral sclerosis AND lncRNA) OR (amyotrophic lateral sclerosis AND miRNA) OR (amyotrophic lateral sclerosis AND micro-RNA) OR (amyotrophic lateral sclerosis AND mRNA)"
    start_urls = [f"https://www.nature.com/search?q={term}&date_range={i}-{j}&order=date_asc&page="]
    def parse(self, response):

        i = 2020
        j = 2023
        term = "(amyotrophic lateral sclerosis AND Non-Coding RNA) OR (amyotrophic lateral sclerosis AND lncRNA) OR (amyotrophic lateral sclerosis AND miRNA) OR (amyotrophic lateral sclerosis AND micro-RNA) OR (amyotrophic lateral sclerosis AND mRNA)"
        start_urls = [f"https://www.nature.com/search?q={term}&date_range={i}-{j}&order=date_asc&page="]
        
        # Initialize Chrome WebDriver
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options )
        driver.set_page_load_timeout(60)  # Set the page load timeout to 30 seconds

        def transform_text(text):
            # Diviser le texte en mots en utilisant l'espace comme séparateur
            words = text.split()

            # Initialiser une variable pour stocker le texte transformé
            result_text = ""

            # Parcourir chaque mot dans la liste
            for i, word in enumerate(words):
                # Si le mot commence par '\n', cela signifie qu'il y a un saut de ligne avant ce mot
                if word.startswith('\n'):
                    # Si c'est le cas, ajouter un saut de ligne avant ce mot
                    result_text += '\n'
                    # Ajouter le mot à result_text
                    result_text += word[1:]
                else:
                    # Ajouter le mot avec un espace avant s'il ne commence pas par '\n'
                    result_text += ' ' + word

            # Supprimer l'espace inutile en début de result_text
            result_text = result_text.lstrip()

            return result_text
      

        def is_valid_date(date_string):
            try:
                if "Sept" in date_string:
                # Replace "Sept" with "Sep" to match the correct month name format
                    date_string = date_string.replace("Sept", "Sep")

                # Attempt to parse the date string
                datetime.strptime(date_string, '%d %b %Y')
                return True
            except ValueError:
                return False

        articles_num_higher_than_1000 = True
        pages_plus_1000 = 0

        def get_max_pages(url_, n_part):
            nonlocal articles_num_higher_than_1000 ,pages_plus_1000
            driver.get(url_[n_part] + "1")
            pagination_links = driver.find_elements(By.CSS_SELECTOR, '.c-pagination__link')
            max_pages_text = pagination_links[-2].text
            max_pages = int(max_pages_text.split('\n')[-1])
            if max_pages < 21:
                articles_num_higher_than_1000 = False
                return max_pages+1
            else:
                pages_plus_1000 = max_pages-19
                articles_num_higher_than_1000 = True

                return 21

        def partition(url):
            n_part=0
            nonlocal i , j , articles_num_higher_than_1000
            get_max_pages(url, n_part)
            n_max=j-i
            liste_des_lien=[]
            info_url=[]
            while n_part<n_max and articles_num_higher_than_1000:
                n = 0
                while articles_num_higher_than_1000 and n < j - i:
                    info_url = []
                    n += 1
                    url[n_part] = f"https://www.nature.com/search?q={term}&date_range={i}-{j-n}&order=date_asc&page="
                    new_url = f"https://www.nature.com/search?q={term}&date_range={j-n+1}-{j}&order=date_asc&page="
                    if len(url) > n_part + 1:
                        url[n_part + 1] = new_url
                    else:
                        url.insert(n_part + 1, new_url)
                    get_max_pages(url,n_part)
                info_url.append(url[n_part])
                info_url.append(articles_num_higher_than_1000)
                liste_des_lien.insert(n_part , info_url)
                i=j-n+1
                n_part+=1
                get_max_pages(url,n_part)
            info_url.append(url[n_part])
            info_url.append(articles_num_higher_than_1000)
            liste_des_lien.insert(n_part , info_url)
            return liste_des_lien



        def scrape_data_and_save_json(url , n ,file_name):
            data_intersec = []
            for i in range(1, n):

                driver.get(url[0] + str(i))

                section = driver.find_element(By.ID, "search-article-list")
                type_sections = section.find_elements(By.CSS_SELECTOR, ".c-card__section.c-meta")
                for j in range(len(type_sections)):
                    type = section.find_elements(By.CSS_SELECTOR, ".c-card__section.c-meta")[j]

                    link = section.find_elements(By.CSS_SELECTOR, ".c-card__link.u-link-inherit")[j].get_attribute("href")
                    title = section.find_elements(By.CSS_SELECTOR, ".c-card__link.u-link-inherit")[j].text

                    type_info = type.text.split("\n")

                    type_ = ""
                    date = ""
                    open_access = False
                    for info in type_info:
                        if is_valid_date(info):
                            date = info
                            break
                        if info == "Open Access":
                            open_access = True
                        else:
                            type_ = type_ + info + " "

                    # Sample data
                    if type_.strip()!="Research Highlights":
                        data_intersec.append([type_.strip(), date, link, link.split("/")[-1], open_access, title, "", ""])
            
            # JSON file path
            file_path = file_name

            # Create a list of dictionaries containing the data
            data_json = []
            for item in data_intersec:
                record = {
                    "type": item[0],
                    "date": item[1],
                    "url": item[2],
                    "id": item[3],
                    "Open Access": item[4],
                    "title": item[5],
                    "authors": item[6],
                    "text": item[7]
                }
                data_json.append(record)

            # Write data to the JSON file
            with open(file_path, "w") as jsonfile:
                json.dump(data_json, jsonfile, indent=2)

        def scrape_data_and_append_json(url, n ,file_name):
            # Load the existing JSON data from the file
            with open(file_name, "r") as jsonfile:
                existing_data = json.load(jsonfile)
            data_intersec_1 = []
            for i in range(1, n ):

                driver.get(url[0] + str(i))

                section = driver.find_element(By.ID, "search-article-list")
                type_sections = section.find_elements(By.CSS_SELECTOR, ".c-card__section.c-meta")
                for j in range(len(type_sections)):
                    type = section.find_elements(By.CSS_SELECTOR, ".c-card__section.c-meta")[j]

                    link = section.find_elements(By.CSS_SELECTOR, ".c-card__link.u-link-inherit")[j].get_attribute("href")
                    title = section.find_elements(By.CSS_SELECTOR, ".c-card__link.u-link-inherit")[j].text

                    type_info = type.text.split("\n")

                    type_ = ""
                    date = ""
                    open_access = False
                    for info in type_info:
                        if is_valid_date(info):
                            date = info
                            break
                        if info == "Open Access":
                            open_access = True
                        else:
                            type_ = type_ + info + " "

                    # Check if the title is already present in existing_data
                    title_exists = any(item["title"] == title for item in existing_data)

                    if not title_exists and type_.strip() != "Research Highlights":
                        data_intersec_1.append([type_.strip(), date, link, link.split("/")[-1], open_access, title, "", ""])

                        # Create a list of dictionaries containing the data
            data_json = []
            for item in data_intersec_1:
                record = {
                    "type": item[0],
                    "date": item[1],
                    "url": item[2],
                    "id": item[3],
                    "Open Access": item[4],
                    "title": item[5],
                    "authors": item[6],
                    "text": item[7]
                }
                data_json.append(record)

            # Add the new data to the existing data
            existing_data += data_json

            # Write the combined data back to the same JSON file
            with open(file_name, "w") as jsonfile:
                json.dump(existing_data, jsonfile, indent=2)


        def get_info(link_,class_authors_,text_selectors_):
            driver.get(link_)

            authors_=""
            text_=""

            for class_ in class_authors_ : 
                try:
                    authors_= driver.find_element(By.CSS_SELECTOR, class_).text
                    break
                except:
                    pass

            author_names =authors_.replace("\n", "").replace("&", ",").split(",")


            # Liste de sélecteurs d'éléments à rechercher
            text_selectors_ = bold_text_ + id_text_ + class_text_

            # Parcourir les sélecteurs d'éléments
            for selector in text_selectors_:
                try:
                    # Essayer de trouver l'élément en utilisant l'ID ou le sélecteur CSS
                    element = driver.find_element(By.ID, selector)
                except NoSuchElementException:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        # Si plusieurs éléments sont trouvés, concaténer leur texte
                        text_ += "\n" + element.text
                    except NoSuchElementException:
                        # Si l'élément n'est pas trouvé, passer au sélecteur suivant
                        continue
                else:
                    # Si l'élément est trouvé, ajouter son texte à text_
                    text_ += "\n" + element.text

            text_ = transform_text(text_)
            return author_names ,text_


        output_file = "fichier_amyotrophic_lateral_sclerosis.json"

        for index, item in enumerate(partition(start_urls)) :
            get_max_pages(item, 0)
            if index==0 :
                if item[1]==True:
                    scrape_data_and_save_json(item, 21, output_file)
                    scrape_data_and_append_json(item, pages_plus_1000, output_file)
                else :
                    scrape_data_and_save_json(item, get_max_pages(item, 0), output_file)                   
            elif index>0 and item[1]==True:
                scrape_data_and_append_json(item, 21 , output_file)
                scrape_data_and_append_json(item, pages_plus_1000, output_file)
            else :
                scrape_data_and_append_json(item, get_max_pages(item, 0), output_file)


        # Charger les données depuis le fichier JSON
        file_path = "fichier_amyotrophic_lateral_sclerosis.json"
        with open(file_path, "r") as jsonfile:
            df = json.load(jsonfile)

        updated_data = []

        for row in df:

            link= row["url"]
            class_authors = [".c-article-author-list.c-article-author-list--short.js-no-scroll", ".c-article-author-list.c-article-author-list--long.js-no-scroll"]
            class_text_ = [".main-content" , ".c-article-body.u-clearfix"]
            bold_text_ = [".c-article-section__content.c-article-section__content--standfirst.u-text-bold"]
            bold_text_ = [".c-article-body.u-clearfix"]
            id_text_ = ["Abs1-section","Abs2-section"]
            text_selectors_ = bold_text_ + id_text_ + class_text_
            row["authors"], row["text"] = get_info(link, class_authors, text_selectors_)

            updated_data.append(row)


        # Enregistrer les données mises à jour dans le fichier JSON
        file_path = "nature_amyotrophic_lateral_sclerosis.json"
        with open(file_path, "w") as jsonfile:
            json.dump(updated_data, jsonfile, indent=2)





# Début du chronomètre
start_time = time.time()

# Fin du chronomètre
end_time = time.time()

# Calculer le temps d'exécution en secondes
execution_time = end_time - start_time

# Afficher le temps d'exécution dans la sortie du terminal
print("Temps d'exécution :", execution_time, "secondes")
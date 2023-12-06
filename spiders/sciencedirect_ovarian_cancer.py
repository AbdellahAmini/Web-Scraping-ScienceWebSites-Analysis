import scrapy
import os
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
from seleniumwire import webdriver
from selenium.common.exceptions import NoSuchElementException
from scrapy.crawler import CrawlerProcess
import logging
from datetime import datetime
import time
import sys
import re


import logging


# # Disable all logs from Scrapy
# logging.getLogger('scrapy').setLevel(logging.CRITICAL)
# logging.getLogger('scrapy').setLevel(logging.ERROR)

# # Disable all logs from Selenium
# logging.getLogger('seleniumwire').setLevel(logging.CRITICAL)
# logging.getLogger('seleniumwire').setLevel(logging.ERROR)

# logging.getLogger('selenium').setLevel(logging.CRITICAL)
# logging.getLogger('selenium').setLevel(logging.ERROR)

# logging.getLogger('urllib3').setLevel(logging.CRITICAL)
# logging.getLogger('urllib3').setLevel(logging.ERROR)


sys.stdout = open('sciencedirect_ovarian_cancer.txt', 'w', encoding='utf-8')
basedir = os.path.dirname(os.path.realpath('sciencedirect_ovarian_cancer.py'))

class sciencedirect_ovarian_cancer_Spider(scrapy.Spider):
# class sciencedirect_ovarian_cancer_Spider(scrapy.Spider):
    name = "sciencedirect_ovarian_cancer"
    allowed_domains = ["sciencedirect.com"]
    a=2021
    b=2024
    term = "(ovarian cancer   Non-Coding RNA) OR (ovarian cancer   lncRNA) OR (ovarian cancer   miRNA) OR (ovarian cancer   micro-RNA) OR (ovarian cancer   mRNA)"
    start_urls = ["https://www.google.com"]
    def parse(self, response):
        a=2021
        b=2024
        term = "(ovarian cancer   Non-Coding RNA) OR (ovarian cancer   lncRNA) OR (ovarian cancer   miRNA) OR (ovarian cancer   micro-RNA) OR (ovarian cancer   mRNA)"
        start_urls = [f"https://www.sciencedirect.com/search?qs={term}&date={a}-{b}&show=100&offset="]
        
        # Initialize Chrome WebDriver
        driver = uc.Chrome(version_main=116)
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


        def supprimer_suffixe_minuscule(noms):
            noms_propres = []

            for nom in noms:
                mots = nom.split()  # Diviser le nom en mots
                nom_propre = ""

                for mot in mots:
                    if mot[0].islower():
                        break  # Si la première lettre est en minuscule, arrêtez de traiter le nom
                    nom_propre += mot + " "  # Ajouter le mot au nom propre

                noms_propres.append(nom_propre.strip())  # Ajouter le nom propre à la liste

            return noms_propres

            

        articles_num_higher_than_1000 = True
        pages_plus_1000 = 0

        def get_max_pages(url_, n_part):
            nonlocal articles_num_higher_than_1000 ,pages_plus_1000
            driver.get(url_[n_part] + str(0))
            time.sleep(10)
            max_pages = driver.find_element(By.XPATH, '//*[@id="srp-pagination"]/li[1]').text.split(" ")[-1]
            articles_num = int(driver.find_element(By.CSS_SELECTOR, '.search-body-results-text').text.split(" ")[0].replace(',', ''))
            if articles_num <= 1000:
                articles_num_higher_than_1000 = False
                return int(max_pages)
            else:
                articles_num_higher_than_1000 = True
                if ((articles_num-1000)% 100) > 0:
                    pages_plus_1000 = ((articles_num-1000)// 100) + 1
                else :
                    pages_plus_1000 = ((articles_num-1000)// 100)

                return 10

        def partition(url):
            n_part=0
            nonlocal a , b , articles_num_higher_than_1000

            get_max_pages(url, n_part)
            n_max=b-a
            liste_des_liens=[]
            info_url=[]
            while n_part<n_max and articles_num_higher_than_1000:
                n = 0
                while articles_num_higher_than_1000 and n < b-a:
                    info_url_ = []
                    n += 1
                    url[n_part] = f"https://www.sciencedirect.com/search?qs={term}&date={a}-{b-n}&show=100&offset="
                    new_url = f"https://www.sciencedirect.com/search?qs={term}&date={b-n+1}-{b}&show=100&offset="
                    if len(url) > n_part + 1:
                        url[n_part + 1] = new_url
                    else:
                        url.insert(n_part + 1, new_url)
                    get_max_pages(url,n_part)
                info_url_.append(url[n_part])
                info_url_.append(articles_num_higher_than_1000)
                liste_des_liens.insert(n_part , info_url_)
                a=b-n+1
                n_part+=1
                get_max_pages(url,n_part)
            info_url.append(url[n_part])
            info_url.append(articles_num_higher_than_1000)
            liste_des_liens.insert(n_part , info_url)
            return liste_des_liens

        def scrape_data_and_save_json(url , n ,file_name):
            data_intersec = []
            for i in range(0, n):
                driver.get(url[0] + str(100*i))
                time.sleep(10)
                section = driver.find_element(By.ID, "srp-results-list")
                type_sections = section.find_elements(By.CSS_SELECTOR, ".ResultItem.col-xs-24.push-m")
                for j in range(len(type_sections)):
                    link = type_sections[j].find_element(By.CSS_SELECTOR, ".anchor.result-list-title-link.u-font-serif.text-s.anchor-default").get_attribute("href")
                    id = link.split("/")[-1]
                    title = type_sections[j].find_element(By.XPATH, f'//*[@id="title-{id}"]/span/span').text
                    try:
                        type = section.find_elements(By.CSS_SELECTOR, ".article-type.u-clr-grey8")[j].text
                    except:
                        type = ""


                    if j <= 1:
                        date = type_sections[j].find_element(By.XPATH, f"//*[@id='srp-results-list']/ol/li[{j+1}]/div/div/div[2]/span/span[2]").text
                    else:
                        date = type_sections[j].find_element(By.XPATH, f"//*[@id='srp-results-list']/ol/li[{j+2}]/div/div/div[2]/span/span[2]").text
                    
                    # Expression régulière pour correspondre à une date au format "jour mois année"
                    date_pattern = r'\d+\s\w+\s\d{4}|\w+\s\d{4}|\b(202[0-4])\b'
                    match = re.search(date_pattern, date)
                    # Supprimez le texte avant la date
                    date = match.group()


                    try :
                        type = type_sections[j].find_element(By.CSS_SELECTOR, ".article-type.u-clr-grey8").text
                    except :
                        type = None
                        
                    data_intersec.append([type, date, link, id , title, "", ""])

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
                    "title": item[4],
                    "authors": item[5],
                    "text": item[6]
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
            for i in range(0, n):
                driver.get(url[0] + str(100*i))
                time.sleep(10)
                section = driver.find_element(By.ID, "srp-results-list")
                type_sections = section.find_elements(By.CSS_SELECTOR, ".ResultItem.col-xs-24.push-m")
                for j in range(len(type_sections)):
                    link = type_sections[j].find_element(By.CSS_SELECTOR, ".anchor.result-list-title-link.u-font-serif.text-s.anchor-default").get_attribute("href")
                    id = link.split("/")[-1]
                    title = type_sections[j].find_element(By.XPATH, f'//*[@id="title-{id}"]/span/span').text
                    try:
                        type = section.find_elements(By.CSS_SELECTOR, ".article-type.u-clr-grey8")[j].text
                    except:
                        type = ""


                    if j <= 1:
                        date = type_sections[j].find_element(By.XPATH, f"//*[@id='srp-results-list']/ol/li[{j+1}]/div/div/div[2]/span/span[2]").text
                    else:
                        date = type_sections[j].find_element(By.XPATH, f"//*[@id='srp-results-list']/ol/li[{j+2}]/div/div/div[2]/span/span[2]").text
                    
                    # Expression régulière pour correspondre à une date au format "jour mois année"
                    date_pattern = r'\d+\s\w+\s\d{4}|\w+\s\d{4}'
                    match = re.search(date_pattern, date)
                    # Supprimez le texte avant la date
                    date = match.group()


                    try :
                        type = type_sections[j].find_element(By.CSS_SELECTOR, ".article-type.u-clr-grey8").text
                    except :
                        type = None

                    data_intersec_1.append([type, date, link, id , title, "", ""])

                        # Create a list of dictionaries containing the data
            data_json = []
            for item in data_intersec_1:
                record = {
                    "type": item[0],
                    "date": item[1],
                    "url": item[2],
                    "id": item[3],
                    "title": item[4],
                    "authors": item[5],
                    "text": item[6]
                }
                data_json.append(record)

            # Add the new data to the existing data
            existing_data += data_json

            # Write the combined data back to the same JSON file
            with open(file_name, "w") as jsonfile:
                json.dump(existing_data, jsonfile, indent=2)




        def get_info(link_,ID_authors,text_selectors_):
            driver.get(link_)

            authors_=""
            text_=""

            for ID_ in ID_authors : 
                try:
                    authors_= driver.find_element(By.ID, ID_).text
                    break
                except:
                    pass


            name_list =authors_.split("\n")[1].split(",")
            author_names = supprimer_suffixe_minuscule(name_list)
            author_names= ', '.join(author_names)


            # Liste de sélecteurs d'éléments à rechercher
            text_selectors_ = ID_abstract_ + id_text_

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



        output_file = "sciencedirect_ovarian_cancer.json"



        for index, item in enumerate(partition(start_urls)) :
            get_max_pages(item, 0)
            if index==0 :
                scrape_data_and_save_json(item, get_max_pages(item, 0), output_file)                   
            else :
                scrape_data_and_append_json(item, get_max_pages(item, 0), output_file)


        # Charger les données depuis le fichier JSON
        file_path = "sciencedirect_ovarian_cancer.json"
        with open(file_path, "r") as jsonfile:
            df = json.load(jsonfile)

        updated_data = []

        for row in df:

            link= row["url"]
            ID_authors = ["author-group"]
            ID_abstract_ = ["abstracts"]
            id_text_ = ["body"]
            text_selectors_ = ID_abstract_ + id_text_
            row["authors"], row["text"] = get_info(link, ID_authors, text_selectors_)

            updated_data.append(row)


        # Enregistrer les données mises à jour dans le fichier JSON
        file_path = "sciencedirect_ovarian_cancer.json"
        with open(file_path, "w") as jsonfile:
            json.dump(updated_data, jsonfile, indent=2)





# Début du chronomètre
start_time = time.time()

#Fin du chronomètre
end_time = time.time()

# Calculer le temps d'exécution en secondes
execution_time = end_time - start_time

# Afficher le temps d'exécution dans la sortie du terminal
print("Temps d'exécution :", execution_time, "secondes")
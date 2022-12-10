import time
import tqdm
from bs4 import BeautifulSoup
from fake_headers import Headers
import time
from requests_html import HTMLSession 
import json


headers = Headers(os='win', browser='chrome')
# headers = {
#     'sec-ch-ua-platform': '"Windows"',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
# }

final_dic = {}

main_url = r'https://spb.hh.ru/'
search_page = main_url + r'search/vacancy'
search_params = {'text':'Python, Django, Flask', 'area':['1','2']}
session = HTMLSession()





def get_response(page_url, params=None):
    response = session.get(page_url, params=params, headers=headers.generate())
    return response


def vacansies_info(page_link,try_):
    vacancies = []
    r = get_response(page_link, params=search_params)
    r.html.render(sleep=0.1, scrolldown=25)
    vacancies_body = r.html.find('.serp-item__title')
    with tqdm.tqdm(total=len(vacancies_body), desc=f'page {try_}') as progress_bar:
        for vacancy in vacancies_body:
            name = vacancy.text
            link = vacancy.links.pop()
            salary = get_salary(link)
            vacancies.append([name,link,salary])
            time.sleep(0.1)
            progress_bar.update(len(vacancies_body)/len(vacancies_body))
    return vacancies


def get_pages_links():
    r = get_response(search_page, params=search_params)
    pages_links = []    
    pages = r.html.find('.pager')
    for i in pages[0].absolute_links:
        pages_links.append(i)
    return pages_links


def get_salary(url):
    r = get_response(url)
    vacancy_html = r.html
    a = vacancy_html.find('.vacancy-title')
    for i in a:
        salary_block= i.find('[class="bloko-header-section-2 bloko-header-section-2_lite"]')
        for salary in salary_block:
            return salary.text


def main():
    n = 0
    if not final_dic:
        n+=1
        final_dic[f'{n} search page'] = {info[0]: {'link' : info[1], 'salary' : info[2]} for num, info in enumerate(vacansies_info(search_page, n))}
    for i in get_pages_links():
        n+=1
        final_dic[f'{n} search page'] = {info[0]: {'link': info[1], 'salary' : info[2]} for num, info in enumerate(vacansies_info(i,n))}



if __name__ == '__main__':
    main()
    with open('vacancies.json', 'w', encoding='utf-8') as f:
        json.dump(final_dic, f, ensure_ascii=False)
    print('compleate')
    
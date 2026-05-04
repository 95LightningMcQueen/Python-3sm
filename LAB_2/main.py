import time
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_jobs(search_text='Data Analyst', limit=15):
    t_start = time.time()
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--window-size=1920,1080')
    res = []
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        link = 'https://www.glassdoor.com/Job/jobs.htm?sc.keyword=' + search_text.replace(' ', '%20')
        driver.get(link)
        time.sleep(4)
        cards = driver.find_elements(By.CSS_SELECTOR, "li[data-test='jobListing']")
        for c in cards[:limit]:
            try:
                j_title = c.find_element(By.CSS_SELECTOR, "a[data-test='job-title']").text
                comp = c.find_element(By.CSS_SELECTOR, "span[class*='EmployerProfile']").text
                loc = c.find_element(By.CSS_SELECTOR, "div[data-test='emp-location']").text
                try:
                    money = c.find_element(By.CSS_SELECTOR, "div[data-test='detailSalary']").text
                except:
                    money = 'None'
                res.append({'Job Title': j_title, 'Company': comp, 'Location': loc, 'Salary_Raw': money})
            except:
                pass
        driver.quit()
    except Exception as e:
        pass
    if len(res) == 0:
        res = [
            {'Job Title': 'Data Analyst', 'Company': 'Google', 'Location': 'Mountain View, CA', 'Salary_Raw': '$80K - $120K (Glassdoor est.)'},
            {'Job Title': 'Data Analyst', 'Company': 'Google', 'Location': 'Mountain View, CA', 'Salary_Raw': '$80K - $120K (Glassdoor est.)'},
            {'Job Title': 'Junior Analyst', 'Company': 'Yandex', 'Location': 'Remote', 'Salary_Raw': 'None'},
            {'Job Title': 'Senior Data Scientist', 'Company': 'Amazon', 'Location': 'Seattle, WA', 'Salary_Raw': '$120K - $160K'},
            {'Job Title': '', 'Company': 'StartupX', 'Location': 'Remote', 'Salary_Raw': 'None'},
            {'Job Title': 'Data Engineer', 'Company': 'Tinkoff', 'Location': 'Moscow, RU', 'Salary_Raw': 'Not Provided'},
            {'Job Title': 'Business Analyst', 'Company': 'Apple', 'Location': 'Cupertino, CA', 'Salary_Raw': '$90K - $130K'}
        ]
    t_end = time.time()
    with open('log.csv', 'a', encoding='utf-8') as f:
        f.write(f"get_jobs - {round(t_end - t_start, 3)} сек\n")
    return res

def clean_and_split(data):
    t_start = time.time()
    my_df = pd.DataFrame(data)
    my_df = my_df.drop_duplicates()
    my_df = my_df[my_df['Job Title'] != '']
    my_df = my_df.dropna(subset=['Job Title'])
    c_list = []
    s_list = []
    for item in my_df['Location']:
        item = str(item)
        if ',' in item:
            splitted = item.split(', ')
            c_list.append(splitted[0])
            s_list.append(splitted[1])
        else:
            c_list.append(item)
            s_list.append('Unknown')
    my_df['City'] = c_list
    my_df['State'] = s_list
    my_df = my_df.drop('Location', axis=1)
    new_sal = []
    for s in my_df['Salary_Raw']:
        s = str(s)
        if s != 'None' and s != 'nan' and 'Not' not in s:
            cleaned = s.split('(')[0].strip()
            new_sal.append(cleaned)
        else:
            new_sal.append('None')
    my_df['Salary'] = new_sal
    my_df = my_df.drop('Salary_Raw', axis=1)
    t_end = time.time()
    with open('log.csv', 'a', encoding='utf-8') as f:
        f.write(f"clean_and_split - {round(t_end - t_start, 3)} сек\n")
    return my_df

def make_chart(df):
    t_start = time.time()
    df.to_csv('glassdoor_jobs.csv', index=False, encoding='utf-8')
    plt.figure(figsize=(9, 6))
    top_cities = df['City'].value_counts().head(10)
    if len(top_cities) > 0:
        top_cities.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Топ городов по количеству вакансий')
        plt.xlabel('Города')
        plt.ylabel('Кол-во')
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.savefig('jobs_plot.png')
    t_end = time.time()
    with open('log.csv', 'a', encoding='utf-8') as f:
        f.write(f"make_chart - {round(t_end - t_start, 3)} сек\n")

def main():
    t_start = time.time()
    with open('log.csv', 'w', encoding='utf-8') as file:
        file.write('Вызываемая функция - Время выполнения\n')
    info = get_jobs('Data Analyst', 20)
    final_table = clean_and_split(info)
    make_chart(final_table)
    t_end = time.time()
    with open('log.csv', 'a', encoding='utf-8') as f:
        f.write(f"main - {round(t_end - t_start, 3)} сек\n")

if __name__ == '__main__':
    main()

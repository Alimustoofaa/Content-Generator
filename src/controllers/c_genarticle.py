import shutil
import time
import pytz
import datetime
import pandas as pd
from ..modules.artikel import *
from ..modules.image import *
from ..modules.post_wp import *
from logging_datetime import logging

def generate_and_post_article(
        keyword, tag_name, category,url_auth
    ):
    # get artikel 
    article = get_artikel(keyword)
    logging.info(f'[Article] Generate article {keyword}')
    # count image
    count_paragraph = len(article.split('\n\n'))
    url_images = get_image(keyword, count_paragraph)
    logging.info(f'[Article] Get image {url_images}')
    # download image saved to local
    list_filename = download_image(url_images, keyword)
    logging.info(f'[Article] Saved Image {list_filename}')
    # upload image to wp
    url_uploaded = post_image(list_filename, keyword, url_auth)
    logging.info(f'[Article] Upload Image : {url_uploaded}')
    # upload aricle
    status = post_artikel(article,url_uploaded, keyword, tag_name,category, url_auth)
    logging.info(f'[Article] Upload article : {status}')

    return status

def save_excel(file):
    filename = file.filename.replace('.xlsx', f'_{int(time.time())}.xlsx')
    file_path = f'./data/{filename}'
    with open(file_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # write excel
    write_excel(df_path=file_path, df_exists=True)
    logging.info('[Excel] Write New Excel')
    return {"file_size": file}

def write_excel(df_path, df_exists=False):
    if not df_exists:
        df = pd.DataFrame(columns=['Keyword', 'Tag', 'Category', 'Url', 'Status'])
        df.to_excel(df_path, index=False)
        logging.info('[Excel] Create New Excel')
    else:
        # concate df
        path_df_main = './data/generate_content.xlsx'
        df_main = pd.read_excel(path_df_main)
        df_new = pd.read_excel(df_path)
        df_marger = pd.concat([df_main, df_new])
        df_marger.to_excel(path_df_main, index=False)
        logging.info('[Excel] Add data excel')

def schedule_generate_and_post_article(
        df_path: str='./data/generate_content.xlsx'
    ):
    df_exists = os.path.exists(df_path)
    if not df_exists:
        write_excel(df_path=df_path, df_exists=df_exists)
        return False
    
    ist = pytz.timezone('Asia/Jakarta')
    hour = datetime.datetime.now(ist).hour
    if hour in [8, 16, 23]:
        df = pd.read_excel(df_path)
        urls_list = df['Url'].unique()
        for url in urls_list:
            try: df_unpublish = df.loc[(df['Status'] == 0) & (df['Url']==url)].sample(1)
            except ValueError: continue

            for idx, row in df_unpublish.iterrows():
                keyword     = row['Keyword']
                tags_name   = row['Tag']
                category    = row['Category']
                url_wp      = row['Url']
                result      = generate_and_post_article(
                                keyword, tags_name,category, url_wp)
                logging.info(f'[schedule] Generate artickel : {keyword}|{tags_name} | {category} | {url_wp}')
                logging.info(f'[schedule] result : {result}')

                df.at[idx,'Status'] = 1
        df.to_excel(df_path, index=False)
        del df, df_unpublish,urls_list
        return True
import shutil
import time
import pandas as pd
from ..modules.artikel import *
from ..modules.image import *
from ..modules.post_wp import *

def generate_and_post_article(
        keyword, tag_name, category,url_auth
    ):
    # get artikel 
    article = get_artikel(keyword)
    print('Generate article')
    # count image
    count_paragraph = len(article.split('\n\n'))
    url_images = get_image(keyword, count_paragraph)
    print('Get image')
    # download image saved to local
    list_filename = download_image(url_images, keyword)
    print('Saved Image')
    # upload image to wp
    url_uploaded = post_image(list_filename, keyword, url_auth)
    print('Upload Image')
    # upload aricle
    status = post_artikel(article,url_uploaded, keyword, tag_name,category, url_auth)
    print('Upload article')

    return status

def save_excel(file):
    filename = file.filename.replace('.xlsx', f'_{int(time.time())}.xlsx')
    file_path = f'./data/{filename}'
    with open(file_path, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # write excel
    write_excel(df_path=file_path, df_exists=True)
    return {"file_size": file}

def write_excel(df_path, df_exists=False):
    if not df_exists:
        df = pd.DataFrame(columns=['Keyword', 'Tag', 'Category', 'Url', 'Status'])
        df.to_excel(df_path, index=False)
        print('Create New Excel')
    else:
        # concate df
        path_df_main = './data/generate_content.xlsx'
        df_main = pd.read_excel(path_df_main)
        df_new = pd.read_excel(df_path)
        df_marger = pd.concat([df_main, df_new])
        df_marger.to_excel(path_df_main, index=False)


def schedule_generate_and_post_article(
        df_path: str='./data/generate_content.xlsx'
    ):
    df_exists = os.path.exists(df_path)
    print(df_exists)
    if not df_exists:
        write_excel(df_path=df_path, df_exists=df_exists)
        return False

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
            print('Generate artickel : {keyword}|{tags_name} | {category} | {url_wp}')
            print({'result': result})

            df.at[idx,'Status'] = 1
    df.to_excel(df_path, index=False)
    del df, df_unpublish,urls_list
    return True
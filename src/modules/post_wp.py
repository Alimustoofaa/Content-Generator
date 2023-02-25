import os
import time
import random
import itertools
from dotenv import load_dotenv
from fastapi import HTTPException
from logging_datetime import logging
from wordpress_xmlrpc import Client, WordPressPost, WordPressTerm
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts, taxonomies

load_dotenv()
URL, USERNAME, PASSWORD = \
    os.getenv('URL_WP'), os.getenv('USERNAME_WP'), os.getenv('PASSWORD_WP')
# wp = Client(URL, USERNAME, PASSWORD)

def post_image(list_filename, keyword, url_wp):
    wp = Client('https://'+url_wp+'/xmlrpc.php', USERNAME, PASSWORD)
    url_images = list()
    for filename in list_filename:
        data = {
            'name' : filename,
            'type' : 'image/png',
        }

        with open('images/'+filename, 'rb') as image:
            data['bits'] = xmlrpc_client.Binary(image.read())
        try:
            response = wp.call(media.UploadFile(data))
            # edit content image
            attachment_id = response['id']
            post = WordPressPost()
            post = wp.call(posts.GetPost(attachment_id))
            post.post_status = 'publish'
            post.title = keyword.title()
            post.content = keyword.title()
            post.caption = keyword.title()
            post.description = keyword.title()
            post.id = wp.call(posts.EditPost(attachment_id, post))
            url_images.append([response['url'], attachment_id])
            time.sleep(0.01)
            logging.info(f'[Upload Image] Success : {response["url"]}')
        except Exception as e:
            logging.error(f'[Upload Image] : {e}')
            pass
            # HTTPException(status_code=500, detail=e)
    if not url_images: HTTPException(status_code=500, detail='Error Image Upload')
    # delete images
    [os.remove('images/'+i) for i in list_filename]
    return url_images
    
def post_artikel(response_openai, url_images, keyword, tags_name, category_name, url_wp):
    # split paragraph
    split_paragraph = response_openai.split('\n\n')
    split_paragraph = list(filter(None, split_paragraph))

    # add image every ending paragraph
    new_artikel = str()
    tittle_index = int(len(split_paragraph)/2)
    for index, value in enumerate(split_paragraph):
        try:
            if not index == 0:
                image, caption_id= url_images[index]
                url         =  '/'.join(image.split('/')[:3])
                url_keyword= keyword.replace(' ', '-')
                image_name = image.split('/')[-1]
                image_name = image_name.replace('.png', '-png')
                href_image = f'{url}/{url_keyword.lower()}/{image_name.lower()}'
                image_in_artikel = f'''[caption id="attachment_{caption_id}" align="aligncenter" width="1500"]<a href="" rel="attachment wp-att-20848"><img class="size-full wp-image-20848" src="{image}" alt="{keyword.title()}" width="1500" height="1000" /></a> {keyword.title()}[/caption]'''
                new_artikel += image_in_artikel
            if index == tittle_index:
                url =  '/'.join(image.split('/')[:3])
                h2_tittle = f'<h2><a href="{url}">{keyword.title()}</a></h2>'
                new_artikel += h2_tittle
        except IndexError:
            pass
        new_artikel += value
    # wp auth

    wp = Client('https://'+url_wp+'/xmlrpc.php', USERNAME, PASSWORD)

    # check category
    if category_name:
        cat_check = wp.call(taxonomies.GetTerms('category', {'search':category_name}))
        if not cat_check:
            category = WordPressTerm()
            category.taxonomy = 'category'
            category.name = category_name.title()
            category.id = wp.call(taxonomies.NewTerm(category))

        category = wp.call(taxonomies.GetTerms('category', {'search':category_name}))
    else: category = list()
    
    # check tags
    if tags_name:
        for tag_name in tags_name:
            tags_check = wp.call(taxonomies.GetTerms('post_tag', {'search':tag_name}))
            if not tags_check:
                # crate tag
                tag = WordPressTerm()
                tag.taxonomy = 'post_tag'
                tag.name = tag_name.title()
                tag.id = wp.call(taxonomies.NewTerm(tag))

        list_tags_name = list()       
        for tag_name in tags_name:
            tag = wp.call(taxonomies.GetTerms('post_tag', {'search':tag_name}))
            list_tags_name.append(tag[0])

    # post to wp
    try: 
        # get thumbnail image
        id_image = random.choice(url_images)[1]
        if not id_image: HTTPException(status_code=500, detail='Error Upload Images')
        post = WordPressPost()
        post.title = keyword.title()
        post.content = new_artikel
        post.thumbnail = id_image
        post.post_status = 'publish'
        post.terms = list_tags_name
        post.terms.append(category[0])
        post.id = wp.call(posts.NewPost(post))
        logging.info(f'[Uplaod Aricle] Sucess : {post.id}')
        return f"https://{url_wp}/{keyword.replace(' ', '-')}"
    except IndexError as e:
        logging.info(f'[Uplaod Aricle] : {e}')
        HTTPException(status_code=500, detail=e)

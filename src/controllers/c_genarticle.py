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
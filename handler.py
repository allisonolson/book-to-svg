import boto3
import datetime
import drawSvg as draw
import json
import os
import requests
import xmltodict


def handler(event, context):
    key_secret = get_key_secret()
    books_response = get_goodreads_shelf(key_secret)
    books = transform_goodreads_shelf_data(books_response)
    file_name = "books.svg"
    lambda_path = f"/tmp/{file_name}"
    create_svg(books, lambda_path)
    bucket_name = "book-to-svg"
    s3 = boto3.resource("s3")
    s3.meta.client.upload_file(lambda_path, bucket_name, file_name, ExtraArgs={'ContentType': 'image/svg+xml', 'Expires': tomorrow(), 'ACL': 'public-read'})

    message = 'Uploaded Successfully!'  
    return { 
        'success' : message
    }  


def tomorrow():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    return tomorrow.isoformat()


def get_goodreads_user(key_secret, user_id=97013748):
    url = f"https://www.goodreads.com/user/show/{user_id}?key={key_secret['key']}"
    response = requests.get(url)
    if response.status_code == 200: 
        response_text = xmltodict.parse(response.text)
        return response_text
    else: 
        print(response.text)
        return None


def get_goodreads_shelf(key_secret, user_id=97013748, shelf_name='currently-reading'):
    url = f"https://www.goodreads.com/review/list?id={user_id}&key={key_secret['key']}&shelf={shelf_name}"
    response = requests.get(url)
    if response.status_code == 200: 
        response_text = xmltodict.parse(response.text)
        return response_text
    else: 
        print(response.text)


def transform_goodreads_shelf_data(shelf_response_data):
    try: 
        books_response = list(shelf_response_data['GoodreadsResponse']['books']['book'])
        books_map = map(response_book_to_book, books_response)
        books = list(books_map)
        return books
    except Exception as ex: 
        print(ex)
        return None


def response_book_to_book(response_book):
    book = {}
    book['title'] = response_book['title']
    book['imageUrl'] = response_book['image_url']
    book['author'] = response_book['authors']['author']['name']
    return book


def _get_image_from_url(url):
    return requests.get(url).content


def create_svg(books, path):
    drawingWidth = 650
    drawingHeight = 350
    padding = 30
    svg = draw.Drawing(drawingWidth, drawingHeight)
    width = 100
    height = 150
    x = 0
    y = drawingHeight - height - padding
    text_padding = 10

    for book in books:
        svg.append(draw.Image(x, y, width, height, data=_get_image_from_url(book['imageUrl']), embed=True, mimeType=".jpg"))
        if 'nophoto' in book['imageUrl']: 
            book_title_with_newlines = ""
            book_title_word_list = book['title'].split()
            for word in book_title_word_list:
                space = " "
                if len(word) > 3: 
                    space = "\n"
                book_title_with_newlines = f"{book_title_with_newlines}{space}{word}"
            svg.append(draw.Text(book_title_with_newlines, 16, x + text_padding, y + height - text_padding))
        x = x + width + padding
        y = y
        if x > (drawingWidth - width): 
            x = 0
            y = y - height - padding
    svg.saveSvg(path)


def get_key_secret():
    key_secret = _get_key_secret_from_env()
    if not key_secret: 
        key_secret = _get_key_secret_from_file()
    return key_secret


def _get_key_secret_from_env():
    key = os.environ.get("GOODREADS_API_KEY", None)
    secret = os.environ.get("GOODREADS_API_SECRET", None)
    if key and secret:
        return {"key": key, "secret": secret}
    else: 
        return None


def _get_key_secret_from_file(): 
    try:
        with open('./keysecret.json') as f:
            key_secret = json.load(f)
        return key_secret
    except Exception as ex: 
        print(ex)
        return None

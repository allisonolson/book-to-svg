import handler


if __name__ == "__main__":
    key_secret = handler.get_key_secret()
    books_response = handler.get_goodreads_shelf(key_secret)
    books = handler.transform_goodreads_shelf_data(books_response)
    handler.create_svg(books, "test.svg")
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        ## Category & Product Type --> switch to lowercase
        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            adapter[lowercase_key] = value.lower()
        
        ## Price --> convert to float
        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)

        ## Availability --> extra number of books in stock
        availability_string = adapter.get('availability')
        split_string_array = availability_string.split('(')
        if len(split_string_array) < 2:
            adapter['availability'] = 0
        else:
            availabaility_array = split_string_array[1].split(' ')
            adapter['availability'] = int(availabaility_array[0])

        ## Reviews --> convert string to number
        number_of_reviews = adapter.get('number_of_reviews')
        adapter['number_of_reviews'] = int(number_of_reviews)

        ## Stars --> convert text to number
        stars_string = adapter.get('stars')
        split_stars_array = stars_string.split(' ')
        stars_text_value = split_stars_array[1].lower()
        if stars_text_value == 'zero':
            adapter['stars'] = 0
        elif stars_text_value == 'one':
            adapter['stars'] = 1
        elif stars_text_value == 'two':
            adapter['stars'] = 2
        elif stars_text_value == 'three':
            adapter['stars'] = 3
        elif stars_text_value == 'four':
            adapter['stars'] = 4
        elif stars_text_value == 'five':
            adapter['stars'] = 5

        return item


import mysql.connector

class SaveToMySQLPipeline:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = '',
            database = 'books'
        )

        ## Create cursor, used to execute commands
        self.cur = self.conn.cursor()

        ## Create books table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id int NOT NULL auto_increment,
            url VARCHAR(255),
            title text,
            upc VARCHAR(255),
            product_type VARCHAR(255),
            price_excl_tax DECIMAL,
            price_incl_tax DECIMAL,
            tax DECIMAL,
            price DECIMAL,
            availability INTEGER,
            number_of_reviews INTEGER,
            stars INTEGER,
            category VARCHAR(255),
            description text,
            PRIMARY KEY (id)
        )
        """)

    def process_item(self, item, spider):
        print("Item data:", item)

        ## Define insert statement
        self.cur.execute(""" insert into books (
            url,
            title,
            upc,
            product_type,
            price_excl_tax,
            price_incl_tax,
            tax,
            price,
            availability,
            number_of_reviews,
            stars,
            category,
            description
        ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (
            item.get('url'),
            item.get('title'),
            item.get('upc'),
            item.get('product_type'),
            item.get('price_excl_tax'),
            item.get('price_incl_tax'),
            item.get('tax'),
            item.get('price'),
            item.get('availability'),
            item.get('number_of_reviews'),
            item.get('stars'),
            item.get('category'),
            str(item.get("description")[0])
        ))

        # ## Execute insert of data into database
        self.conn.commit()
        return item


    def close_spider(self, spider):

        ## Close cursor
        self.cur.close()

        ## Close connection
        self.conn.close()            
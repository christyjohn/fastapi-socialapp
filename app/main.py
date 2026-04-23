from typing import Optional

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

import time
import psycopg
from psycopg.rows import dict_row

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

while True:
    try:
        # Connect to an existing database
        conn = psycopg.connect(host='localhost', dbname='fastapi_socialapp',
                                user='postgres', password='admin',
                                row_factory=dict_row)
        # Open a cursor to perform database operations
        cursor = conn.cursor()
        print('Database conection was successful!!!')
        break
    except Exception as error:
        print('Connecting to the database failed.')
        print("Error: ", error)
        time.sleep(2)

my_posts = [
    { "title": "title of post 1", "content": "content of post 1", "id": 1},
    { "title": "favorite foods", "content": "I like pizza", "id": 2}
    ]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.get("/")
def root():
    return {"message": "Welcome to my FastAPI API!!!"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}

@app.post("/posts", status_code = status.HTTP_201_CREATED)
def create_post(post: Post):
    # print(post.model_dump())
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0, 10000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts) - 1]
    return { "detail": post }

@app.get("/posts/{id}")
def get_post(id: int, respone: Response):
    # print(type(id))
    post = find_post(id)
    if not post:
        # respone.status_code = status.HTTP_404_NOT_FOUND
        # return { 'message': f"post with {id} was not found."}
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, 
                            detail = f"post with {id} was not found.")
    return { "post_detail": post }

@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response):
    # deleting post
    # find the index inthe list that has required ID
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                           detail = f"post with {id} does not exit." )
                            
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                           detail = f"post with {id} does not exit." )
    
    post_dict = post.model_dump()
    post_dict['id'] = id
    my_posts[index] = post_dict
    
    return { "data" : post_dict }
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database_modified import SessionLocal
from schema import UserGet, PostGet, FeedGet
from table_feed import Feed
from table_post import Post
from table_user import User

app = FastAPI()


def get_db():
    with SessionLocal() as db:
        return db


@app.get("/user/{id}", response_model=UserGet)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    result = db.query(User).filter(User.id == id).all()
    if not result:
        raise HTTPException(status_code=404, detail=f"User with id = {id} not found")
    else:
        return result[0]


@app.get("/post/{id}", response_model=PostGet)
def get_post_by_id(id: int, db: Session = Depends(get_db)):
    result = db.query(Post).filter(Post.id == id).all()
    if not result:
        raise HTTPException(status_code=404, detail=f"Post with id = {id} not found")
    else:
        return result[0]


@app.get("/user/{id}/feed", response_model=List[FeedGet])
def get_user_by_id(id: int, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Feed).filter(Feed.user_id == id).order_by(Feed.time.desc()).limit(limit).all()


@app.get("/post/{id}/feed", response_model=List[FeedGet])
def get_post_by_id(id: int, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Feed).filter(Feed.post_id == id).order_by(Feed.time.desc()).limit(limit).all()


@app.get("/post/recommendations/", response_model=List[PostGet]
         )
def get_post_by_id(limit: int = 10, db: Session = Depends(get_db)):

    subquery = (
        select(Feed.post_id)
        .filter(Feed.action == 'like')
        .group_by(Feed.post_id)
        .order_by(func.count(Feed.post_id).desc())
        .limit(limit)
        .subquery()
    )
    query = db.query(Post).filter(Post.id.in_(select(subquery))).all()

    return query

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Book(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=101)


@app.get("/")
def read_api(db: Session = Depends(get_db)):
    return db.query(models.Books).all()


@app.get("/{id}")
def read_id(id: int, db: Session = Depends(get_db)):
    book_model = db.query(models.Books).filter(models.Books.id == id).first()
    if book_model is None:
        raise HTTPException(
            status_code=404,
            detail=f'ID {id} not found'
        )
    return book_model


@app.post("/")
def create_book(book: Book, db: Session = Depends(get_db)):

    book_model = models.Books()
    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating

    db.add(book_model)
    db.commit()
    return book


@app.put("/modify")
def modify_api(id: int, book: Book, db: Session = Depends(get_db)):
    book_model = db.query(models.Books).filter(models.Books.id == id).first()
    if book_model is None:
        raise HTTPException(
            status_code=404,
            detail=f'ID {id} not found'
        )
    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating

    db.add(book_model)
    db.commit()
    return book


@app.delete("/")
def delete_all(db: Session = Depends(get_db)):
    db.query(models.Books).delete()
    db.commit()



@app.delete("/{id}")
def delete_id(id: int, db: Session = Depends(get_db)):
    book_model = db.query(models.Books).filter(models.Books.id == id).first()
    if book_model is None:
        raise HTTPException(
            status_code=404,
            detail=f'ID {id} not found'
        )
    db.query(models.Books).filter(models.Books.id == id).delete()
    db.commit()

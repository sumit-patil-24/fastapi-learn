from fastapi import FastAPI

app=FastAPI()

@app.get('/')
def first():
    return {"list":{"name":"sumit"}}
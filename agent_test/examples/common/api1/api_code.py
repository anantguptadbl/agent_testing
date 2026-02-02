from fastapi import FastAPI, Query
import uvicorn

app = FastAPI()

@app.post("/api1/getdata1")
def get_data1(input: str = Query(...)):
	return {'role': 'api1', 'content': 'hello'}

if __name__ == "__main__":   
	uvicorn.run(app, host="0.0.0.0", port=8004)

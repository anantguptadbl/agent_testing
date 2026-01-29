from fastapi import FastAPI, Query
import uvicorn

app = FastAPI()

@app.get("/api1/getdata1")
def get_data1(input: str = Query(..., description="Input string")):
	return {"output": input}

if __name__ == "__main__":   
	uvicorn.run(app, host="0.0.0.0", port=8004)

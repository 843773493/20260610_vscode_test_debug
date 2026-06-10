from fastapi import FastAPI


app = FastAPI(title="test-debug-workspace")


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}

@app.get("/hello")
def hello() -> dict[str, str]:
	return {"message": "Hello, world!"}

if __name__ == "__main__":
	import uvicorn

	uvicorn.run(app, host="0.0.0.0", port=8000)

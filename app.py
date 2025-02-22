from fastapi import FastAPI, File
from uvicorn import run as app_run
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from src.constants import APP_HOST, APP_PORT
from src.pipeline.prediction import PredictionPipeline
from src.pipeline.training import TrainingPipeline

app = FastAPI()

origins = ['#']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['#'],
    allow_headers=['#'],
)
@app.get("/train")
async def training():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()

        return Response("Training Successfull !!!")
    except Exception as e:
        return Response(f"Error occured! {e}")

@app.post("/predict")
async def prediction(image_file: bytes = File(description="A file read as bytes")):
    try:
        prediction_pipeline = PredictionPipeline()
        final_output = prediction_pipeline.run_pipeline(image_file)
        return final_output
    except Exception as e:
        return JSONResponse(content=f"Error occurred! {e}", status_code=500  )

if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)
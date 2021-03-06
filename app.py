import flask
import os
from flask import Flask
from flask import render_template
from PIL import Image
from core import DogBreedDetector, DogDetector, HumanDetector, WikiClient, DogBreedPredictor, DogBreedResultsBuilder

import io
import base64

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route("/predict", methods=["POST"])
def predict():
    data = {"success": False}
    input_model, dog_breed_model = DogBreedDetector().load_models()
    dog_model = DogDetector().load_model()
    human_model = HumanDetector().load_model()
    wiki_client = WikiClient()
    predictor = DogBreedPredictor(dog_model, dog_breed_model, input_model, human_model)

    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            image = flask.request.files["image"].read()
            image = Image.open(io.BytesIO(image))

            # Get predictions
            data["predictions"] = predictor.predict(image)
            data["success"] = data["predictions"] is not None

            if data["predictions"]:
                # Build result set 
                result_builder = DogBreedResultsBuilder(data['predictions'], wiki_client)
                data['result'] = result_builder.build()

            # Save in memory current uploaded photo for later preview
            img_io = io.BytesIO()
            image.save(img_io, 'PNG', quality=100)
            img_io.seek(0)

            data['image'] = base64.b64encode(img_io.getvalue()).decode('ascii')

    return render_template('index.html', data=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


# Import data manipulation libraries
import numpy as np
import pandas as pd

# For serialization
import joblib

# Flask API
from flask import Flask, request, jsonify

# Import logging
import logging
import sys

# Initialize the Flask app
superkart_api = Flask("superkart_sales_app")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

logger.info(f"Module name: {__name__}")
logger.info(f"Flask app name: {superkart_api.name}")
logger.info(f"Root path: {superkart_api.root_path}")

# Load the trained sales prediction model
model = joblib.load("superkart_model.joblib")

# Feature columns expected by the trained model
BATCH_FEATURE_COLUMNS = [
    'Product_Weight',
    'Product_Sugar_Content',
    'Product_Allocated_Area',
    'Product_MRP',
    'Store_Size',
    'Store_Location_City_Type',
    'Store_Type',
    'Product_Id_char',
    'Store_Age_Years',
    'Product_Type_Category'
]

# Define a route for the home page
@superkart_api.route('/', methods=['GET'])
def home():
    """
    Handles GET requests to the root URL ('/').
    Returns a welcome message and information about the API endpoints.
    """
    logger.info("Home endpoint accessed")

    html = """
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SuperKart Sales API</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
          * { box-sizing: border-box; }

          body {
            margin: 0;
            min-height: 100vh;
            font-family: "DM Sans", sans-serif;
            color: #1e293b;
            background:
              radial-gradient(900px 480px at 8% -10%, rgba(125, 211, 252, 0.55), transparent 55%),
              radial-gradient(820px 460px at 96% 4%, rgba(196, 181, 253, 0.50), transparent 52%),
              radial-gradient(700px 420px at 50% 110%, rgba(167, 243, 208, 0.45), transparent 50%),
              linear-gradient(180deg, #f8fbff 0%, #eef4ff 45%, #f7f3ff 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 32px 20px;
          }

          .wrap {
            width: min(720px, 100%);
          }

          .hero {
            background: rgba(255, 255, 255, 0.42);
            border: 1px solid rgba(255, 255, 255, 0.72);
            border-radius: 24px;
            padding: 36px 32px 28px;
            box-shadow: 0 18px 50px rgba(148, 163, 184, 0.18);
            backdrop-filter: blur(22px);
            -webkit-backdrop-filter: blur(22px);
            margin-bottom: 16px;
          }

          .eyebrow {
            letter-spacing: 0.14em;
            text-transform: uppercase;
            font-size: 12px;
            font-weight: 600;
            color: #0284c7;
            margin-bottom: 10px;
          }

          h1 {
            margin: 0 0 10px;
            font-size: 34px;
            line-height: 1.2;
            color: #0f172a;
          }

          .lead {
            margin: 0;
            color: #475569;
            font-size: 16px;
            line-height: 1.65;
          }

          .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
          }

          .card {
            background: rgba(255, 255, 255, 0.48);
            border: 1px solid rgba(255, 255, 255, 0.78);
            border-radius: 18px;
            padding: 18px 18px 16px;
            box-shadow: 0 10px 28px rgba(148, 163, 184, 0.12);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
          }

          .label {
            color: #64748b;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
          }

          code {
            display: inline-block;
            margin-top: 6px;
            padding: 4px 8px;
            border-radius: 8px;
            background: rgba(224, 242, 254, 0.8);
            color: #0369a1;
            font-size: 14px;
          }

          p {
            margin: 0;
            color: #1e293b;
            line-height: 1.55;
          }

          @media (max-width: 640px) {
            .grid { grid-template-columns: 1fr; }
            h1 { font-size: 28px; }
          }
        </style>
      </head>
      <body>
        <main class="wrap">
          <section class="hero">
            <div class="eyebrow">Retail forecasting</div>
            <h1>SuperKart Sales API</h1>
            <p class="lead">
              JSON for a single store-product estimate, or a CSV for a full batch.
              Both routes return predicted sales from the trained model.
            </p>
          </section>

          <section class="grid">
            <article class="card">
              <div class="label">Single prediction</div>
              <p>Send a JSON body with product and store features.</p>
              <code>POST /v1/predict</code>
            </article>
            <article class="card">
              <div class="label">Batch prediction</div>
              <p>Upload a CSV using the <strong>file</strong> form field.</p>
              <code>POST /v1/predictbatch</code>
            </article>
          </section>
        </main>
      </body>
      </html>
    """

    return html

# Define an endpoint to predict sales for a single product
@superkart_api.route('/v1/predict', methods=['POST'])
def predict_sales():
    """
    Handles POST requests to /v1/predict.
    Accepts JSON input containing the required product and store features
    and returns the predicted sales value.
    """
    try:
        # Get JSON data from the request body
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Request body must contain valid JSON'
            }), 400

        # Prepare input using the exact feature names expected by the model
        sample = {
            'Product_Weight': data['Product_Weight'],
            'Product_Sugar_Content': data['Product_Sugar_Content'],
            'Product_Allocated_Area': data['Product_Allocated_Area'],
            'Product_MRP': data['Product_MRP'],
            'Store_Size': data['Store_Size'],
            'Store_Location_City_Type': data['Store_Location_City_Type'],
            'Store_Type': data['Store_Type'],
            'Store_Age_Years': data['Store_Age_Years'],
            'Product_Type_Category': data['Product_Type_Category'],
            'Product_Id_char': data['Product_Id_char']
        }

        # Convert input to DataFrame
        input_data = pd.DataFrame([sample])

        # Generate prediction
        prediction = model.predict(input_data).tolist()[0]

        logger.info("Sales prediction generated successfully")

        return jsonify({
            'Sales': prediction
        })

    except KeyError as e:
        logger.warning("Missing required field: %s", e)

        return jsonify({
            'error': f'Missing key: {str(e)}'
        }), 400

    except Exception:
        logger.exception("Prediction failed")

        return jsonify({
            'error': 'Prediction failed'
        }), 500

# Define an endpoint for batch sales predictions
@superkart_api.route('/v1/predictbatch', methods=['POST'])
def predict_batch():
    """
    Handles POST requests to /v1/predictbatch.
    Accepts a CSV file containing all required model features
    and returns sales predictions for each row.
    """
    try:
        # Check that a file was included in the request
        if 'file' not in request.files:
            return jsonify({
                'error': 'CSV file is required. Use the "file" field.'
            }), 400

        file = request.files['file']

        # Check that a file was actually provided
        if not file or file.filename == '':
            return jsonify({
                'error': 'No CSV file was provided.'
            }), 400

        # Read the uploaded CSV file into a DataFrame
        batch_data = pd.read_csv(file)

        # Check for missing required feature columns
        missing_columns = [
            column
            for column in BATCH_FEATURE_COLUMNS
            if column not in batch_data.columns
        ]

        if missing_columns:
            return jsonify({
                'error': 'CSV is missing required feature columns.',
                'missing_columns': missing_columns
            }), 400

        # Select only the columns expected by the model
        input_data = batch_data[BATCH_FEATURE_COLUMNS]

        # Generate predictions for all rows
        predictions = model.predict(input_data).tolist()

        logger.info(
            "Batch prediction generated successfully for %d rows",
            len(input_data)
        )

        return jsonify({
            str(index): prediction
            for index, prediction in enumerate(predictions)
        })

    except pd.errors.EmptyDataError:
        logger.warning("Batch prediction failed: CSV file is empty")

        return jsonify({
            'error': 'The CSV file is empty.'
        }), 400

    except pd.errors.ParserError:
        logger.warning("Batch prediction failed: Invalid CSV format")

        return jsonify({
            'error': 'Unable to parse the CSV file. Please provide a valid CSV.'
        }), 400

    except Exception:
        logger.exception("Batch prediction failed")

        return jsonify({
            'error': 'Batch prediction failed'
        }), 500

# Run the Flask app
if __name__ == '__main__':
    superkart_api.run(
        debug=True
    )

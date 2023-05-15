import os
import logging
from logging import StreamHandler
from waitress import serve
from flask import Flask, request, jsonify, send_from_directory
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

NEWS_API_URL = 'https://newsapi.org/v2/everything'
NEWS_API_KEY = os.environ['NEWS_API_KEY']

# Remove default logger handler
app.logger.handlers.clear()

# Add custom logging handler for Replit
handler = StreamHandler()
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Log when the application starts
app.logger.info("Application started")


def get_news(topic, from_date, to_date):
  params = {
    'q': topic,
    'from': from_date,
    'to': to_date,
    'sortBy': 'popularity',
    'apiKey': NEWS_API_KEY
  }
  response = requests.get(NEWS_API_URL, params=params)

  if response.status_code == 200:
    return response.json()
  else:
    raise Exception(f"Error: {response.status_code}, {response.text}")


@app.route('/news', methods=['GET'])
def fetch_news():
  app.logger.info("Fetching news")
  topic = request.args.get('topic')
  from_date = request.args.get('date_from',
                               datetime.now().strftime('%Y-%m-%d'))
  to_date = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))

  try:
    news = get_news(topic, from_date, to_date)
    return jsonify(news)
  except Exception as e:
    return jsonify({"error": str(e)}), 400


@app.route('/.well-known/ai-plugin.json')
def serve_ai_plugin():
  app.logger.info("Serving ai-plugin.json")
  return send_from_directory('.',
                             'ai-plugin.json',
                             mimetype='application/json')


@app.route('/.well-known/openapi.yaml')
def serve_openapi_yaml():
  app.logger.info("Serving openapi.yaml")
  return send_from_directory('.', 'openapi.yaml', mimetype='text/yaml')


if __name__ == '__main__':
  serve(app, host="0.0.0.0", port=8080)

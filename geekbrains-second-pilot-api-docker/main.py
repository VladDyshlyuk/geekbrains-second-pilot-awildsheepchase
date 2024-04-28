
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer

from sklearn.decomposition import PCA
from sklearn.metrics import DistanceMetric

from flask import Flask, jsonify, request
from threading import Thread

df_q_a = pd.read_csv('train_ds.csv')

model = SentenceTransformer("distiluse-base-multilingual-cased-v1")

#encode questions
embedding_arr = model.encode(df_q_a['Question'])



# Fit PCA on your full embeddings
pca_full = PCA()
pca_full.fit(embedding_arr)  # Assuming 'question_embeddings' contains all your data

# Explained variance ratio for each component
explained_variance = pca_full.explained_variance_ratio_

cumulative_explained_variance = np.cumsum(explained_variance)

# Define a threshold for cumulative explained variance
variance_threshold = 0.94

# Find the number of components that explain at least this threshold of variance
n_components = np.where(cumulative_explained_variance >= variance_threshold)[0][0] + 1

pca = PCA(n_components=n_components).fit(embedding_arr)


app = Flask('api')
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/ask', methods=['GET'])
def get_query_json():
    query = request.args.get('query').replace('"', '')
    # Get query embedding
    query_embedding = model.encode(query)

    # Define distance metric
    dist = DistanceMetric.get_metric('euclidean')  # or 'manhattan', 'chebyshev'

    # Compute pairwise distances between query embedding and all embeddings in the array
    dist_arr = dist.pairwise(embedding_arr, query_embedding.reshape(1, -1)).flatten()

    # Get index of the sorted distances
    idist_arr_sorted = np.argsort(dist_arr)

    # # Get the smallest distance (closest match)
    # closest_distance = dist_arr[idist_arr_sorted[0]]

    # # Calculate confidence using exponential decay
    # confidence = np.exp(-closest_distance)
    # if (confidence >= 85):
    #       action = 0
    # else:
    #       if ((confidence < 85) and (confidence >= 70)) or (confidence < 10):
    #         action = 1
    #       else:
    #         action = 2

    # Retrieve the answer class of the closest match
    answer_class = df_q_a['answer_class'].iloc[idist_arr_sorted[0]]
    question = df_q_a['Question'].iloc[idist_arr_sorted[0]]
    answer = df_q_a['Answer'].iloc[idist_arr_sorted[0]]


    response = {
          "query": query,
          "similar_question": question,
          "answer_class": float(answer_class),
          "answer_text": answer,
          # "score": float(confidence),
          # "action": action
      }

    return jsonify(response)

@app.route('/clarify', methods=['GET'])
def clarify_question(): #return 5 similar questions
    query = request.args.get('question').replace('"', '')
     # Get query embedding
    query_embedding = model.encode(query)

    # Define distance metric
    dist = DistanceMetric.get_metric('euclidean')  # or 'manhattan', 'chebyshev'

    # Compute pairwise distances between query embedding and all embeddings in the array
    dist_arr = dist.pairwise(embedding_arr, query_embedding.reshape(1, -1)).flatten()

    # Get index of the sorted distances
    idist_arr_sorted = np.argsort(dist_arr)
    print(df_q_a['Question'].iloc[idist_arr_sorted[:5]])

    # Selecting top 5 questions using iloc and indices array
    selected_questions = df_q_a['Question'].iloc[idist_arr_sorted[:5]]

    # Convert to JSON array
    json_array = selected_questions.to_json(orient='values', force_ascii=False )

    return jsonify(json_array)


def run_flask():
    app.run(host='0.0.0.0')

# Using a thread to run Flask so the executing cell doesn't block
thread = Thread(target=run_flask)
thread.start()

FROM python:3.10.12

# Set the working directory in the container
WORKDIR /

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Download the model during image build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('distiluse-base-multilingual-cased-v1')"

# Copy the rest of your application's code
COPY . .

EXPOSE 5000
# Run the application
CMD ["python", "main.py"]
# Variables
IMAGE_NAME=reyshazni/gdp-demo-weather-be

# Run the backend locally (requires Python and dependencies installed locally)
run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Build the Docker image for linux/amd64 architecture
dbuild:
	docker buildx build --platform linux/amd64 -t $(IMAGE_NAME) .

# Run the Docker container for the backend
drun:
	docker run --platform linux/amd64 -dp 8000:8000 $(IMAGE_NAME)

# Push the Docker image to the repository
dpush:
	docker push $(IMAGE_NAME)

install:
	pip install -r requirements.txt
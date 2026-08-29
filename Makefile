.PHONY: install run test fetch docker-build docker-run clean

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip -q && pip install -r requirements.txt -q

run:
	streamlit run app.py

test:
	pip install -q pytest
	pytest -q

fetch:
	python3 live_fetch.py

docker-build:
	docker build -t mpg-mobile-play-genre-metrics .

docker-run:
	docker run -p 8501:8501 mpg-mobile-play-genre-metrics

clean:
	rm -rf __pycache__ .pytest_cache .venv

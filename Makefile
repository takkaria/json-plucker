.PHONY: test
test:
	pytest --cov=src --cov-report html --cov-report term


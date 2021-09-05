
all: build push

clean:
	rm -rf ./comic_html_view_generator.egg-info
	rm -rf ./build/
	rm -rf ./dist/

.PHONY: push
push: build
	twine upload dist/*

.PHONY: build
build:
	poetry build

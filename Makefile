all: build

clean:
	@rm -rf README.pdf

build: README.md
	pandoc -V colorlinks=true -V linkcolor=blue -V urlcolor=blue -V toccolor=gray README.md -o README.pdf

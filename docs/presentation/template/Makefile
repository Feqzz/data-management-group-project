CC=pdflatex
.PHONY: build

all: build

clean:
	@rm -rf *.snm *.run.xml *.bcf *.aux *.log *.out *.pdf *.toc *.nav

build: main.tex
	$(CC) $< 

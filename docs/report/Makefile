.PHONY: build clean

all: build

clean:
	@rm -rf *.bbl *.blg *.run.xml *.bcf *.aux *.log *.out *.pdf *.toc chapters/*.aux configuration/*.aux

build: main.tex
	pdflatex $< && biber main && pdflatex $<

.PHONY: build clean report
NAME=CS4010ProjectAutumn21_8009_8011_8017

all: build

clean:
	@rm -rf *.bbl *.blg *.run.xml *.bcf *.aux *.log *.out *.pdf *.toc chapters/*.aux configuration/*.aux

build: main.tex
	pdflatex $< && biber main && pdflatex $<

report: main.tex
	pdflatex --jobname=$(NAME) $< && biber $(NAME) && pdflatex --jobname=$(NAME) $<

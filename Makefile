NAME    := Thu.5.Lihm
PDF     := $(NAME).pdf
TAR     := $(NAME).tar
SRC_PDF := document/main.pdf
SRC_DIR := code

.PHONY: all pdf tar clean

all: pdf tar

pdf: $(PDF)

$(PDF): $(SRC_PDF)
	cp $(SRC_PDF) $(PDF)

$(SRC_PDF): document/main.tex document/settings.tex
	cd document && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex

tar: $(TAR)

$(TAR):
	ln -sfn $(SRC_DIR) $(NAME)
	tar --exclude='.DS_Store' -chf $(TAR) $(NAME)
	rm -f $(NAME)

clean:
	rm -f $(PDF) $(TAR)

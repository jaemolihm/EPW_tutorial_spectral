NAME    := Thu.5.Lihm
PDF     := $(NAME).pdf
TAR     := $(NAME).tar
SRC_PDF := document/main.pdf
SRC_DIR := code

GDRIVE_REMOTE    := gdrive_EPW2026:
GDRIVE_FOLDER_ID := REDACTED

FRONTERA_HOST := jmlihm@frontera.tacc.utexas.edu
FRONTERA_DEST := ~/

.PHONY: all pdf tar push frontera clean

all: pdf tar push

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

push: $(PDF) $(TAR)
	rclone copy --drive-root-folder-id $(GDRIVE_FOLDER_ID) $(PDF) $(GDRIVE_REMOTE) -v
	rclone copy --drive-root-folder-id $(GDRIVE_FOLDER_ID) $(TAR) $(GDRIVE_REMOTE) -v

frontera: $(TAR)
	scp $(TAR) $(FRONTERA_HOST):$(FRONTERA_DEST)

clean:
	rm -f $(PDF) $(TAR)

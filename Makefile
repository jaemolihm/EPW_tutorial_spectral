NAME    := Thu.5.Lihm
PDF     := $(NAME).pdf
TAR     := $(NAME).tar
SRC_PDF := document/main.pdf
SRC_DIR := code
CODE_FILES := $(shell find $(SRC_DIR) -type f)

GDRIVE_REMOTE    := gdrive_EPW2026:
# GDRIVE_FOLDER_ID is set in Makefile.local (gitignored).

FRONTERA_HOST := jmlihm@frontera.tacc.utexas.edu
FRONTERA_DEST := ~/

-include Makefile.local

.PHONY: all pdf tar push frontera clean

all: pdf tar push

pdf: $(PDF)

$(PDF): $(SRC_PDF)
	cp $(SRC_PDF) $(PDF)

$(SRC_PDF): document/main.tex document/settings.tex
	cd document && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex

tar: $(TAR)

$(TAR): $(CODE_FILES)
	ln -sfn $(SRC_DIR) $(NAME)
	COPYFILE_DISABLE=1 tar --no-xattrs --exclude='.DS_Store' -chf $(TAR) $(NAME)
	rm -f $(NAME)

push: $(PDF) $(TAR)
	@if [ -z "$(GDRIVE_FOLDER_ID)" ]; then \
	  echo "ERROR: GDRIVE_FOLDER_ID is not set. Create Makefile.local containing:"; \
	  echo "    GDRIVE_FOLDER_ID := <your-folder-id>"; \
	  exit 1; \
	fi
	@for f in $(PDF) $(TAR); do \
	  log=$$(mktemp); \
	  rclone copy --drive-root-folder-id $(GDRIVE_FOLDER_ID) $$f $(GDRIVE_REMOTE) -v 2>&1 | tee "$$log"; \
	  if ! grep -q "$$f: Copied (replaced existing)" "$$log"; then \
	    echo ""; \
	    echo "WARNING: '$$f' — did not see 'Copied (replaced existing)' in rclone output."; \
	    echo "         The existing file on Drive may not have been overwritten in place."; \
	    echo "         Check the folder for duplicates."; \
	  fi; \
	  rm -f "$$log"; \
	done

frontera:
	rm -f $(TAR)
	$(MAKE) $(TAR)
	chmod 755 $(TAR)
	scp -p $(TAR) $(FRONTERA_HOST):$(FRONTERA_DEST)

clean:
	rm -f $(PDF) $(TAR)

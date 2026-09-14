# Ingest and build. See Docs/RUNBOOK.md for the operating procedure.
#
# fetch runs on a human's residential connection; F1's archive blocks
# datacenter IPs and returns empty bodies rather than errors.

F1DB_DIR ?= .cache/f1db
SITE     := site

.PHONY: help spine emit geo align outlines profile data build preview check banner clean

help:
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "};{printf "  %-12s %s\n", $$1, $$2}'

spine: ## Download the current F1DB release (CC BY 4.0)
	@mkdir -p $(F1DB_DIR)
	@REL=$$(curl -s https://api.github.com/repos/f1db/f1db/releases/latest \
	    | python3 -c "import sys,json;print(json.load(sys.stdin)['tag_name'])"); \
	  echo "F1DB $$REL"; \
	  curl -sL -o $(F1DB_DIR)/f1db-csv.zip \
	    "https://github.com/f1db/f1db/releases/download/$$REL/f1db-csv.zip"; \
	  cd $(F1DB_DIR) && unzip -oq f1db-csv.zip && echo "$$REL" > .release

emit: ## F1DB CSV -> canonical JSON in site/data/
	python3 pipeline/f1db_emit.py $(F1DB_DIR)

geo: ## Report which geometry source each circuit resolves to
	python3 pipeline/geo.py

align: ## Solve the TUMFTM local frame against geographic space (slow; cached)
	python3 pipeline/align.py

outlines: ## Normalised outlines from the best geometry available (length-validated)
	python3 pipeline/outlines.py

data: spine emit align outlines profile ## Full data refresh

build: ## Build the site and its search index
	cd $(SITE) && npm run build

preview: ## Serve the built site
	cd $(SITE) && npm run preview

check: ## Type check
	cd $(SITE) && npm run check

clean:
	rm -rf $(SITE)/dist $(SITE)/node_modules/.astro

banner: ## Regenerate the README banner
	python3 pipeline/banner.py

profile: ## Derive curvature profiles and corner detection
	python3 pipeline/profile.py

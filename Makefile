CACHE_DIR=var/cache
TMP_DIR=tmp/
PIPELINE=pipeline/

all:: $(TMP_DIR) $(CACHE_DIR)/organisation.csv $(PIPELINE) init

$(TMP_DIR)::
	@mkdir -p $(TMP_DIR)

$(CACHE_DIR)/organisation.csv::
	@mkdir -p $(CACHE_DIR)
	curl -qs "https://raw.githubusercontent.com/digital-land/organisation-dataset/master/collection/organisation.csv" > $@

$(PIPELINE)::
	@mkdir -p $(PIPELINE)
	cd $(PIPELINE) && \
	git init temp && \
	cd temp && \
	git remote add origin https://github.com/digital-land/brownfield-land-collection.git && \
	git config core.sparsecheckout true && \
	echo "pipeline/*" >> .git/info/sparse-checkout && \
	git pull --depth=1 origin main
	cd $(PIPELINE) && \
	mv temp/pipeline/* ./ && \
	rm -rf temp

include makerules/makerules.mk
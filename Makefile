setup:
	wget "http://nlp.stanford.edu/software/stanford-corenlp-4.0.0.zip" --no-check-certificate
	unzip -j stanford-corenlp-4.0.0.zip -d ./data/corenlp
	rm stanford-corenlp-4.0.0.zip

run-server:
	cd data/corenlp && \
	java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,ner,parse,depparse -status_port 9000 -port 9000 -timeout 30000

run-low-server:
	cd data/corenlp && \
	java -mx1g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,ner,parse,depparse -status_port 9000 -port 9000 -timeout 30000

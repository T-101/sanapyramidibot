build:
		@docker build -t sanapyramidibot .

up:
		@docker run \
		-p 127.0.0.1:8100:8100 \
		--name sanapyramidibot \
		-v .:/app \
		-d --restart unless-stopped sanapyramidibot

sh:
		@docker run -it \
		--name sanapyramidibot \
		-v .:/app \
		--rm sanapyramidibot sh

stop:
		@docker stop sanapyramidibot
		@docker rm sanapyramidibot
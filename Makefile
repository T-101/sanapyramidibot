build:
		@docker build -t sanapyramidibot .

up:
		@docker run \
		-p 127.0.0.1:8100:8100 \
		--name sanapyramidibot \
		-d --restart unless-stopped sanapyramidibot

stop:
		@docker stop sanapyramidibot
		@docker rm sanapyramidibot
### SanaPyramidiBot

Tämä Telegram-botti muistuttaa Yle:n Sanapyramidipelistä joka aamu klo 7:15

https://yle.fi/a/74-20131998

Käyttöohjeet:
1. Uudelleennimeä `config-example.toml` `config.toml`
2. Luo botti Telegrammissa ja lisää se kanaville
3. Aseta botin token ja kanava id:t
4. Muuta tarvittaessa botin portti `Makefile`:ssä
5. Rakenna botti `make build`
6. Aja botti `make up`
7. Kun haluat sammuttaa botin, `make stop`

Mikäli muutat ajoaikaa, pitää botti rakentaa uudestaan.
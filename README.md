## Instrukcja obsługi
- Pobieramy folder z plikami projektu
- W terminalu, przechodzimy do lokalizacji w której mamy folder z projektem
- Za pomocą poniższej komendy budujemy obraz Docker
```console
docker build -t ochroniarz .
```
- Następnie uruchamiamy zbudowany obraz
```console
docker run -p 8501:8501 ochroniarz
```
- W przeglądarce uruchamiamy aplikację pod zdefiniowanym wcześniej portem
- W polu tekstowym po lewej stronie wpisujemy tekst do analizy
- Po wciśnięciu przycisku "Analyze" zostanie przeanalizowany wprowadzony tekst oraz zostaną wyświetlone wyniki

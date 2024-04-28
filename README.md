
# Цифровой Прорыв 2024 ЦФО Кейс Второй пилот для куратора / специалиста поддержки

Решение кейса GeekBrains команды AWildSheepChase




## Развертывание API
Clone the project

```bash
  git clone https://github.com/VladDyshlyuk/geekbrains-second-pilot-awildsheepchase
```

Go to the project directory

```bash
  cd geekbrains-second-pilot-api
```

Docker build

```bash
  docker build -t geekbrains-secondpilot-api .
```

Run the container

```bash
  docker run -d -p 5000:5000 geekbrains-secondpilot-api
```
```bash
2024-04-28 10:25:34  * Running on all addresses (0.0.0.0)
2024-04-28 10:25:34  * Running on http://127.0.0.1:5000
2024-04-28 10:25:34  * Running on http://172.17.0.2:5000
2024-04-28 10:25:34 Press CTRL+C to quit
```

## Развертывание Бота
Clone the project

```bash
  git clone https://github.com/VladDyshlyuk/geekbrains-second-pilot-awildsheepchase
```

Go to the project directory


```bash
  cd geekbrains-second-pilot-api
```

Docker build

```bash
  docker build -t geekbrains-bot-docker .
```

Compose

Write an .env file with your TELEGRAM_TOKEN in it and other env vars.
Run docker-compose up -d and wait for the build to finish.


## Run API in Colab
Вы можете быстро запустить временный API Endpoint с помощью Googl Colab и Cloudfare Quick Tunnel. Не забудьте загрузить датасет. 
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1xWDvV-xiXLfbSfDK5PC9YXHpOqii6KHM?usp=sharing/)

## Run Bot in Colab
Вы также можете запустить бота с помощью Colab и Endpoint выше. Не забудьте изменить Credentials для Telegram Bot API. 
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)

##Прочие использовавшиеся вариации ноутбуков находятся в папке notebooks

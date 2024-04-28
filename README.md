
# Цифровой Прорыв 2024 ЦФО Кейс Второй пилот для куратора / специалиста поддержки

Решение кейса GeekBrains команды AWildSheepChase




## Развертывание API
Clone the project

```bash
  git clone https://github.com/VladDyshlyuk/geekbrains-second-pilot-awildsheepchase
```

Go to the project directory

```bash
  cd my-project
```

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
#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Начинаем настройку сервера...${NC}"

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "Docker не найден. Устанавливаем..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo -e "${GREEN}Docker установлен.${NC}"
else
    echo -e "${GREEN}Docker уже установлен.${NC}"
fi

# Проверка наличия Docker Compose (плагин)
if ! docker compose version &> /dev/null; then
    echo "Docker Compose плагин не найден. Пробуем установить..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    if ! docker compose version &> /dev/null; then
         echo "Не удалось установить плагин. Пробуем старый docker-compose..."
         sudo apt-get install -y docker-compose
    fi
fi

# Остановка контейнера и обновление
echo -e "${GREEN}Останавливаем контейнер и обновляем код...${NC}"
docker compose stop daily_budget_bot || true
git pull

# Создание .env если нет
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "Создаем .env из примера..."
        cp .env.example .env
        echo -e "${GREEN}Файл .env создан. Пожалуйста, отредактируйте его и вставьте токен бота!${NC}"
        echo "Для редактирования используйте команду: nano .env"
        exit 1
    else
        echo "Ошибка: не найден файл .env.example"
        exit 1
    fi
fi

# Запуск
echo -e "${GREEN}Запускаем бота...${NC}"
docker compose up -d --build

echo -e "${GREEN}Готово! Бот запущен в фоне.${NC}"
echo "Просмотр логов: docker compose logs -f"

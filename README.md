# Мой Python проект

Простой Python проект для демонстрации работы с GitHub.

## Описание

Этот проект содержит базовый Python скрипт, который выводит приветствие.

## Установка и запуск

```bash
python main.py
```

## Инструкции для завершения настройки GitHub

### 1. Завершить первый коммит

В терминале Git Bash выполните:

```bash
cd git
git commit -m "Initial commit: добавлен main.py и .gitignore"
```

### 2. Создать репозиторий на GitHub

1. Перейдите на [GitHub.com](https://github.com)
2. Нажмите кнопку "New repository" (зеленая кнопка)
3. Введите название репозитория (например, `my-python-project`)
4. Добавьте описание (опционально)
5. Выберите "Public" или "Private"
6. **НЕ** добавляйте README, .gitignore или лицензию (они уже есть локально)
7. Нажмите "Create repository"

### 3. Связать локальный репозиторий с GitHub

После создания репозитория на GitHub, выполните команды (замените `USERNAME` на ваш GitHub username):

```bash
git remote add origin https://github.com/USERNAME/my-python-project.git
git branch -M main
git push -u origin main
```

### 4. Альтернативный способ через SSH (если настроен SSH ключ)

```bash
git remote add origin git@github.com:USERNAME/my-python-project.git
git branch -M main
git push -u origin main
```

### 5. Проверка

После успешного push'а ваш код будет доступен на GitHub по адресу:
`https://github.com/USERNAME/my-python-project`

## Дальнейшая работа

Для добавления изменений в будущем:

```bash
git add .
git commit -m "Описание изменений"
git push
```

## Автор

ostroverkhii
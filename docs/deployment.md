# Запуск и развёртывание

В файле две инструкции: как запустить проект на своём компьютере и как опубликовать его на Render. Команды написаны для PowerShell.

Сайт: https://database-pz8-django-project.onrender.com



## Часть 1. Запуск на компьютере

Нужны Python 3.12 и Git.

1. Скачайте проект и проверьте, что скачалось всё:

```
git clone https://github.com/informatics317/Database\_PZ8\_django\_project.git django\_auth
   cd django\_auth
   dir
   ```

   Если Git пишет `already exists and is not an empty directory`, такая папка уже есть. Клонируйте под другим именем (например `django\_auth\_new`) или переименуйте старую папку.



2. Создайте виртуальное окружение и установите библиотеки:

```
python -m venv .venv
   .\\.venv\\Scripts\\Activate.ps1
   pip install -r requirements.txt
   ```



3. Задайте переменные окружения:

```
$env:DJANGO\_SECRET\_KEY = "local-secret-key-for-learning"
   $env:DJANGO\_DEBUG = "True"
   $env:DJANGO\_ALLOWED\_HOSTS = "127.0.0.1,localhost"
   ```

   `DATABASE\_URL` не задаём: тогда используется SQLite.



4. Создайте таблицы, администратора и запустите сайт:

```
python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

   Сайт откроется на http://127.0.0.1:8000/.



5. Добавьте тестовые данные в админ-панели (`/admin/`): группу «Методист», категории заявок, оборудование (проектор 3, компьютер 10, микрофон 5) и двух пользователей (студент и методист в группе «Методист»).
6. Проверьте работу по разделу «Проверка» в [README.md](../README.md).



## Часть 2. Развёртывание на Render

Нужны только бесплатные услуги: PostgreSQL и Web Service.

### Какие бывают процессы



|**Процесс**|**Что происходит**|**Как запускается**|
|-|-|-|
|Сборка|Ставятся библиотеки и собирается статика (`build.sh`)|Сама, при каждом деплое|
|Миграции|Создаются таблицы в базе|Вручную, с компьютера|
|Запуск сервера|Gunicorn запускает сайт|Сам, после сборки|
|Проверка|Открываем `/healthz/` и входим на сайт|Вручную|

Миграции в `build.sh` не запускаются. Их нужно сделать отдельно, иначе будет ошибка «relation does not exist».



### 1\. База PostgreSQL

1. В Render выберите **New → PostgreSQL**, тариф Free, запомните регион.
2. Когда база будет готова, на её странице появятся два адреса:

   * **Internal Database URL** – для сайта на Render;
   * **External Database URL** – для миграций с компьютера.

В адресах есть пароль, их нельзя показывать.



### 2\. Web Service

1. **New → Web Service**, выберите репозиторий и ветку `main`.
2. Укажите команды:

|**Поле**|**Значение**|
|-|-|
|Build Command|`bash build.sh`|
|Start Command|`gunicorn config.wsgi:application`|

3. Тариф Free, регион тот же, что у базы.



### 3\. Переменные окружения

В разделе **Environment** добавьте пять переменных:

|**Переменная**|**Для чего**|**Значение**|
|-|-|-|
|`DJANGO\_SECRET\_KEY`|Секретный ключ Django|Длинная случайная строка|
|`DJANGO\_DEBUG`|Режим отладки|`False`|
|`DJANGO\_ALLOWED\_HOSTS`|Адрес сайта без `https://`|`database-pz8-django-project.onrender.com`|
|`DJANGO\_CSRF\_TRUSTED\_ORIGINS`|Адрес сайта с `https://`|`https://database-pz8-django-project.onrender.com`|
|`DATABASE\_URL`|Адрес базы данных|**Internal Database URL**|

Internal Database URL нужен потому, что сайт и база находятся на Render в одной сети. Вставляйте его только на сайте Render, в Git его записывать нельзя.



### 4\. Сборка

После сохранения Render сам соберёт и запустит сайт. Ход виден в разделе **Logs**. Сайт готов, когда статус стал **Live**.



### 5\. Миграции

Выполните один раз с компьютера, временно подставив **External Database URL**:

```
.\\.venv\\Scripts\\Activate.ps1
$env:DJANGO\_SECRET\_KEY = "any-value-for-migration"
$env:DATABASE\_URL = "<External Database URL из Render>"
python manage.py migrate
python manage.py createsuperuser
Remove-Item Env:DATABASE\_URL
```

* Вместо `<External Database URL из Render>` вставьте настоящий адрес. Нигде его не публикуйте.
* В конце `migrate` у всех строк должно быть `OK`.
* Администратор нужен, потому что пользователи из локальной базы в облако не переносятся.
* Последняя команда убирает адрес, чтобы случайно не работать с облачной базой.



### 6\. Данные

Облачная база пустая. Зайдите в `/admin/` на сайте и добавьте группу «Методист», категории, оборудование и пользователей.

Локальная SQLite и облачная PostgreSQL – две разные базы. Данные между ними сами не переносятся.



### 7\. Проверка

1. `/healthz/` отвечает `{"status": "ok"}`.
2. На `/accounts/login/` можно войти, страница оформлена.
3. На `/bookings/` виден список оборудования и можно создать бронь.
4. Если что-то не работает, смотрите **Logs** и файл [troubleshooting.md](troubleshooting.md).



### Обновление сайта

Сделайте `git add`, `git commit` и `git push` в ветку `main`. Render сам пересоберёт сайт. Если менялись модели, снова выполните миграции (пункт 5).

Бесплатный сервис «засыпает», поэтому первый запрос после паузы идёт около минуты.


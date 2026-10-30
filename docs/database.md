# База данных

Таблицы создаются командой `python manage.py migrate`. 



#### Схема связей

**Заявки и бронирование:**

```
mermaid
erDiagram
    CATEGORY ||--o{ TICKET : category
    USER ||--o{ TICKET : owner
    USER ||--o{ BOOKING : owner
    EQUIPMENT ||--o{ BOOKING : equipment
    BOOKING ||--o{ BOOKINGEVENT : booking
    USER ||--o{ BOOKINGEVENT : actor
    CATEGORY {
        int id PK
        string name
    }
    TICKET {
        int id PK
        string title
        string status
    }
    EQUIPMENT {
        int id PK
        string name
        int total
        int available
    }
    BOOKING {
        int id PK
        int quantity
        string purpose
        string status
    }
    BOOKINGEVENT {
        int id PK
        string action
    }
```

**Учебный портал:**

```
mermaid
erDiagram
    DEPARTMENT ||--o{ ACADEMICGROUP : department
    DEPARTMENT ||--o{ COURSE : department
    DEPARTMENT ||--o{ STUDENTPROFILE : department
    ACADEMICGROUP ||--o{ STUDENTPROFILE : academic_group
    USER ||--o| STUDENTPROFILE : user
    STUDENTPROFILE }o--o{ COURSE : courses
```

Как читать: `||--o{` – «один ко многим», `||--o|` – «один к одному», `}o--o{` – «многие ко многим».



## Заявки (tickets)

|**Модель**|**Главные поля**|**Связи**|
|-|-|-|
|`Category` (категория)|`id`, `name`|У категории много заявок|
|`Ticket` (заявка)|`id`, `title`, `description`, `status` (`new`, `progress`, `done`), `created_at`|`category` (нельзя удалить категорию с заявками), `owner` (автор заявки)|



## Бронирование (bookings)

|**Модель**|**Главные поля**|**Связи**|
|-|-|-|
|`Equipment` (оборудование)|`id`, `name`, `total` (всего), `available` (свободно)|У оборудования много броней|
|`Booking` (бронь)|`id`, `quantity`, `purpose`, `status` (`created`, `confirmed`, `completed`, `cancelled`), `created_at`|`equipment` (нельзя удалить оборудование с бронями), `owner` (кто забронировал)|
|`BookingEvent` (история)|`id`, `action`, `created_at`|`booking` (к какой брони относится), `actor` (кто сделал действие)|



## Учебный портал (accounts)

|**Модель**|**Главные поля**|**Связи**|
|-|-|-|
|`Department` (подразделение)|`id`, `name`|У него много курсов, групп и студентов|
|`Course` (курс)|`id`, `title`, `description`|Принадлежит подразделению|
|`AcademicGroup` (группа)|`id`, `name`|Принадлежит подразделению|
|`StudentProfile` (профиль студента)|`id`|Один к одному с `User`; необязательные подразделение и группа; много курсов|



## Роль «Методист»

Отдельной таблицы ролей нет. Методист – это пользователь из группы Django с названием **«Методист»**.


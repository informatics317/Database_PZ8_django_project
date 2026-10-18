// Шаг 7
const csrfToken = document.querySelector(
    "[name=csrfmiddlewaretoken]"
).value;

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
            ...(options.headers || {})
        },
        credentials: "same-origin"
    });

    let data = null;

    if (response.status !== 204) {
        data = await response.json().catch(() => null);
    }

    if (!response.ok) {
        throw new Error(
            JSON.stringify(data || {
                detail: "Ошибка выполнения запроса"
            })
        );
    }

    return data;
}

// Шаг 8
const categorySelect =
    document.getElementById("category");

const form =
    document.getElementById("ticket-form");

const titleInput =
    document.getElementById("title");

const message =
    document.getElementById("message");

function showMessage(text, isError = false) {
    message.textContent = text;
    message.className =
        "alert " + (isError ? "alert-danger" : "alert-success");
}

function formatError(error) {
    let data;

    try {
        data = JSON.parse(error.message);
    } catch {
        return error.message;
    }

    const messages = [];

    for (const key in data) {
        const value = data[key];

        if (Array.isArray(value)) {
            messages.push(value.join(" "));
        } else {
            messages.push(value);
        }
    }

    return messages.join(" ");
}

async function loadCategories() {
    const categories = await apiRequest(
        "/api/categories/"
    );

    categorySelect.replaceChildren();

    for (const category of categories) {
        const option = document.createElement("option");
        option.value = category.id;
        option.textContent = category.name;
        categorySelect.append(option);
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        await apiRequest("/api/tickets/", {
            method: "POST",
            body: JSON.stringify({
                title: titleInput.value,
                category: Number(categorySelect.value)
            })
        });

        titleInput.value = "";
        showMessage("Заявка успешно создана");

        await loadTickets();
    } catch (error) {
        showMessage(
            "Не удалось создать заявку. " + formatError(error),
            true
        );
    }
});


// Шаг 9
const list = document.getElementById("tickets-list");
const loading = document.getElementById("loading");
const filter = document.getElementById("status-filter");


const STATUS_NAMES = {
    new: "Новая",
    progress: "В работе",
    done: "Выполнена"
};

const NEXT_STATUS = {
    new: "progress",
    progress: "done",
    done: null
};

const STATUS_COLORS = {
    new: "bg-blue-lt",
    progress: "bg-yellow-lt",
    done: "bg-green-lt"
};

async function loadTickets() {
    loading.hidden = false;

    const params = new URLSearchParams();

    if (filter.value) {
        params.set("status", filter.value);
    }

    const query = params.toString();
    const url = "/api/tickets/" + (query ? "?" + query : "");

    try {
        const tickets = await apiRequest(url);

        list.replaceChildren();

        if (tickets.length === 0) {
            const empty = document.createElement("p");
            empty.textContent = "Заявки не найдены";
            list.append(empty);
            return;
        }

        for (const ticket of tickets) {
            const row = document.createElement("div");
            row.className =
                "d-flex justify-content-between align-items-center border-bottom py-3 gap-3";

            const title = document.createElement("div");
            title.textContent =
                ticket.title + " — " + ticket.category_name;

                const created = document.createElement("div");
                created.className = "text-secondary small";
                created.textContent = "Создана: " + new Date(ticket.created_at).toLocaleString("ru-RU", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit"
                });
                title.append(created);

                const owner = document.createElement("div");
                owner.className = "text-secondary small";
                owner.textContent = "Автор: " + ticket.owner_name;
                title.append(owner);

            const status = document.createElement("span");
            status.className = "badge bg-blue-lt";
            status.textContent = ticket.status;

            status.textContent = STATUS_NAMES[ticket.status];
            status.className = "badge " + STATUS_COLORS[ticket.status];

            const select = document.createElement("select");
            select.className = "form-select w-auto";

            const currentOption = document.createElement("option");
            currentOption.value = ticket.status;
            currentOption.textContent = STATUS_NAMES[ticket.status];
            select.append(currentOption);

            const nextStatus = NEXT_STATUS[ticket.status];

            if (nextStatus) {
                const nextOption = document.createElement("option");
                nextOption.value = nextStatus;
                nextOption.textContent = STATUS_NAMES[nextStatus];
                select.append(nextOption);
            }

            const changeButton = document.createElement("button");
            changeButton.className = "btn btn-outline-primary btn-sm";
            changeButton.textContent = "Изменить статус";

            if (!nextStatus) {
                changeButton.disabled = true;
            }

            changeButton.addEventListener("click", () => {
                handleChange(ticket, select.value);
            });


            const deleteButton = document.createElement("button");
            deleteButton.className = "btn btn-outline-danger btn-sm";
            deleteButton.textContent = "Удалить";

            deleteButton.addEventListener("click", () => {
                handleDelete(ticket.id, ticket.title);
            });

            row.append(title, status);

            row.append(select, changeButton, deleteButton);

            if (!ticket.can_manage) {
                select.remove();
                changeButton.remove();
                deleteButton.remove();
            }

            list.append(row);
        }
    } catch (error) {
        showMessage(
            "Не удалось загрузить заявки. " + formatError(error),
            true
        );
    } finally {
        loading.hidden = true;
    }
}

filter.addEventListener("change", loadTickets);

async function initialize() {
    try {
        await loadCategories();
        await loadTickets();
    } catch (error) {
        showMessage(
            "Ошибка инициализации. " + formatError(error),
            true
        );
    }
}

initialize();


// Шаг 10
async function changeStatus(ticketId, newStatus) {
    await apiRequest(`/api/tickets/${ticketId}/`, {
        method: "PATCH",
        body: JSON.stringify({
            status: newStatus
        })
    });

    await loadTickets();

    showMessage("Статус заявки изменён");
}

async function deleteTicket(ticketId, ticketTitle) {
    const confirmed = confirm(
        `Удалить заявку «${ticketTitle}»?`
    );

    if (!confirmed) {
        return;
    }

    await apiRequest(`/api/tickets/${ticketId}/`, {
        method: "DELETE"
    });

    await loadTickets();

    showMessage("Заявка удалена");
}


async function handleChange(ticket, newStatus) {
    if (newStatus === ticket.status) {
        showMessage("Выберите новый статус", true);
        return;
    }

    try {
        await changeStatus(ticket.id, newStatus);
    } catch (error) {
        showMessage(
            "Не удалось изменить статус. " + formatError(error),
            true
        );
    }
}

async function handleDelete(ticketId, ticketTitle) {
    try {
        await deleteTicket(ticketId, ticketTitle);
    } catch (error) {
        showMessage(
            "Не удалось удалить заявку. " + formatError(error),
            true
        );
    }
}

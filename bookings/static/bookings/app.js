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

const message = document.getElementById("message");

function showMessage(text, isError = false) {
    message.textContent = text;
    message.className =
        "alert " + (isError ? "alert-danger" : "alert-success");
}

function formatError(error) {
    if (error instanceof TypeError) {
        return "Сервер временно недоступен. Проверьте подключение к интернету и попробуйте позже.";
    }

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


const form = document.getElementById("booking-form");
const equipmentSelect = document.getElementById("equipment");
const quantityInput = document.getElementById("quantity");
const purposeInput = document.getElementById("purpose");
const filterStatus = document.getElementById("filter-status");
const filterEquipment = document.getElementById("filter-equipment");
const list = document.getElementById("bookings-list");
const loading = document.getElementById("loading");
const historyCard = document.getElementById("history-card");
const historyTitle = document.getElementById("history-title");
const historyList = document.getElementById("history-list");

const STATUS_COLORS = {
    created: "bg-blue-lt",
    confirmed: "bg-yellow-lt",
    completed: "bg-green-lt",
    cancelled: "bg-red-lt"
};

const DONE_TEXT = {
    confirm: "Бронирование подтверждено",
    complete: "Бронирование завершено, оборудование возвращено",
    cancel: "Бронирование отменено"
};

let openedHistoryId = null;

// ---------- Оборудование ----------
async function loadEquipment() {
    const items = await apiRequest("/api/equipment/");
    const selectedFilter = filterEquipment.value;

    equipmentSelect.replaceChildren();
    filterEquipment.replaceChildren();
    filterEquipment.append(new Option("Всё оборудование", ""));

    for (const item of items) {
        equipmentSelect.append(new Option(
            item.name + " (свободно: " + item.available + ")",
            item.id
        ));
        filterEquipment.append(new Option(item.name, item.id));
    }

    filterEquipment.value = selectedFilter;
}


function makeButton(text, style, onClick) {
    const button = document.createElement("button");
    button.className = "btn btn-sm " + style;
    button.textContent = text;
    button.addEventListener("click", onClick);
    return button;
}

function createRow(booking) {
    const row = document.createElement("div");
    row.className =
        "list-group-item d-flex flex-wrap justify-content-between align-items-center gap-2";

    const info = document.createElement("div");
    info.textContent =
        "№" + booking.id + ": " + booking.equipment_name +
        " × " + booking.quantity + " — " + booking.purpose;

    const author = document.createElement("div");
    author.className = "text-secondary small";
    author.textContent = "Автор: " + booking.owner_name;
    info.append(author);

    const badge = document.createElement("span");
    badge.className = "badge " + STATUS_COLORS[booking.status];
    badge.textContent = booking.status_text;

    const buttons = document.createElement("div");
    buttons.className = "btn-list";

    if (booking.status === "created" && booking.can_manage) {
        buttons.append(makeButton("Подтвердить", "btn-outline-success",
            () => runAction(booking.id, "confirm")));
    }

    if (booking.status === "confirmed" && booking.can_manage) {
        buttons.append(makeButton("Завершить", "btn-outline-success",
            () => runAction(booking.id, "complete")));
    }

    if (booking.status === "created") {
        buttons.append(makeButton("Изменить цель", "btn-outline-primary",
            () => editBooking(booking)));
        buttons.append(makeButton("Отменить", "btn-outline-warning",
            () => runAction(booking.id, "cancel")));
    }

    buttons.append(makeButton("История", "btn-outline-secondary",
        () => showHistory(booking.id)));

    if (booking.status === "created" || booking.status === "cancelled") {
        buttons.append(makeButton("Удалить", "btn-outline-danger",
            () => deleteBooking(booking)));
    }

    row.append(info, badge, buttons);
    return row;
}

async function loadBookings() {
    loading.hidden = false;

    const params = new URLSearchParams();

    if (filterStatus.value) {
        params.set("status", filterStatus.value);
    }

    if (filterEquipment.value) {
        params.set("equipment", filterEquipment.value);
    }

    const query = params.toString();
    const url = "/api/bookings/" + (query ? "?" + query : "");

    try {
        const bookings = await apiRequest(url);

        list.replaceChildren();

        if (bookings.length === 0) {
            list.textContent = "Бронирования не найдены";
            return;
        }

        for (const booking of bookings) {
            list.append(createRow(booking));
        }
    } catch (error) {
        showMessage(
            "Не удалось загрузить бронирования. " + formatError(error),
            true
        );
    } finally {
        loading.hidden = true;
    }
}

async function refreshAll() {
    await loadEquipment();
    await loadBookings();

    if (openedHistoryId !== null) {
        await showHistory(openedHistoryId);
    }
}


async function showHistory(id) {
    try {
        const events = await apiRequest("/api/bookings/" + id + "/history/");

        openedHistoryId = id;
        historyTitle.textContent = "История бронирования №" + id;
        historyList.replaceChildren();

        for (const event of events) {
            const item = document.createElement("li");
            item.className = "list-group-item";
            item.textContent =
                new Date(event.created_at).toLocaleString("ru-RU") +
                " — " + event.action + " (" + event.actor_name + ")";
            historyList.append(item);
        }

        historyCard.hidden = false;
    } catch (error) {
        showMessage(
            "Не удалось загрузить историю. " + formatError(error),
            true
        );
    }
}


form.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        await apiRequest("/api/bookings/", {
            method: "POST",
            body: JSON.stringify({
                equipment: Number(equipmentSelect.value),
                quantity: Number(quantityInput.value),
                purpose: purposeInput.value
            })
        });

        purposeInput.value = "";
        await refreshAll();
        showMessage("Бронирование создано");
    } catch (error) {
        showMessage(
            "Не удалось создать бронирование. " + formatError(error),
            true
        );
    }
});

async function runAction(id, action) {
    try {
        await apiRequest("/api/bookings/" + id + "/" + action + "/", {
            method: "POST"
        });

        await refreshAll();
        showMessage(DONE_TEXT[action]);
    } catch (error) {
        showMessage(
            "Действие не выполнено. " + formatError(error),
            true
        );
    }
}

async function editBooking(booking) {
    const purpose = prompt("Новая цель бронирования:", booking.purpose);

    if (purpose === null) {
        return;
    }

    try {
        await apiRequest("/api/bookings/" + booking.id + "/", {
            method: "PATCH",
            body: JSON.stringify({ purpose: purpose })
        });

        await refreshAll();
        showMessage("Цель бронирования изменена");
    } catch (error) {
        showMessage(
            "Не удалось изменить бронирование. " + formatError(error),
            true
        );
    }
}

async function deleteBooking(booking) {
    const confirmed = confirm(
        "Удалить бронирование №" + booking.id + "?"
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest("/api/bookings/" + booking.id + "/", {
            method: "DELETE"
        });

        if (openedHistoryId === booking.id) {
            openedHistoryId = null;
            historyCard.hidden = true;
        }

        await refreshAll();
        showMessage("Бронирование удалено");
    } catch (error) {
        showMessage(
            "Не удалось удалить бронирование. " + formatError(error),
            true
        );
    }
}


filterStatus.addEventListener("change", loadBookings);
filterEquipment.addEventListener("change", loadBookings);

async function initialize() {
    try {
        await loadEquipment();
        await loadBookings();
    } catch (error) {
        showMessage(
            "Ошибка инициализации. " + formatError(error),
            true
        );
    }
}

initialize();


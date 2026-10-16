const SUPABASE_URL = "https://ofsjdrhpnqjeqhuuazmo.supabase.co";
const SUPABASE_PUBLISHABLE_KEY = "sb_publishable_g2pivdmPtUrCeXmGhhwFoA_iKdDUNY-";

const supabaseClient = window.supabase.createClient(
    SUPABASE_URL,
    SUPABASE_PUBLISHABLE_KEY
);
const API_URL = "https://expense-tracker-api-kg8k.onrender.com/expenses";

async function loadExpenses() {
    try {
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }

        const contentType = response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            throw new Error("API returned HTML or another non-JSON response.");
        }

        const expenses = await response.json();


        const monthFilter = document.getElementById("month-filter");
        const selectedMonth = monthFilter.value;

// Build the list of available months.
        const months = [...new Set(
            expenses.map((expense) => expense.date.slice(0, 7))
        )].sort().reverse();

// Populate the dropdown only once.
        if (monthFilter.options.length === 1) {
            months.forEach((month) => {
                const option = document.createElement("option");
                option.value = month;
                option.textContent = month;
                monthFilter.appendChild(option);
            });
        }

// Filter expenses when a specific month is selected.
        const filteredExpenses = selectedMonth === "all"
            ? expenses
            : expenses.filter(
                (expense) => expense.date.startsWith(selectedMonth)
            );


        const monthlyTotals = {};

        expenses.forEach((expense) => {
            const month = expense.date.slice(0, 7);

            monthlyTotals[month] =
                (monthlyTotals[month] || 0) + expense.amount;
        });

        const monthlyChart = document.getElementById("monthly-chart");
        monthlyChart.innerHTML = "";

        Object.entries(monthlyTotals)
            .sort((a, b) => a[0].localeCompare(b[0]))
            .reverse()
            .forEach(([month, amount]) => {
                const row = document.createElement("p");

                const maxMonthlyAmount = Math.max(
                    ...Object.values(monthlyTotals),
                    1
                );

                const bar = document.createElement("div");
                bar.className = "chart-bar-row";

                const label = document.createElement("span");
                label.textContent = month;

                const track = document.createElement("div");
                track.className = "chart-bar-track";

                const fill = document.createElement("div");
                fill.className = "chart-bar-fill";
                fill.style.width = `${(amount / maxMonthlyAmount) * 100}%`;

                const value = document.createElement("span");
                value.textContent = `₹${amount.toFixed(2)}`;

                track.appendChild(fill);
                bar.append(label, track, value);
                monthlyChart.appendChild(bar);

            });

        if (Object.keys(monthlyTotals).length === 0) {
            monthlyChart.textContent = "No expense data available.";
        }


        const categoryTotalsForChart = {};

        filteredExpenses.forEach((expense) => {
            const category = expense.category;

            categoryTotalsForChart[category] =
                (categoryTotalsForChart[category] || 0) + expense.amount;
        });

        const categoryChart = document.getElementById("category-chart");
        categoryChart.innerHTML = "";

        Object.entries(categoryTotalsForChart)
            .sort((a, b) => b[1] - a[1])
            .forEach(([category, amount]) => {
                const row = document.createElement("p");

                const maxCategoryAmount = Math.max(
                    ...Object.values(categoryTotalsForChart),
                    1
                );

                const bar = document.createElement("div");
                bar.className = "chart-bar-row";

                const label = document.createElement("span");
                label.textContent = category;

                const track = document.createElement("div");
                track.className = "chart-bar-track";

                const fill = document.createElement("div");
                fill.className = "chart-bar-fill";
                fill.style.width = `${(amount / maxCategoryAmount) * 100}%`;

                const value = document.createElement("span");
                value.textContent = `₹${amount.toFixed(2)}`;

                track.appendChild(fill);
                bar.append(label, track, value);
                categoryChart.appendChild(bar);

            });

        if (Object.keys(categoryTotalsForChart).length === 0) {
            categoryChart.textContent = "No expense data for this month.";
        }




        const total = expenses.reduce(
            (sum, expense) => sum + expense.amount,
            0
        );

        document.getElementById("total-expenses").textContent =
            `₹${total.toFixed(2)}`;


        document.getElementById("expense-count").textContent =
            expenses.length;

        const categoryTotals = {};

        expenses.forEach((expense) => {
            const category = expense.category;

            categoryTotals[category] =
                (categoryTotals[category] || 0) + expense.amount;
        });

        const topCategory = Object.entries(categoryTotals)
            .sort((a, b) => b[1] - a[1])[0];

        document.getElementById("top-category").textContent =
            topCategory ? topCategory[0] : "—";


        const expenseList = document.getElementById("expense-list");
        expenseList.innerHTML = "";


        expenses.forEach((expense) => {
            const item = document.createElement("li");
            item.className = "expense-item";

            const details = document.createElement("span");
            details.textContent =
                `${expense.category} — ₹${expense.amount.toFixed(2)} — ${expense.date}`;

            const actions = document.createElement("div");
            actions.className = "expense-actions";

            const editButton = document.createElement("button");
            editButton.type = "button";
            editButton.textContent = "Edit";
            editButton.addEventListener("click", () => {
                startEditing(expense);
            });

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.textContent = "Delete";
            deleteButton.addEventListener("click", () => {
                deleteExpense(expense.id);
            });

            actions.append(editButton, deleteButton);
            item.append(details, actions);
            expenseList.appendChild(item);
        });


    } catch (error) {
        console.error("Could not load expenses:", error);

        document.getElementById("total-expenses").textContent =
            "Unable to load expenses";

        document.getElementById("expense-count").textContent = "—";
        document.getElementById("top-category").textContent = "—";
        document.getElementById("expense-list").innerHTML = "";
        document.getElementById("monthly-chart").textContent =
            "Unable to load monthly chart.";
        document.getElementById("category-chart").textContent =
            "Unable to load category chart.";
    }
}

loadExpenses();

const expenseForm = document.getElementById("expense-form");
const formMessage = document.getElementById("form-message");

expenseForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    console.log("Expense form submitted");

    const expense = {
        amount: Number(document.getElementById("amount").value),
        category: document.getElementById("category").value.trim(),
        description: document.getElementById("description").value.trim(),
        date: document.getElementById("date").value
    };


    try {
        const expenseId = document.getElementById("expense-id").value;

        const response = await fetch(
            expenseId ? `${API_URL}/${expenseId}` : API_URL,
            {
                method: expenseId ? "PUT" : "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(expense)
            }
        );

        if (!response.ok) {
            throw new Error("Failed to save expense");
        }

        formMessage.textContent = expenseId
            ? "Expense updated successfully!"
            : "Expense added successfully!";

        cancelEditing();

        await loadExpenses();

    } catch (error) {
        console.error("Could not save expense:", error);
        formMessage.textContent =
            "Could not save expense. Check the API server.";
    }

});

document.getElementById("month-filter").addEventListener("change", () => {
    loadExpenses();
});

function startEditing(expense) {
    document.getElementById("expense-id").value = expense.id;
    document.getElementById("amount").value = expense.amount;
    document.getElementById("category").value = expense.category;
    document.getElementById("description").value =
        expense.description || "";
    document.getElementById("date").value = expense.date;

    document.getElementById("submit-button").textContent =
        "Update Expense";
    document.getElementById("cancel-edit").hidden = false;

    document.getElementById("expense-form").scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}

function cancelEditing() {
    document.getElementById("expense-form").reset();
    document.getElementById("expense-id").value = "";

    document.getElementById("submit-button").textContent =
        "Add Expense";
    document.getElementById("cancel-edit").hidden = true;
}

async function deleteExpense(expenseId) {
    if (!confirm("Are you sure you want to delete this expense?")) {
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/${expenseId}`,
            { method: "DELETE" }
        );

        if (!response.ok) {
            throw new Error("Failed to delete expense");
        }

        await loadExpenses();
        cancelEditing();
    } catch (error) {
        console.error("Could not delete expense:", error);
        alert("Could not delete expense. Please try again.");
    }
}

document.getElementById("cancel-edit").addEventListener(
    "click",
    cancelEditing
);

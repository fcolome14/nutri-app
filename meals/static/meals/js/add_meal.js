document.addEventListener('DOMContentLoaded', () => {
  MealApp.init();
});

const MealApp = (() => {
  const meals = [];
  let debounceTimeout = null;
  const cache = {};
  const MAX_CACHE_SIZE = 100;

  // Element references
  const elements = {
    foodSearch: document.getElementById('food-search'),
    foodId: document.getElementById('food-id'),
    quantity: document.getElementById('quantity'),
    date: document.getElementById('date'),
    keepDate: document.getElementById('keep-date'),
    tableBody: document.getElementById('meal-list-body'),
    mealsJson: document.getElementById('meals-json'),
    counter: document.getElementById('counter'),
  };

  const suggestionsBox = createSuggestionsBox();

  function init() {
    setTodayAsDefaultDate();
    setupAutocomplete();
    setupOutsideClickListener();
    setupAddMealButton();
  }

  function setTodayAsDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    elements.date.value = today;
  }

  function createSuggestionsBox() {
    const box = document.createElement('ul');
    box.id = 'suggestions';
    box.style.position = 'absolute';
    box.style.zIndex = '1000';
    document.body.appendChild(box);
    return box;
  }

  function setupAutocomplete() {
    elements.foodSearch.addEventListener('input', () => {
      const query = elements.foodSearch.value.trim();
      clearTimeout(debounceTimeout);

      debounceTimeout = setTimeout(() => {
        if (query.length < 2) {
          suggestionsBox.innerHTML = '';
          return;
        }
        fetchSuggestions(query);
      }, 500);
    });
  }

  function setupAddMealButton() {
    const addButton = document.getElementById('add-meal-button');
    if (addButton) {
      addButton.addEventListener('click', addMeal);
    } else {
      console.warn("⚠️ 'Add Meal' button not found!");
    }
  }
  
  function fetchSuggestions(query) {
    const normalizedQuery = query.toLowerCase().trim();
    if (cache[normalizedQuery]) {
      showSuggestions(cache[normalizedQuery]);
      return;
    }

    fetch(`/food-autocomplete/?q=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(data => {
        cacheSuggestions(normalizedQuery, data);
        showSuggestions(data)})
      .catch(console.error);
  }

  function showSuggestions(data) {
    suggestionsBox.innerHTML = '';
    const rect = elements.foodSearch.getBoundingClientRect();
    suggestionsBox.style.top = `${rect.bottom + window.scrollY}px`;
    suggestionsBox.style.left = `${rect.left + window.scrollX}px`;

    data.forEach(item => {
      const li = document.createElement('li');
      li.textContent = item.name;
      li.style.cursor = 'pointer';
      li.addEventListener('click', () => {
        elements.foodSearch.value = item.name;
        elements.foodId.value = item.id;
        suggestionsBox.innerHTML = '';
      });
      suggestionsBox.appendChild(li);food-search
    });
  }

  function setupOutsideClickListener() {
    document.addEventListener('click', (e) => {
      if (!e.target.closest('#food-search') && !e.target.closest('#suggestions')) {
        suggestionsBox.innerHTML = '';
      }
    });
  }

  function validateInputs() {
    const { foodId, quantity, date } = elements;
    return foodId.value && quantity.value && date.value;
  }

  function updateMealCounter(change) {
    elements.counter.textContent = parseInt(elements.counter.textContent) + change;
  }

  function clearInputs() {
    elements.foodId.value = '';
    elements.foodSearch.value = '';
    elements.quantity.value = '';
    if (!elements.keepDate.checked) {
      elements.date.value = '';
    }
  }

  function createMealRow({ food_id, food_name, quantity, date }) {
    const row = document.createElement('tr');

    row.appendChild(createTableCell(food_name));
    row.appendChild(createTableCell(`${quantity}g`));
    row.appendChild(createTableCell(date));

    const actionsCell = document.createElement('td');
    const deleteButton = createDeleteButton(() => {
      const index = meals.findIndex(
        m => m.food_id === food_id && m.quantity === quantity && m.date === date
      );
      if (index > -1) meals.splice(index, 1);
      row.remove();
      updateMealCounter(-1);
      updateMealsJson();
    });
    actionsCell.appendChild(deleteButton);
    row.appendChild(actionsCell);

    return row;
  }

  function createTableCell(content) {
    const cell = document.createElement('td');
    cell.textContent = content;
    return cell;
  }

  function createDeleteButton(onClick) {
    const btn = document.createElement('button');
    btn.textContent = '❌';
    btn.title = 'Remove';
    btn.classList.add('delete-button');
    btn.style.color = 'red';
    btn.style.cursor = 'pointer';
    btn.addEventListener('click', onClick);
    return btn;
  }

  function updateMealsJson() {
    elements.mealsJson.value = JSON.stringify(meals);
  }

  function cacheSuggestions(key, data) {
    if (Object.keys(cache).length >= MAX_CACHE_SIZE) {
      delete cache[Object.keys(cache)[0]]; // Basic FIFO cache cleanup
    }
    cache[key] = data;
  }

  function addMeal() {
    if (!validateInputs()) {
      alert('Please fill in all fields before adding.');
      return;
    }

    const meal = {
      food_id: elements.foodId.value,
      food_name: elements.foodSearch.value,
      quantity: elements.quantity.value,
      date: elements.date.value,
    };

    meals.push(meal);

    const row = createMealRow(meal);
    elements.tableBody.appendChild(row);
    updateMealCounter(1);
    updateMealsJson();
    clearInputs();
  }

  return {
    init,
    addMeal,
  };
})();
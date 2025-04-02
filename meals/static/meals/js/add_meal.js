const meals = [];

function addMeal() {
  const foodId = document.getElementById('food-id').value;
  const foodName = document.getElementById('food-search').value;
  const quantity = document.getElementById('quantity').value;
  const dateInput = document.getElementById('date');
  const keepDate = document.getElementById('keep-date').checked;
  const date = dateInput.value;

  if (!foodId || !quantity || !date) {
    alert('Please fill in all fields before adding.');
    return;
  }

  meals.push({ food_id: foodId, quantity, date });

  const list = document.getElementById('meal-list');
  const li = document.createElement('li');
  li.innerHTML = `<strong>${foodName}</strong>: ${quantity}g [${date}]`;
  list.appendChild(li);

  document.getElementById('counter').textContent = meals.length;
  document.getElementById('meals-json').value = JSON.stringify(meals);

  document.getElementById('food-id').value = '';
  document.getElementById('food-search').value = '';
  document.getElementById('quantity').value = '';
  if (!keepDate) {
    dateInput.value = '';
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('food-search');
  const hiddenInput = document.getElementById('food-id');
  const suggestionsBox = document.createElement('ul');
  const dateInput = document.getElementById('date');

  const today = new Date().toISOString().split('T')[0];
  dateInput.value = today;

  suggestionsBox.id = 'suggestions';
  document.body.appendChild(suggestionsBox);

  searchInput.addEventListener('input', function () {
    const query = this.value;
    if (query.length < 2) {
      suggestionsBox.innerHTML = '';
      return;
    }

    fetch(`/food-autocomplete/?q=${encodeURIComponent(query)}`)
      .then(response => response.json())
      .then(data => {
        suggestionsBox.innerHTML = '';
        const rect = searchInput.getBoundingClientRect();
        suggestionsBox.style.top = rect.bottom + window.scrollY + 'px';
        suggestionsBox.style.left = rect.left + window.scrollX + 'px';

        data.forEach(item => {
          const li = document.createElement('li');
          li.textContent = item.name;
          li.addEventListener('click', () => {
            searchInput.value = item.name;
            hiddenInput.value = item.id;
            suggestionsBox.innerHTML = '';
          });
          suggestionsBox.appendChild(li);
        });
      });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('#food-search') && !e.target.closest('#suggestions')) {
      suggestionsBox.innerHTML = '';
    }
  });
});

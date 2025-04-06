const WeightApp = (() => {
    const weights = []; // Array to store weight entries
  
    // Element references
    const elements = {
      weight: document.getElementById('weight'),
      fat: document.getElementById('fat'),
      date: document.getElementById('date'),
      weightForm: document.getElementById('weight-form'),
      weightList: document.getElementById('weight-list-body'), // Table body for displaying weights
      counter: document.getElementById('weight-counter'), // Counter for the number of entries
    };
  
    function init() {
      setupAddWeightButton();
      loadWeightsFromSession();
    }
  
    function setupAddWeightButton() {
      if (elements.weightForm) {
        elements.weightForm.addEventListener('submit', (e) => {
          e.preventDefault(); // Prevent form submission
          addWeight();
        });
      } else {
        console.warn("⚠️ 'Weight Form' not found!");
      }
    }
  
    function addWeight() {
      const weight = parseFloat(elements.weight.value);
      const fat = parseFloat(elements.fat.value);
      const date = elements.date.value;
  
      // Validate inputs
      if (!weight || weight <= 0 || !fat || fat < 0 || fat > 100 || !date) {
        alert('Please provide valid inputs for weight, body fat, and date.');
        return;
      }
  
      // Create a weight entry object
      const weightEntry = { weight, fat, date };
  
      // Add the entry to the weights array
      weights.push(weightEntry);
  
      // Update the UI
      const row = createWeightRow(weightEntry);
      elements.weightList.appendChild(row);
      updateWeightCounter(1);
      saveWeightsToSession();
  
      // Clear input fields
      clearInputs();
    }
  
    function createWeightRow({ weight, fat, date }) {
      const row = document.createElement('tr');
  
      row.appendChild(createTableCell(`${weight} kg`));
      row.appendChild(createTableCell(`${fat}%`));
      row.appendChild(createTableCell(date));
  
      const actionsCell = document.createElement('td');
      const deleteButton = createDeleteButton(() => {
        const index = weights.findIndex(
          (entry) => entry.weight === weight && entry.fat === fat && entry.date === date
        );
        if (index > -1) weights.splice(index, 1);
        row.remove();
        updateWeightCounter(-1);
        saveWeightsToSession();
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
  
    function updateWeightCounter(change) {
      const counter = elements.counter;
      if (counter) {
        counter.textContent = parseInt(counter.textContent || '0') + change;
      }
    }
  
    function saveWeightsToSession() {
      sessionStorage.setItem('weights', JSON.stringify(weights));
    }
  
    function loadWeightsFromSession() {
      const savedWeights = sessionStorage.getItem('weights');
      if (!savedWeights) return;
  
      try {
        const parsedWeights = JSON.parse(savedWeights);
        parsedWeights.forEach((entry) => {
          weights.push(entry); // Re-populate the weights array
          const row = createWeightRow(entry); // Re-render rows
          elements.weightList.appendChild(row);
        });
  
        updateWeightCounter(parsedWeights.length);
      } catch (e) {
        console.warn("⚠️ Failed to restore weights from session:", e);
      }
    }
  
    function clearInputs() {
      elements.weight.value = '';
      elements.fat.value = '';
      elements.date.value = '';
    }
  
    return {
      init,
    };
  })();
  
  // Initialize the WeightApp when the DOM is fully loaded
  document.addEventListener('DOMContentLoaded', () => {
    WeightApp.init();
  });
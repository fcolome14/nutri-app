document.addEventListener('DOMContentLoaded', () => {
  const computeBMRButton = document.getElementById('compute-bmr-button');
  const formulaRadios = document.querySelectorAll('input[name="formula"]');
  const fatContainer = document.getElementById('body-fat-container');
  const toggleEstimator = document.getElementById('toggle-fat-estimator');
  const estimationForm = document.getElementById('fat-estimation-form');
  const closeEstimator = document.getElementById('close-estimator');
  const estimateButton = document.getElementById('estimate-fat-btn');
  const fatInput = document.getElementById('fat-bmr');
  const genderSelect = document.getElementById('gender');
  const hipsInput = document.getElementById('hips');
  const hipsLabel = document.getElementById('hips-label');

  // Update visibility of Body Fat input
  const updateFatInputVisibility = () => {
    const selected = document.querySelector('input[name="formula"]:checked');
    fatContainer.style.display = selected && selected.value === 'katch-mcardle' ? 'inline' : 'none';
  };

  formulaRadios.forEach(radio => {
    radio.addEventListener('change', updateFatInputVisibility);
  });

  updateFatInputVisibility(); // on load

  // Show/hide hips for female
  const updateHipsVisibility = () => {
    const showHips = genderSelect.value === 'female';
    hipsInput.style.display = showHips ? 'inline' : 'none';
    hipsLabel.style.display = showHips ? 'inline' : 'none';
  };

  genderSelect.addEventListener('change', updateHipsVisibility);
  updateHipsVisibility();

  // BMR computation
  if (computeBMRButton) {
    computeBMRButton.addEventListener('click', async () => {
      const formula = document.querySelector('input[name="formula"]:checked').value;
      const age = document.getElementById('age').value;
      const height = document.getElementById('height').value;
      const weight = document.getElementById('weight-bmr').value;
      const activityLevel = document.getElementById('activity-level').value;
      const gender = genderSelect.value;
      const fat = formula === 'katch-mcardle' ? fatInput.value : null;
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      const data = { formula, age, height, weight, activity_level: activityLevel, gender, fat };

      try {
        const response = await fetch('/compute_bmr/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
          },
          body: JSON.stringify(data),
        });

        const result = await response.json();
        const output = document.getElementById('bmr-result');

        if (response.ok) {
          output.innerHTML = `
            <div class="bmr-result-box">
              <h4 style="margin-bottom: 0.5em;">🎯 BMR Results</h4>
              <p><strong>Basal Metabolic Rate:</strong> <span class="highlight">${result.bmr} kcal/day</span></p>
              <p><strong>Adjusted for Activity:</strong> <span class="highlight">${result.bmr_adj} kcal/day</span></p>
              <p style="font-size: 0.9em; color: gray;">* Based on the <em>${data.formula.replace('-', ' ')}</em> formula and <em>${data.activity_level.replace('-', ' ')}</em> activity level.</p>
            </div>
          `;
        } else {
          output.textContent = `❌ Error: ${result.error || 'An unexpected error occurred.'}`;
        }
      } catch (err) {
        console.error(err);
        alert("Something went wrong while computing BMR.");
      }
    });
  }

  // Estimator toggle button logic
  toggleEstimator.addEventListener('click', () => {
    const isOpen = estimationForm.style.display === 'block';
    estimationForm.style.display = isOpen ? 'none' : 'block';
    toggleEstimator.textContent = isOpen ? 'Estimate Body Fat % 🔍' : 'Close Estimation Mode ❌';
  });

  // Optional close button (if you added a ❌)
  if (closeEstimator) {
    closeEstimator.addEventListener('click', () => {
      estimationForm.style.display = 'none';
      toggleEstimator.textContent = 'Estimate Body Fat % 🔍';
    });
  }

  // Estimate Body Fat
  estimateButton.addEventListener('click', () => {
    const gender = genderSelect.value;
    const neck = parseFloat(document.getElementById('neck').value);
    const waist = parseFloat(document.getElementById('waist').value);
    const hips = parseFloat(document.getElementById('hips').value);
    const height = parseFloat(document.getElementById('height-est').value);

    if (!gender || isNaN(neck) || isNaN(waist) || isNaN(height) || (gender === 'female' && isNaN(hips))) {
      alert("Please fill all fields correctly to estimate body fat.");
      return;
    }

    let bodyFat;

    try {
      if (gender === 'male') {
        bodyFat = 495 / (1.0324 - 0.19077 * Math.log10(waist - neck) + 0.15456 * Math.log10(height)) - 450;
      } else {
        bodyFat = 495 / (1.29579 - 0.35004 * Math.log10(waist + hips - neck) + 0.22100 * Math.log10(height)) - 450;
      }
    } catch (err) {
      alert("⚠️ Invalid values. Ensure waist > neck, and hips (if needed) are logical.");
      return;
    }

    bodyFat = Math.max(0, Math.min(100, bodyFat.toFixed(2)));
    fatInput.value = bodyFat;

    estimationForm.style.display = 'none';
    toggleEstimator.textContent = 'Estimate Body Fat % 🔍';

    const feedback = document.createElement('p');
    feedback.className = 'estimate-success';
    feedback.textContent = `✅ Estimated Body Fat: ${bodyFat}% has been filled in.`;
    fatInput.parentNode.appendChild(feedback);
  });
});
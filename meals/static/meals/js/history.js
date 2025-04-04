document.addEventListener('DOMContentLoaded', function () {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');

    if (startDateInput && endDateInput) {
        // Set min value if pre-filled
        if (startDateInput.value) {
            endDateInput.min = startDateInput.value;
        }

        startDateInput.addEventListener('change', function () {
            endDateInput.min = this.value;
            if (endDateInput.value < this.value) {
                endDateInput.value = '';
            }
        });
    }
});

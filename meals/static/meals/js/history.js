document.addEventListener('DOMContentLoaded', function () {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');

    const today = new Date();
    const weekAgo = new Date();
    weekAgo.setDate(today.getDate() - 6); // 7 days including today

    const formatDate = (date) => date.toISOString().split('T')[0];

    if (startDateInput && !startDateInput.value) {
        startDateInput.value = formatDate(weekAgo);
        endDateInput.min = startDateInput.value;
    }

    if (endDateInput && !endDateInput.value) {
        endDateInput.value = formatDate(today);
    }

    if (startDateInput && endDateInput) {
        endDateInput.min = startDateInput.value;
    
        startDateInput.addEventListener('change', function () {
            endDateInput.min = this.value;
            if (endDateInput.value < this.value) {
                endDateInput.value = '';
            }
        });
    } else {
        if (!startDateInput) console.warn("'start_date' input not found.");
        if (!endDateInput) console.warn("'end_date' input not found.");
    }
    
});
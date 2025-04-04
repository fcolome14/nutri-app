document.addEventListener('DOMContentLoaded', function () {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');

    const today = new Date();
    const weekAgo = new Date();
    weekAgo.setDate(today.getDate() - 6); // 7 days including today

    const formatDate = (date) => date.toISOString().split('T')[0];

    if (!startDateInput.value) {
        startDateInput.value = formatDate(weekAgo);
    }

    if (!endDateInput.value) {
        endDateInput.value = formatDate(today);
    }

    endDateInput.min = startDateInput.value;

    startDateInput.addEventListener('change', function () {
        endDateInput.min = this.value;
        if (endDateInput.value < this.value) {
            endDateInput.value = '';
        }
    });
});
function showToast(title, message, category = 'info') {
    const toastTitle = document.getElementById('toastTitle');
    const toastBody = document.getElementById('toastBody');
    const toastElement = document.getElementById('liveToast');

    if (!toastTitle || !toastBody || !toastElement) {
        console.error('Элементы тостера не найдены.');
        return;
    }

    toastTitle.innerText = title;
    toastBody.innerText = message;

    let toastClass;
    if (category === 'success') {
        toastClass = 'text-success';
    } else if (category === 'danger') {
        toastClass = 'text-danger';
    } else if (category === 'info') {
        toastClass = 'text-info';
    } else {
        toastClass = 'text-secondary';
    }
    toastTitle.className = `me-auto ${toastClass}`;

    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

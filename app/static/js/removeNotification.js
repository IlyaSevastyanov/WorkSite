function removeNotification(notificationId) {
    // Ищем элемент уведомления по ID
    const notificationElement = document.getElementById(`notification-${notificationId}`);
    if (notificationElement) {
        // Удаляем элемент с уведомлением
        notificationElement.remove();
    }
}

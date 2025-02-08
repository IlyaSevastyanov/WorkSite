function openEditRoleModal(userId, currentRole) {
    console.log("Открытие модального окна для пользователя:", userId, "с ролью:", currentRole);

    document.getElementById('editUserId').value = userId;
    const roleSelect = document.getElementById('editRole');

    // Устанавливаем текущую роль в select
    Array.from(roleSelect.options).forEach(option => {
        option.selected = option.text === currentRole;
    });

    // Открываем модальное окно
    const modal = new bootstrap.Modal(document.getElementById('editRoleModal'));
    modal.show();
}

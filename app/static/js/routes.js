function openEditRouteModal(routeId, routeName) {
    if (!routeId || isNaN(routeId)) {
        console.error("Некорректный routeId:", routeId);
        return;
    }

    const form = document.getElementById('editRouteForm');
    form.action = `/update_route/${routeId}`;
    document.getElementById('editRouteName').value = routeName;

    const modal = new bootstrap.Modal(document.getElementById('editRouteModal'));
    modal.show();
}


function editRoute(routeId) {
    const form = document.getElementById('routeForm');
    form.action = form.dataset.actionTemplate.replace('/0', `/${routeId}`);
    // Обновление значений в форме
    const routeElement = document.querySelector(`[data-route-id="${routeId}"]`);
    form.querySelector('#routeName').value = routeElement.dataset.routeName;
    form.querySelector('#travelTime').value = routeElement.dataset.travelTime;
    form.querySelector('#cost').value = routeElement.dataset.routeCost;
}

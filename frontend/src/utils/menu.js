const invoice = document.getElementById('id_invoice')
const task = document.getElementById('id_task')
const project = document.getElementById('id_project')
const client = document.getElementById('id_client')

invoice.addEventListener('change', function() {
    var selectedIndex = this.selectedIndex;
    task.selectedIndex = selectedIndex;
    project.selectedIndex = selectedIndex;
    client.selectedIndex = selectedIndex;
});

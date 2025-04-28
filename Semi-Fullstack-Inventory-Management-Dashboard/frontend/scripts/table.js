document.addEventListener("DOMContentLoaded", function() {
    // get data
    function fetchAlerts() {
        fetch('/api/dashboard-table-data')
            .then(response => response.json()) // response to JSON
            .then(data => {
                populateTable(data.alerts); // populate table
            })
            .catch(error => {
                console.error('Error fetching alerts:', error);
            });
    }

    // populate table with alerts
    function populateTableRecursive(alerts, table) {
        if (alerts.length === 0) return; // default
    
        const alert = alerts[0]; // get first alert
        const row = document.createElement('tr');
    
        // create cells
        function createCell(content, className = '') {
            const cell = document.createElement('td');
            cell.textContent = content;
            if (className) cell.classList.add(className);
            return cell;
        }
    
        // append cells
        row.appendChild(createCell(alert.urgency, alert.urgency === 'Critical' ? 'critical' : alert.urgency === 'Warning' ? 'warning' : ''));
        row.appendChild(createCell(alert.type));
        row.appendChild(createCell(alert.category));
        row.appendChild(createCell(alert.product));
        row.appendChild(createCell(alert['effective-date']));
    
        table.appendChild(row);
    
        // get remaining alerts
        populateTableRecursive(alerts.slice(1), table);
    }

    function populateTable(alerts) {
        const tableSection = document.getElementById('table-section');
        const table = document.createElement('table');
    
        // table header row
        const headerRow = document.createElement('tr');
        const headers = ['Urgency', 'Type', 'Category', 'Product Name', 'Effective Date'];
        headers.forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText;
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);
    
        // clear previous content
        tableSection.innerHTML = '';
    
        // call recursive function
        populateTableRecursive(alerts, table);
    
        tableSection.appendChild(table);
    }
    
    

    // main entry when page loads
    fetchAlerts();
});

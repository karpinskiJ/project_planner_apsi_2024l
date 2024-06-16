const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
];

let currentMonthIndex = new Date().getMonth(); // Start with the current month

// Generate a random color for each project
const projectColors = {};

function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function createTimelineTable(projects) {
    const currentMonth = monthNames[currentMonthIndex];
    const daysInMonth = new Date(2024, currentMonthIndex + 1, 0).getDate();
    const thead = document.querySelector('#timeline-table thead tr');
    const tbody = document.getElementById('timeline-body');
    const legend = document.getElementById('legend');

    // Clear existing headers and rows
    thead.innerHTML = '<th>User</th>';
    tbody.innerHTML = '';
    legend.innerHTML = '';

    // Populate headers
    for (let day = 1; day <= daysInMonth; day++) {
        const th = document.createElement('th');
        th.textContent = day;
        thead.appendChild(th);
    }

    // Populate rows
    projects.forEach((project) => {
        const row = document.createElement('tr');
        const userCell = document.createElement('td');
        userCell.textContent = project.user;
        row.appendChild(userCell);

        for (let day = 1; day <= daysInMonth; day++) {
            const cell = document.createElement('td');
            const dateStr = `2024-${String(currentMonthIndex + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const assignments = project.assignments.filter(a => dateStr >= a.start && dateStr <= a.end);
            let currentTop = 0;
            assignments.forEach((assignment) => {
                const projectDiv = document.createElement('div');
                projectDiv.className = 'project';

                if (!projectColors[assignment.project]) {
                    projectColors[assignment.project] = getRandomColor();
                }

                projectDiv.style.backgroundColor = projectColors[assignment.project];
                projectDiv.dataset.project = assignment.project;
                projectDiv.dataset.allocation = assignment.allocation_part;

                // Set height and top position based on allocation part
                const allocationPercentage = parseInt(assignment.allocation_part, 10);
                projectDiv.style.height = `${allocationPercentage}%`;
                projectDiv.style.top = `${currentTop}%`;
                currentTop += allocationPercentage;

                projectDiv.addEventListener('mouseover', showInfo);
                projectDiv.addEventListener('mouseout', hideInfo);
                cell.appendChild(projectDiv);
            });
            row.appendChild(cell);
        }

        tbody.appendChild(row);
    });

    // Create legend
    for (const [project, color] of Object.entries(projectColors)) {
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';

        const colorBox = document.createElement('div');
        colorBox.className = 'legend-color';
        colorBox.style.backgroundColor = color;

        const projectName = document.createElement('span');
        projectName.textContent = project;

        legendItem.appendChild(colorBox);
        legendItem.appendChild(projectName);
        legend.appendChild(legendItem);
    }

    document.getElementById('current-month').textContent = currentMonth;
}

function showInfo(event) {
    const infoBox = document.createElement('div');
    infoBox.className = 'info-box';
    infoBox.textContent = `${event.target.dataset.project} (Allocation: ${event.target.dataset.allocation})`;
    document.body.appendChild(infoBox);

    const rect = event.target.getBoundingClientRect();
    infoBox.style.left = `${rect.left + window.scrollX}px`;
    infoBox.style.top = `${rect.top + window.scrollY - infoBox.offsetHeight}px`;

    event.target.infoBox = infoBox;
}

function hideInfo(event) {
    document.body.removeChild(event.target.infoBox);
    event.target.infoBox = null;
}

function previousMonth() {
    if (currentMonthIndex > 0) {
        currentMonthIndex--;
        createTimelineTable(projects);
    }
}

function nextMonth() {
    if (currentMonthIndex < 11) {
        currentMonthIndex++;
        createTimelineTable(projects);
    }
}

document.addEventListener('DOMContentLoaded', () => createTimelineTable(projects));

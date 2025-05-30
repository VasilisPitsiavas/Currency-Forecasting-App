// fetch_handler.js

document.addEventListener('DOMContentLoaded', () => {
    const fetchForm = document.getElementById('fetch-form');
    if (fetchForm) {
        fetchForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch('/fetch', {
                    method: 'POST',
                    body: JSON.stringify(data),  
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded' 
                    }
                });

                const result = await response.json();

                if (response.ok) {
                    showNotification(result.message, 'success');
                } else {
                    showNotification(result.error, 'error');
                }
            } catch (err) {
                showNotification('An unexpected error occurred.', 'error');
                console.error(err);
            }
        });
    }
});


function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
    notification.textContent = message;

    // Append to a specific notification area if available, or the body
    const notificationArea = document.getElementById('notification-area');
    if (notificationArea) {
        notificationArea.appendChild(notification);
    } else {
        document.body.prepend(notification);
    }

    setTimeout(() => notification.remove(), 5000); // Remove after 5 seconds
}

window.toggleSidebar = function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    
    if (sidebar && mainContent) {
        sidebar.classList.toggle('closed'); 
        sidebar.classList.toggle('active'); 
        mainContent.classList.toggle('wide');
    }
};

window.toggleLogoutModal = function() {
    const modal = document.getElementById('logoutModal');
    if (modal) {
        modal.classList.toggle('show');
    }
};

window.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const logoutModal = document.getElementById('logoutModal');

    if (event.target === logoutModal) {
        logoutModal.classList.remove('show');
    }

    if (sidebar.classList.contains('active')) {
        if (!sidebar.contains(event.target) && !toggleBtn.contains(event.target)) {
            sidebar.classList.remove('active');
            sidebar.classList.add('closed');
            const mainContent = document.getElementById('main-content');
            if (mainContent) mainContent.classList.add('wide');
        }
    }
});
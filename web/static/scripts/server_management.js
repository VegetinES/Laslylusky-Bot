document.addEventListener('DOMContentLoaded', function() {
    initializeTabSystem();
    initializeCommandsSystem();
    initializePermissionsSystem();
    initializeLogsSystem();
    initializeTicketsSystem();
    initializeModals();
});

function initializeTabSystem() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
    });

    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            button.classList.add('active');
            document.getElementById(`${targetTab}-tab`).classList.add('active');
            
            resetCurrentStates();
            
            if (targetTab === 'permissions') {
                setTimeout(() => loadPermissionsData(), 100);
            } else if (targetTab === 'tickets') {
                setTimeout(() => loadTicketsData(), 100);
            } else if (targetTab === 'logs') {
                setTimeout(() => loadLogsData(), 100);
            } else if (targetTab === 'commands') {
                setTimeout(() => loadCommands(), 100);
            }
        });
    });
}

function initializeCommandsSystem() {
    loadCommands();
    
    document.getElementById('command-search')?.addEventListener('input', filterCommands);
    document.getElementById('select-all')?.addEventListener('click', selectAllCommands);
    document.getElementById('deselect-all')?.addEventListener('click', deselectAllCommands);
    document.getElementById('save-changes')?.addEventListener('click', saveCommandChanges);
    document.getElementById('cancel-changes')?.addEventListener('click', cancelCommandChanges);
}

let permissionsData = {};
let currentPermissionKey = null;
let currentPermissionDetails = null;
let rolesData = [];

function initializePermissionsSystem() {
    const createCustomPermissionBtn = document.getElementById('create-custom-permission-btn');
    const deletePermissionBtn = document.getElementById('delete-permission-btn');
    const permissionsSearchInput = document.getElementById('permissions-search');

    createCustomPermissionBtn?.addEventListener('click', openCreateCustomPermissionModal);
    deletePermissionBtn?.addEventListener('click', confirmDeletePermission);
    permissionsSearchInput?.addEventListener('input', filterPermissions);

    initializeCustomPermissionModal();
    initializePermissionDetailModal();
    initializeConfirmDeleteModal();
}

function initializeCustomPermissionModal() {
    const saveBtn = document.getElementById('save-custom-permission');
    const cancelBtn = document.getElementById('cancel-custom-permission');

    saveBtn?.addEventListener('click', createCustomPermission);
    cancelBtn?.addEventListener('click', closeAllModals);
}

function initializePermissionDetailModal() {
    const closeBtn = document.getElementById('close-permission-detail');
    const addRoleBtn = document.getElementById('add-permission-role');
    const addUserBtn = document.getElementById('add-permission-user');

    closeBtn?.addEventListener('click', closeAllModals);
    addRoleBtn?.addEventListener('click', addPermissionRole);
    addUserBtn?.addEventListener('click', addPermissionUser);
}

function initializeConfirmDeleteModal() {
    const confirmBtn = document.getElementById('confirm-delete-permission');
    const cancelBtn = document.getElementById('cancel-delete-permission');

    confirmBtn?.addEventListener('click', deleteCustomPermission);
    cancelBtn?.addEventListener('click', closeAllModals);
}

async function loadPermissionsData() {
    try {
        resetPermissionsState();
        const response = await fetch(`/api/server/${window.serverId}/permissions`);
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }
        
        permissionsData = data.permissions || {};
        renderPermissionsCategories();
    } catch (error) {
        console.error('Error loading permissions:', error);
        showToast('Error al cargar permisos', 'error');
        resetPermissionsState();
    }
}

function renderPermissionsCategories() {
    const container = document.getElementById('permissions-categories');
    
    if (Object.keys(permissionsData).length === 0) {
        container.innerHTML = '<div class="empty-state">No hay permisos configurados</div>';
        return;
    }
    
    const searchTerm = document.getElementById('permissions-search').value.toLowerCase();
    
    const categoriesHtml = Object.entries(permissionsData).map(([categoryKey, categoryData]) => {
        if (!categoryData || !categoryData.permissions) return '';
        
        const permissionsHtml = Object.entries(categoryData)
            .filter(([key]) => key !== 'name' && key !== 'description' && key !== 'permissions')
            .filter(([permissionKey, permissionData]) => {
                if (!searchTerm) return true;
                return permissionKey.toLowerCase().includes(searchTerm) || 
                       (permissionData.base_permission && permissionData.base_permission.toLowerCase().includes(searchTerm));
            })
            .map(([permissionKey, permissionData]) => {
                const count = permissionData.count || 0;
                const typeIcon = permissionData.type === 'roles' ? '👥' : '👤';
                const typeName = permissionData.type === 'roles' ? 'Roles' : 'Usuarios';
                
                return `
                    <div class="permission-item" data-permission="${permissionKey}">
                        <div class="permission-info">
                            <div class="permission-name">${typeIcon} ${permissionData.base_permission} - ${typeName}</div>
                            <div class="permission-type">${getPermissionDescription(permissionKey)}</div>
                        </div>
                        <div class="permission-count ${count === 0 ? 'zero' : ''}">${count}</div>
                    </div>
                `;
            })
            .join('');
        
        if (!permissionsHtml && searchTerm) return '';
        
        return `
            <div class="permission-category">
                <div class="category-header" data-category="${categoryKey}">
                    <div>
                        <div class="category-name">
                            ${getCategoryIcon(categoryKey)} ${categoryData.name || categoryKey}
                        </div>
                        <div class="category-description">${categoryData.description || ''}</div>
                    </div>
                    <div class="category-toggle">›</div>
                </div>
                <div class="category-permissions" data-category="${categoryKey}">
                    ${permissionsHtml}
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = categoriesHtml;
    
    setupPermissionsCategoryListeners();
    setupPermissionsItemListeners();
}

function getCategoryIcon(categoryKey) {
    const icons = {
        'admin': '🛡️',
        'mg-srv': '⚙️',
        'custom': '🔧'
    };
    return icons[categoryKey] || '🔑';
}

function getPermissionDescription(permissionKey) {
    const descriptions = {
        'admin-roles': 'Control total del bot',
        'admin-users': 'Control total del bot',
        'mg-srv-roles': 'Gestión del servidor',
        'mg-srv-users': 'Gestión del servidor'
    };
    
    if (descriptions[permissionKey]) {
        return descriptions[permissionKey];
    }
    
    const parts = permissionKey.split('-');
    const basePerm = parts.slice(0, -1).join('-');
    const type = parts[parts.length - 1];
    return `Permiso personalizado ${basePerm}`;
}

function setupPermissionsCategoryListeners() {
    document.querySelectorAll('.category-header').forEach(header => {
        header.addEventListener('click', function() {
            const categoryKey = this.getAttribute('data-category');
            const categoryPerms = document.querySelector(`.category-permissions[data-category="${categoryKey}"]`);
            
            const isExpanded = categoryPerms.classList.contains('expanded');
            
            document.querySelectorAll('.category-permissions').forEach(perms => {
                perms.classList.remove('expanded');
            });
            document.querySelectorAll('.category-header').forEach(h => {
                h.classList.remove('expanded');
            });
            
            if (!isExpanded) {
                categoryPerms.classList.add('expanded');
                this.classList.add('expanded');
            }
        });
    });
}

function setupPermissionsItemListeners() {
    document.querySelectorAll('.permission-item').forEach(item => {
        item.addEventListener('click', function() {
            const permissionKey = this.getAttribute('data-permission');
            loadPermissionDetails(permissionKey);
        });
    });
}

async function loadPermissionDetails(permissionKey) {
    try {
        const response = await fetch(`/api/server/${window.serverId}/permissions/${permissionKey}`);
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }
        
        currentPermissionKey = permissionKey;
        currentPermissionDetails = data;
        
        document.querySelectorAll('.permission-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-permission="${permissionKey}"]`).classList.add('active');
        
        renderPermissionEditor();
        
        if (data.type === 'roles') {
            await loadRolesForPermission();
        }
    } catch (error) {
        console.error('Error loading permission details:', error);
        showToast('Error al cargar detalles del permiso', 'error');
    }
}

function renderPermissionEditor() {
    const editorTitle = document.getElementById('permissions-editor-title');
    const editorContent = document.getElementById('permissions-editor-content');
    const deleteBtn = document.getElementById('delete-permission-btn');
    
    if (!currentPermissionDetails) {
        editorContent.innerHTML = `
            <div class="welcome-state">
                <div class="welcome-icon">🔑</div>
                <h3>Gestión de Permisos</h3>
                <p>Selecciona una categoría y permiso para configurar quién puede usar las funciones específicas del bot.</p>
                <div class="welcome-features">
                    <div class="feature-item">
                        <span class="feature-icon">👥</span>
                        <span>Gestión de roles</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">👤</span>
                        <span>Gestión de usuarios</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">🛡️</span>
                        <span>Control granular</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">⚙️</span>
                        <span>Permisos personalizados</span>
                    </div>
                </div>
            </div>
        `;
        editorTitle.textContent = 'Selecciona un permiso para configurar';
        deleteBtn.style.display = 'none';
        return;
    }
    
    const typeIcon = currentPermissionDetails.type === 'roles' ? '👥' : '👤';
    const typeName = currentPermissionDetails.type === 'roles' ? 'Roles' : 'Usuarios';
    
    editorTitle.textContent = `${typeIcon} ${currentPermissionDetails.base_permission} - ${typeName}`;
    
    const isCustomPermission = !['admin', 'mg-srv'].includes(currentPermissionDetails.base_permission);
    deleteBtn.style.display = isCustomPermission ? 'block' : 'none';
    
    editorContent.innerHTML = `
        <div class="permission-detail-content">
            <div class="permission-description">
                <p><strong>${typeIcon} ${currentPermissionDetails.base_permission} - ${typeName}:</strong></p>
                <p>${currentPermissionDetails.description}</p>
            </div>
            
            <div class="permission-items-section">
                <h4>${typeIcon} ${typeName} con este permiso</h4>
                <div class="permission-items-list" id="current-permission-items">
                    ${renderCurrentPermissionItems()}
                </div>
            </div>
            
            <div class="add-permission-section">
                <h4>➕ Añadir al permiso</h4>
                <div class="add-permission-controls">
                    ${currentPermissionDetails.type === 'roles' ? `
                        <div class="form-group">
                            <label>👥 Añadir rol</label>
                            <select id="permission-role-select" class="form-select">
                                <option value="">Selecciona un rol...</option>
                            </select>
                            <button class="btn-secondary" id="add-permission-role">
                                <span class="btn-icon">➕</span>
                                Añadir Rol
                            </button>
                        </div>
                    ` : `
                        <div class="form-group">
                            <label>👤 Añadir usuario</label>
                            <input type="text" id="permission-user-input" class="form-input" placeholder="ID del usuario">
                            <button class="btn-secondary" id="add-permission-user">
                                <span class="btn-icon">➕</span>
                                Añadir Usuario
                            </button>
                        </div>
                    `}
                </div>
            </div>
        </div>
    `;
    
    if (currentPermissionDetails.type === 'roles') {
        populateRoleSelect();
    }
    
    setupPermissionEditorListeners();
}

function renderCurrentPermissionItems() {
    if (!currentPermissionDetails.items || currentPermissionDetails.items.length === 0) {
        return '<div class="empty-state">No hay elementos configurados</div>';
    }
    
    return currentPermissionDetails.items.map(item => `
        <div class="permission-item-element">
            <div class="item-info">
                ${currentPermissionDetails.type === 'roles' ? 
                    `<div class="item-color" style="background-color: ${item.color};"></div>` :
                    `<img src="${item.avatar}" alt="Avatar" class="item-avatar">`
                }
                <div class="item-name">${item.name}</div>
            </div>
            <div class="item-actions">
                <button class="btn-danger btn-small" onclick="removePermissionItem(${item.id})">
                    <span class="btn-icon">✕</span>
                    Eliminar
                </button>
            </div>
        </div>
    `).join('');
}

function renderTicketPermissionItems(type) {
    const rolesContainer = document.getElementById(`${type}-roles-list`);
    const usersContainer = document.getElementById(`${type}-users-list`);
    
    const permissions = currentTicketConfig.permissions[type];
    
    rolesContainer.innerHTML = permissions.roles.map(roleId => {
        const role = rolesData.find(r => r.id === String(roleId));
        return `
            <div class="selected-item">
                ${role ? role.name : `Rol ID: ${roleId}`}
                <button class="remove-btn" onclick="removeRole('${type}', '${roleId}')">✕</button>
            </div>
        `;
    }).join('');
    
    usersContainer.innerHTML = permissions.users.map(userId => `
        <div class="selected-item">
            Usuario ID: ${userId}
            <button class="remove-btn" onclick="removeUser('${type}', '${userId}')">✕</button>
        </div>
    `).join('');
}

function renderTicketPermissionItems(type) {
    const rolesContainer = document.getElementById(`${type}-roles-list`);
    const usersContainer = document.getElementById(`${type}-users-list`);
    
    const permissions = currentTicketConfig.permissions[type];
    
    rolesContainer.innerHTML = permissions.roles.map(roleId => {
        const role = rolesData.find(r => r.id === String(roleId));
        return `
            <div class="selected-item">
                ${role ? role.name : `Rol ID: ${roleId}`}
                <button class="remove-btn" onclick="removeRole('${type}', '${roleId}')">✕</button>
            </div>
        `;
    }).join('');
    
    usersContainer.innerHTML = permissions.users.map(userId => `
        <div class="selected-item">
            Usuario ID: ${userId}
            <button class="remove-btn" onclick="removeUser('${type}', '${userId}')">✕</button>
        </div>
    `).join('');
}

function renderPermissionItems() {
    if (!currentPermissionDetails.items || currentPermissionDetails.items.length === 0) {
        return '<div class="empty-state">No hay elementos configurados</div>';
    }
    
    return currentPermissionDetails.items.map(item => `
        <div class="permission-item-element">
            <div class="item-info">
                ${currentPermissionDetails.type === 'roles' ? 
                    `<div class="item-color" style="background-color: ${item.color};"></div>` :
                    `<img src="${item.avatar}" alt="Avatar" class="item-avatar">`
                }
                <div class="item-name">${item.name}</div>
            </div>
            <div class="item-actions">
                <button class="btn-danger btn-small" onclick="removePermissionItem(${item.id})">
                    <span class="btn-icon">✕</span>
                    Eliminar
                </button>
            </div>
        </div>
    `).join('');
}

function setupPermissionEditorListeners() {
    const addRoleBtn = document.getElementById('add-permission-role');
    const addUserBtn = document.getElementById('add-permission-user');
    
    addRoleBtn?.addEventListener('click', addPermissionRole);
    addUserBtn?.addEventListener('click', addPermissionUser);
}

async function loadRolesForPermission() {
    if (rolesData.length === 0) {
        await loadRolesData();
    }
    populateRoleSelect();
}

async function loadRolesData() {
    try {
        const response = await fetch(`/api/server/${window.serverId}/roles`);
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }
        
        rolesData = data.roles || [];
    } catch (error) {
        console.error('Error loading roles:', error);
        showToast('Error al cargar roles', 'error');
    }
}

function populateRoleSelect() {
    const roleSelect = document.getElementById('permission-role-select');
    if (!roleSelect) return;
    
    roleSelect.innerHTML = '<option value="">Selecciona un rol...</option>';
    
    rolesData.forEach(role => {
        const option = new Option(role.name, role.id);
        roleSelect.add(option);
    });
}

async function addPermissionRole() {
    const roleSelect = document.getElementById('permission-role-select');
    const roleId = roleSelect.value;
    
    if (!roleId) {
        showToast('Selecciona un rol', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/server/${window.serverId}/permissions/${currentPermissionKey}/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: roleId,
                item_type: 'role'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Rol añadido correctamente', 'success');
            roleSelect.value = '';
            loadPermissionDetails(currentPermissionKey);
            loadPermissionsData();
        } else {
            showToast(result.message || 'Error al añadir rol', 'error');
        }
    } catch (error) {
        console.error('Error adding role:', error);
        showToast('Error al añadir rol', 'error');
    }
}

async function addPermissionUser() {
    const userInput = document.getElementById('permission-user-input');
    const userId = userInput.value.trim();
    
    if (!userId || !userId.match(/^\d+$/)) {
        showToast('Ingresa un ID de usuario válido', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/server/${window.serverId}/permissions/${currentPermissionKey}/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: userId,
                item_type: 'user'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Usuario añadido correctamente', 'success');
            userInput.value = '';
            loadPermissionDetails(currentPermissionKey);
            loadPermissionsData();
        } else {
            showToast(result.message || 'Error al añadir usuario', 'error');
        }
    } catch (error) {
        console.error('Error adding user:', error);
        showToast('Error al añadir usuario', 'error');
    }
}

async function removePermissionItem(itemId) {
    try {
        const response = await fetch(`/api/server/${window.serverId}/permissions/${currentPermissionKey}/remove`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: itemId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Elemento eliminado correctamente', 'success');
            loadPermissionDetails(currentPermissionKey);
            loadPermissionsData();
        } else {
            showToast(result.message || 'Error al eliminar elemento', 'error');
        }
    } catch (error) {
        console.error('Error removing item:', error);
        showToast('Error al eliminar elemento', 'error');
    }
}

function openCreateCustomPermissionModal() {
    const modal = document.getElementById('create-custom-permission-modal');
    const overlay = document.getElementById('modal-overlay');
    
    document.getElementById('custom-permission-name').value = '';
    
    modal.classList.add('active');
    overlay.classList.add('active');
}

async function createCustomPermission() {
    const permissionName = document.getElementById('custom-permission-name').value.trim();
    
    if (!permissionName) {
        showToast('Ingresa un nombre para el permiso', 'error');
        return;
    }
    
    if (!permissionName.match(/^[a-z0-9-]+$/)) {
        showToast('Solo se permiten letras minúsculas, números y guiones', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/server/${window.serverId}/permissions/custom`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                permission_name: permissionName
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Permiso personalizado creado correctamente', 'success');
            closeAllModals();
            loadPermissionsData();
        } else {
            showToast(result.message || 'Error al crear permiso personalizado', 'error');
        }
    } catch (error) {
        console.error('Error creating custom permission:', error);
        showToast('Error al crear permiso personalizado', 'error');
    }
}

function confirmDeletePermission() {
    if (!currentPermissionDetails || ['admin', 'mg-srv'].includes(currentPermissionDetails.base_permission)) {
        showToast('No se pueden eliminar permisos del sistema', 'error');
        return;
    }
    
    const modal = document.getElementById('confirm-delete-permission-modal');
    const overlay = document.getElementById('modal-overlay');
    
    modal.classList.add('active');
    overlay.classList.add('active');
}

async function deleteCustomPermission() {
    if (!currentPermissionDetails) return;
    
    try {
        const response = await fetch(`/api/server/${window.serverId}/permissions/custom/${currentPermissionDetails.base_permission}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Permiso personalizado eliminado correctamente', 'success');
            closeAllModals();
            loadPermissionsData();
            
            currentPermissionKey = null;
            currentPermissionDetails = null;
            renderPermissionEditor();
        } else {
            showToast(result.message || 'Error al eliminar permiso personalizado', 'error');
        }
    } catch (error) {
        console.error('Error deleting custom permission:', error);
        showToast('Error al eliminar permiso personalizado', 'error');
    }
}

function filterPermissions() {
    renderPermissionsCategories();
}

let logsData = {};
let currentLogConfig = null;
let originalLogConfig = null;
let currentEditingLog = null;
let logChangeHistory = [];
let currentLogHistoryIndex = -1;
let hasLogChanges = false;

function initializeLogsSystem() {
    const toggleLogsPreviewBtn = document.getElementById('toggle-logs-preview-btn');
    const closeLogsPreviewBtn = document.getElementById('close-logs-preview-btn');
    const saveLogBtn = document.getElementById('save-log-btn');
    const cancelLogsEditBtn = document.getElementById('cancel-logs-edit-btn');
    const logsUndoBtn = document.getElementById('logs-undo-btn');
    const logsSearchInput = document.getElementById('logs-search');

    toggleLogsPreviewBtn?.addEventListener('click', toggleLogsPreview);
    closeLogsPreviewBtn?.addEventListener('click', closeLogsPreview);
    saveLogBtn?.addEventListener('click', saveCurrentLog);
    cancelLogsEditBtn?.addEventListener('click', cancelLogEdit);
    logsUndoBtn?.addEventListener('click', undoLastLogChange);
    logsSearchInput?.addEventListener('input', filterLogs);

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            filterLogs();
        });
    });
}

let ticketsData = [];
let currentTicketConfig = null;
let originalTicketConfig = null;
let currentEditingTicket = null;
let channelsData = [];
let currentPermissionType = 'manage';
let isEditingButton = false;
let editingButtonIndex = -1;
let currentMessageType = 'open_message';
let hasTicketChanges = false;

let changeHistory = [];
let currentHistoryIndex = -1;

function initializeTicketsSystem() {
    const createTicketBtn = document.getElementById('create-ticket-btn');
    const togglePreviewBtn = document.getElementById('toggle-preview-btn');
    const closePreviewBtn = document.getElementById('close-preview-btn');
    const saveTicketBtn = document.getElementById('save-ticket-btn');
    const cancelEditBtn = document.getElementById('cancel-edit-btn');
    const undoBtn = document.getElementById('undo-btn');

    createTicketBtn?.addEventListener('click', createNewTicket);
    togglePreviewBtn?.addEventListener('click', togglePreview);
    closePreviewBtn?.addEventListener('click', closePreview);
    saveTicketBtn?.addEventListener('click', saveCurrentTicket);
    cancelEditBtn?.addEventListener('click', cancelTicketEdit);
    undoBtn?.addEventListener('click', undoLastChange);
}

function initializeModals() {
    const modals = document.querySelectorAll('.modal');
    const overlay = document.getElementById('modal-overlay');
    const closeButtons = document.querySelectorAll('.modal-close');

    closeButtons.forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });

    overlay?.addEventListener('click', closeAllModals);

    initializeChannelSelectModal();
    initializePermissionsModal();
    initializeRoleSelectModal();
    initializeMessageConfigModal();
    initializeButtonConfigModal();
    initializeLogChannelSelectModal();
    initializeLogMessageConfigModal();
    initializeLogFieldConfigModal();
}

let commandsData = {};
let commandsChanges = {};

function saveSnapshot(action) {
    if (!currentTicketConfig) return;
    
    const snapshot = {
        config: JSON.parse(JSON.stringify(currentTicketConfig)),
        action: action,
        timestamp: Date.now()
    };
    
    changeHistory = changeHistory.slice(0, currentHistoryIndex + 1);
    changeHistory.push(snapshot);
    currentHistoryIndex = changeHistory.length - 1;
    
    updateUndoButton();
    checkForChanges();
}

function saveLogSnapshot(action) {
    if (!currentLogConfig) return;
    
    const snapshot = {
        config: JSON.parse(JSON.stringify(currentLogConfig)),
        action: action,
        timestamp: Date.now()
    };
    
    logChangeHistory = logChangeHistory.slice(0, currentLogHistoryIndex + 1);
    logChangeHistory.push(snapshot);
    currentLogHistoryIndex = logChangeHistory.length - 1;
    
    updateLogUndoButton();
    checkForLogChanges();
}

function undoLastChange() {
    if (currentHistoryIndex <= 0) return;
    
    currentHistoryIndex--;
    currentTicketConfig = JSON.parse(JSON.stringify(changeHistory[currentHistoryIndex].config));
    
    renderTicketEditor();
    updatePreview();
    updateUndoButton();
    checkForChanges();
    showToast(`Deshecho: ${changeHistory[currentHistoryIndex + 1].action}`, 'info');
}

function undoLastLogChange() {
    if (currentLogHistoryIndex <= 0) return;
    
    currentLogHistoryIndex--;
    currentLogConfig = JSON.parse(JSON.stringify(logChangeHistory[currentLogHistoryIndex].config));
    
    renderLogEditor();
    updateLogsPreview();
    updateLogUndoButton();
    checkForLogChanges();
    showToast(`Deshecho: ${logChangeHistory[currentLogHistoryIndex + 1].action}`, 'info');
}

function updateUndoButton() {
    const undoBtn = document.getElementById('undo-btn');
    if (!undoBtn) return;
    
    if (currentHistoryIndex > 0) {
        undoBtn.style.display = 'block';
        undoBtn.textContent = `Deshacer: ${changeHistory[currentHistoryIndex].action}`;
        undoBtn.disabled = false;
    } else {
        undoBtn.style.display = 'none';
        undoBtn.disabled = true;
    }
}

function updateLogUndoButton() {
    const undoBtn = document.getElementById('logs-undo-btn');
    if (!undoBtn) return;
    
    if (currentLogHistoryIndex > 0) {
        undoBtn.style.display = 'block';
        undoBtn.textContent = `Deshacer: ${logChangeHistory[currentLogHistoryIndex].action}`;
        undoBtn.disabled = false;
    } else {
        undoBtn.style.display = 'none';
        undoBtn.disabled = true;
    }
}

function resetHistory() {
    changeHistory = [];
    currentHistoryIndex = -1;
    hasTicketChanges = false;
    updateUndoButton();
    updateSaveButton();
}

function resetLogHistory() {
    logChangeHistory = [];
    currentLogHistoryIndex = -1;
    hasLogChanges = false;
    updateLogUndoButton();
    updateLogSaveButton();
}

function checkForChanges() {
    if (!currentTicketConfig) {
        hasTicketChanges = false;
        updateSaveButton();
        return;
    }
    
    if (!originalTicketConfig) {
        hasTicketChanges = true;
        updateSaveButton();
        return;
    }
    
    const currentConfigStr = JSON.stringify(currentTicketConfig);
    const originalConfigStr = JSON.stringify(originalTicketConfig);
    
    hasTicketChanges = currentConfigStr !== originalConfigStr;
    updateSaveButton();
}

function checkForLogChanges() {
    if (!currentLogConfig || !originalLogConfig) {
        hasLogChanges = false;
        updateLogSaveButton();
        return;
    }
    
    const currentConfigStr = JSON.stringify(currentLogConfig);
    const originalConfigStr = JSON.stringify(originalLogConfig);
    
    hasLogChanges = currentConfigStr !== originalConfigStr;
    updateLogSaveButton();
}

function updateSaveButton() {
    const saveBtn = document.getElementById('save-ticket-btn');
    if (!saveBtn) return;
    
    const cancelBtn = document.getElementById('cancel-edit-btn');
    
    if (hasTicketChanges && currentTicketConfig) {
        saveBtn.style.display = 'block';
        saveBtn.disabled = false;
        
        if (!originalTicketConfig) {
            saveBtn.innerHTML = '<span class="btn-icon">💾</span> Crear Ticket';
        } else {
            saveBtn.innerHTML = '<span class="btn-icon">💾</span> Guardar Cambios';
        }
        
        if (cancelBtn) {
            cancelBtn.style.display = 'block';
        }
    } else {
        saveBtn.style.display = 'none';
        saveBtn.disabled = true;
        
        if (cancelBtn && !currentTicketConfig) {
            cancelBtn.style.display = 'none';
        }
    }
}

function updateLogSaveButton() {
    const saveBtn = document.getElementById('save-log-btn');
    if (!saveBtn) return;
    
    if (hasLogChanges && currentLogConfig) {
        saveBtn.style.display = 'block';
        saveBtn.disabled = false;
    } else {
        saveBtn.style.display = 'none';
        saveBtn.disabled = true;
    }
}

function updatePreviewButton() {
    const togglePreviewBtn = document.getElementById('toggle-preview-btn');
    if (!togglePreviewBtn) return;
    
    if (currentTicketConfig) {
        togglePreviewBtn.style.display = 'block';
    } else {
        togglePreviewBtn.style.display = 'none';
        closePreview();
    }
}

function updateLogsPreviewButton() {
    const togglePreviewBtn = document.getElementById('toggle-logs-preview-btn');
    if (!togglePreviewBtn) return;
    
    if (currentLogConfig) {
        togglePreviewBtn.style.display = 'block';
    } else {
        togglePreviewBtn.style.display = 'none';
        closeLogsPreview();
    }
}

async function loadCommands() {
    try {
        resetCommandsState();
        const response = await fetch(`/api/server/${window.serverId}/commands`);
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }
        
        commandsData = data;
        renderCommands();
    } catch (error) {
        console.error('Error loading commands:', error);
        showToast('Error al cargar comandos', 'error');
        resetCommandsState();
    }
}

function renderCommands() {
    const container = document.getElementById('commands-container');
    
    if (!commandsData.commands || Object.keys(commandsData.commands).length === 0) {
        container.innerHTML = '<div class="loading-state"><p>No hay comandos configurados</p></div>';
        return;
    }
    
    const commandsHtml = Object.entries(commandsData.commands).map(([command, info]) => `
        <div class="command-item ${commandsChanges[command] ? 'changed' : ''} ${!info.can_modify ? 'disabled' : ''}" data-command="${command}">
            <div class="command-header">
                <h3 class="command-name">${command}</h3>
                <div class="command-toggle ${info.active ? 'active' : ''} ${!info.can_modify ? 'disabled' : ''}" 
                     data-command="${command}" ${!info.can_modify ? 'title="Este comando no puede ser modificado"' : ''}>
                    <div class="toggle-slider"></div>
                </div>
            </div>
            <div class="command-status">
                <span class="status-badge ${info.active ? 'status-active' : 'status-inactive'}">
                    ${info.active ? 'Activo' : 'Inactivo'}
                </span>
                ${info.default ? '<span class="status-badge status-default">Por defecto</span>' : ''}
            </div>
        </div>
    `).join('');
    
    container.innerHTML = commandsHtml;
    
    document.querySelectorAll('.command-toggle:not(.disabled)').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const command = this.getAttribute('data-command');
            const currentState = commandsData.commands[command].active;
            
            commandsChanges[command] = !currentState;
            commandsData.commands[command].active = !currentState;
            
            this.classList.toggle('active');
            this.closest('.command-item').classList.add('changed');
            
            const statusBadge = this.closest('.command-item').querySelector('.status-badge:not(.status-default)');
            statusBadge.className = `status-badge ${!currentState ? 'status-active' : 'status-inactive'}`;
            statusBadge.textContent = !currentState ? 'Activo' : 'Inactivo';
            
            updateSaveActions();
        });
    });
}

function filterCommands() {
    const searchTerm = document.getElementById('command-search').value.toLowerCase();
    const commandItems = document.querySelectorAll('.command-item');
    
    commandItems.forEach(item => {
        const commandName = item.querySelector('.command-name').textContent.toLowerCase();
        if (commandName.includes(searchTerm)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

function selectAllCommands() {
    document.querySelectorAll('.command-toggle:not(.disabled):not(.active)').forEach(toggle => {
        toggle.click();
    });
}

function deselectAllCommands() {
    document.querySelectorAll('.command-toggle:not(.disabled).active').forEach(toggle => {
        toggle.click();
    });
}

function updateSaveActions() {
    const changesCount = Object.keys(commandsChanges).length;
    const saveActions = document.getElementById('save-actions');
    const changesCountElement = document.querySelector('.changes-count');
    
    if (changesCount > 0) {
        saveActions.style.display = 'flex';
        changesCountElement.textContent = changesCount;
    } else {
        saveActions.style.display = 'none';
    }
}

async function saveCommandChanges() {
    try {
        const response = await fetch(`/api/server/${window.serverId}/commands`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(commandsChanges)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Comandos actualizados correctamente', 'success');
            commandsChanges = {};
            updateSaveActions();
            document.querySelectorAll('.command-item.changed').forEach(item => {
                item.classList.remove('changed');
            });
        } else {
            showToast(result.error || 'Error al actualizar comandos', 'error');
        }
    } catch (error) {
        console.error('Error saving commands:', error);
        showToast('Error al guardar comandos', 'error');
    }
}

function cancelCommandChanges() {
    commandsChanges = {};
    loadCommands();
    updateSaveActions();
}

async function loadLogsData() {
    try {
        resetLogsState();
        const response = await fetch(`/api/server/${window.serverId}/logs`);
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }
        
        logsData = data.logs || {};
        renderLogsList();
    } catch (error) {
        console.error('Error loading logs:', error);
        showToast('Error al cargar logs', 'error');
        resetLogsState();
    }
}

function renderLogsList() {
    const container = document.getElementById('logs-list');
    
    if (Object.keys(logsData).length === 0) {
        container.innerHTML = '<div class="empty-state">No hay logs configurados</div>';
        return;
    }
    
    const activeFilter = document.querySelector('.filter-btn.active').getAttribute('data-filter');
    const searchTerm = document.getElementById('logs-search').value.toLowerCase();
    
    const filteredLogs = Object.entries(logsData).filter(([logType, logConfig]) => {
        const matchesSearch = logConfig.name.toLowerCase().includes(searchTerm) || 
                             logType.toLowerCase().includes(searchTerm);
        
        if (!matchesSearch) return false;
        
        if (activeFilter === 'activated') return logConfig.activated;
        if (activeFilter === 'deactivated') return !logConfig.activated;
        return true;
    });
    
    const logsHtml = filteredLogs.map(([logType, logConfig]) => `
        <div class="log-item ${logConfig.activated ? 'activated' : 'deactivated'}" data-log-type="${logType}">
            <div class="log-name">
                <span class="status-indicator ${logConfig.activated ? 'active' : 'inactive'}"></span>
                ${logConfig.name}
            </div>
            <div class="log-details">
                <div class="log-status">
                    <span>Estado: ${logConfig.activated ? 'Activo' : 'Inactivo'}</span>
                </div>
                <div>Canal: ${logConfig.channel_name}</div>
                <div>Tipo: ${logConfig.message_type}</div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = logsHtml;
    
    document.querySelectorAll('.log-item').forEach(item => {
        item.addEventListener('click', function() {
            const logType = this.getAttribute('data-log-type');
            loadLogConfig(logType);
        });
    });
}

function filterLogs() {
    renderLogsList();
}

async function loadLogConfig(logType) {
    try {
        const response = await fetch(`/api/server/${window.serverId}/logs/${logType}`);
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }
        
        currentLogConfig = data;
        originalLogConfig = JSON.parse(JSON.stringify(data));
        currentEditingLog = logType;
        
        resetLogHistory();
        saveLogSnapshot('Configuración cargada');
        
        document.querySelectorAll('.log-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-log-type="${logType}"]`).classList.add('active');
        
        renderLogEditor();
        updateLogsPreview();
        updateLogsPreviewButton();
    } catch (error) {
        console.error('Error loading log config:', error);
        showToast('Error al cargar configuración del log', 'error');
    }
}

function renderLogEditor() {
    const editorTitle = document.getElementById('logs-editor-title');
    const editorContent = document.getElementById('logs-editor-content');
    const cancelBtn = document.getElementById('cancel-logs-edit-btn');
    
    if (!currentLogConfig) {
        editorContent.innerHTML = `
            <div class="welcome-state">
                <div class="welcome-icon">📋</div>
                <h3>Configuración de Logs</h3>
                <p>Selecciona un tipo de log para configurarlo y comenzar a registrar eventos en tu servidor.</p>
                <div class="welcome-features">
                    <div class="feature-item">
                        <span class="feature-icon">⚙️</span>
                        <span>Personalización completa</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">📝</span>
                        <span>Mensajes personalizados</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">🎨</span>
                        <span>Embeds y colores</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">📊</span>
                        <span>Campos y parámetros</span>
                    </div>
                </div>
            </div>
        `;
        editorTitle.textContent = 'Selecciona un log para configurar';
        cancelBtn.style.display = 'none';
        resetLogHistory();
        updateLogsPreviewButton();
        return;
    }
    
    const logInfo = currentLogConfig.log_info || {};
    editorTitle.textContent = `Configurando: ${logInfo.name || 'Log'}`;
    cancelBtn.style.display = 'block';
    
    const hasConfigOptions = logInfo.config_options && logInfo.config_options.length > 0;
    
    editorContent.innerHTML = `
        <div class="config-form">
            <div class="config-section">
                <h3>⚙️ Configuración Básica</h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label>📋 Canal de Logs</label>
                        <select id="log-channel-edit" class="form-select">
                            <option value="">Seleccionar canal...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>📊 Estado</label>
                        <div class="checkbox-group">
                            <input type="checkbox" id="log-activated" ${currentLogConfig.activated ? 'checked' : ''}>
                            <label for="log-activated">Activar este log</label>
                        </div>
                    </div>
                </div>
                ${hasConfigOptions ? `
                <div class="form-group">
                    <label>🔧 Opciones adicionales</label>
                    ${logInfo.config_options.map(option => `
                        <div class="checkbox-group">
                            <input type="checkbox" id="log-${option}" ${currentLogConfig[option] ? 'checked' : ''}>
                            <label for="log-${option}">
                                ${option === 'changedname' ? 'Seguir cambios de nombre' : ''}
                                ${option === 'changedperms' ? 'Seguir cambios de permisos' : ''}
                            </label>
                        </div>
                    `).join('')}
                </div>
                ` : ''}
            </div>
            
            <div class="config-section">
                <h3>📝 Configuración del Mensaje</h3>
                <p>Personaliza cómo se mostrarán los logs de ${logInfo.name || 'este tipo'}.</p>
                <button class="btn-primary" id="config-log-message-btn">
                    <span class="btn-icon">📝</span>
                    Configurar Mensaje
                </button>
            </div>
            
            <div class="config-section">
                <h3>🔧 Parámetros Disponibles</h3>
                <p>Estos son los parámetros que puedes usar en el mensaje:</p>
                <div class="parameters-grid" id="log-parameters-display">
                    ${(logInfo.params || []).map(param => `
                        <div class="parameter-item">${param}</div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    
    loadChannelsForLogEdit();
    setupLogConfigListeners();
}

async function loadChannelsForLogEdit() {
    if (channelsData.length === 0) {
        await loadChannelsData();
    }
    
    const logChannelSelect = document.getElementById('log-channel-edit');
    
    channelsData.forEach(channel => {
        const option = new Option(channel.name, channel.id);
        
        if (channel.id === String(currentLogConfig.log_channel)) {
            option.selected = true;
        }
        
        logChannelSelect.add(option);
    });
}

function setupLogConfigListeners() {
    document.getElementById('config-log-message-btn')?.addEventListener('click', () => {
        openLogMessageConfigModal();
    });
    
    document.getElementById('log-channel-edit')?.addEventListener('change', function() {
        saveLogSnapshot('Cambio de canal de logs');
        currentLogConfig.log_channel = parseInt(this.value);
        checkForLogChanges();
    });
    
    document.getElementById('log-activated')?.addEventListener('change', function() {
        saveLogSnapshot('Cambio de estado de activación');
        currentLogConfig.activated = this.checked;
        checkForLogChanges();
    });
    
    if (currentLogConfig.log_info && currentLogConfig.log_info.config_options) {
        currentLogConfig.log_info.config_options.forEach(option => {
            const checkbox = document.getElementById(`log-${option}`);
            if (checkbox) {
                checkbox.addEventListener('change', function() {
                    saveLogSnapshot(`Cambio de opción: ${option}`);
                    currentLogConfig[option] = this.checked;
                    checkForLogChanges();
                });
            }
        });
    }
}

function saveCurrentLog() {
    if (!currentLogConfig || !currentLogConfig.log_channel) {
        showToast('Debes seleccionar un canal para los logs', 'error');
        return;
    }
    
    const messageConfig = currentLogConfig.message || {};
    if (messageConfig.embed) {
        if (!messageConfig.description || !messageConfig.description.trim()) {
            showToast('El embed debe tener una descripción', 'error');
            return;
        }
    } else {
        if (!messageConfig.message || !messageConfig.message.trim()) {
            showToast('Debes configurar un mensaje de texto', 'error');
            return;
        }
    }
    
    saveLogConfig();
}

async function saveLogConfig() {
    try {
        const response = await fetch(`/api/server/${window.serverId}/logs/${currentEditingLog}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentLogConfig)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Log guardado correctamente', 'success');
            loadLogsData();
            
            originalLogConfig = JSON.parse(JSON.stringify(currentLogConfig));
            resetLogHistory();
            saveLogSnapshot('Configuración guardada');
        } else {
            showToast(result.error || 'Error al guardar log', 'error');
        }
    } catch (error) {
        console.error('Error saving log:', error);
        showToast('Error al guardar log', 'error');
    }
}

function cancelLogEdit() {
    currentLogConfig = null;
    originalLogConfig = null;
    currentEditingLog = null;
    resetLogHistory();
    
    document.querySelectorAll('.log-item').forEach(item => {
        item.classList.remove('active');
    });
    
    renderLogEditor();
    closeLogsPreview();
}

function toggleLogsPreview() {
    if (!currentLogConfig) {
        showToast('Selecciona un log para ver la vista previa', 'warning');
        return;
    }
    
    const preview = document.getElementById('logs-preview');
    const btn = document.getElementById('toggle-logs-preview-btn');
    
    if (preview.classList.contains('active')) {
        preview.classList.remove('active');
        btn.innerHTML = '<span class="btn-icon">👁️</span> Mostrar Vista Previa';
    } else {
        preview.classList.add('active');
        btn.innerHTML = '<span class="btn-icon">👁️</span> Ocultar Vista Previa';
        updateLogsPreview();
    }
}

function closeLogsPreview() {
    const preview = document.getElementById('logs-preview');
    const btn = document.getElementById('toggle-logs-preview-btn');
    
    preview.classList.remove('active');
    btn.innerHTML = '<span class="btn-icon">👁️</span> Mostrar Vista Previa';
}

async function updateLogsPreview() {
    if (!currentLogConfig) return;
    
    try {
        const response = await fetch(`/api/server/${window.serverId}/logs/preview`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                log_type: currentEditingLog,
                message_config: currentLogConfig.message || {}
            })
        });
        
        const preview = await response.json();
        
        if (preview.error) {
            showToast(preview.error, 'error');
            return;
        }
        
        const previewContent = document.getElementById('log-preview-content');
        const parametersContent = document.getElementById('log-parameters-list');
        
        if (preview.embed) {
            previewContent.innerHTML = generateLogEmbedPreview(preview);
        } else if (preview.content) {
            previewContent.innerHTML = `<div class="preview-content-text">${preview.content}</div>`;
        } else {
            previewContent.innerHTML = '<p>No hay configuración de mensaje</p>';
        }
        
        if (preview.params && preview.params.length > 0) {
            parametersContent.innerHTML = preview.params.map(param => 
                `<div class="parameter-item">${param}</div>`
            ).join('');
        } else {
            parametersContent.innerHTML = '<p>No hay parámetros disponibles</p>';
        }
        
    } catch (error) {
        console.error('Error updating logs preview:', error);
    }
}

function generateLogEmbedPreview(preview) {
    const embed = preview.embed;
    const borderColor = embed.color || '#3498db';
    
    let html = `<div class="preview-embed" style="border-left-color: ${borderColor};">`;
    
    if (embed.title) {
        html += `<div class="embed-title">${embed.title}</div>`;
    }
    
    if (embed.description) {
        html += `<div class="embed-description">${embed.description}</div>`;
    }
    
    if (embed.fields && embed.fields.length > 0) {
        html += '<div class="embed-fields">';
        embed.fields.forEach(field => {
            html += `
                <div class="embed-field ${field.inline ? 'inline' : ''}">
                    <div class="embed-field-name">${field.name}</div>
                    <div class="embed-field-value">${field.value}</div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    if (embed.footer) {
        html += `<div class="embed-footer">${embed.footer}</div>`;
    }
    
    html += '</div>';
    
    if (preview.content) {
        html = `<div class="preview-content-text">${preview.content}</div>` + html;
    }
    
    return html;
}

async function loadTicketsData() {
    try {
        const response = await fetch(`/api/server/${window.serverId}/tickets`);
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }
        
        ticketsData = data.tickets || [];
        renderTicketsList();
    } catch (error) {
        console.error('Error loading tickets:', error);
        showToast('Error al cargar tickets', 'error');
    }
}

function renderTicketsList() {
    const container = document.getElementById('tickets-list');
    
    if (ticketsData.length === 0) {
        container.innerHTML = '<div class="empty-state">No hay tickets configurados</div>';
        return;
    }
    
    const ticketsHtml = ticketsData.map(ticket => `
        <div class="ticket-item" data-channel-id="${ticket.channel_id}">
            <div class="ticket-name">
                🎫 ${ticket.channel_name}
            </div>
            <div class="ticket-details">
                <div>📋 Logs: ${ticket.log_channel_name}</div>
                <div>🔘 ${ticket.buttons_count} botón(es)</div>
                <div>🔒 ${ticket.has_permissions ? 'Configurado' : 'Sin configurar'}</div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = ticketsHtml;
    
    document.querySelectorAll('.ticket-item').forEach(item => {
        item.addEventListener('click', function() {
            const channelId = this.getAttribute('data-channel-id');
            loadTicketConfig(channelId);
        });
    });
}

async function loadTicketConfig(channelId) {
    try {
        const response = await fetch(`/api/server/${window.serverId}/tickets/${channelId}`);
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }
        
        currentTicketConfig = data.config;
        originalTicketConfig = JSON.parse(JSON.stringify(data.config));
        currentEditingTicket = channelId;
        
        resetHistory();
        saveSnapshot('Configuración cargada');
        
        document.querySelectorAll('.ticket-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-channel-id="${channelId}"]`).classList.add('active');
        
        renderTicketEditor();
        updatePreview();
        updatePreviewButton();
        checkForChanges();
    } catch (error) {
        console.error('Error loading ticket config:', error);
        showToast('Error al cargar configuración del ticket', 'error');
    }
}

function renderTicketEditor() {
    const editorTitle = document.getElementById('editor-title');
    const editorContent = document.getElementById('editor-content');
    const cancelBtn = document.getElementById('cancel-edit-btn');
    
    if (!currentTicketConfig) {
        editorContent.innerHTML = `
            <div class="welcome-state">
                <div class="welcome-icon">🎫</div>
                <h3>Configuración de Tickets</h3>
                <p>Selecciona un ticket existente para editarlo o crea uno nuevo para comenzar.</p>
                <div class="welcome-features">
                    <div class="feature-item">
                        <span class="feature-icon">⚙️</span>
                        <span>Personalización completa</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">🔒</span>
                        <span>Control de permisos</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">📝</span>
                        <span>Mensajes personalizados</span>
                    </div>
                </div>
            </div>
        `;
        editorTitle.textContent = 'Selecciona un ticket para editar';
        cancelBtn.style.display = 'none';
        resetHistory();
        updatePreviewButton();
        return;
    }
    
    const ticketChannel = ticketsData.find(t => t.channel_id === currentEditingTicket);
    editorTitle.textContent = `Configurando: ${ticketChannel ? ticketChannel.channel_name : 'Ticket'}`;
    cancelBtn.style.display = 'block';
    
    editorContent.innerHTML = `
        <div class="config-form">
            <div class="config-section">
                <h3>⚙️ Configuración Básica</h3>
                <div class="form-grid">
                    <div class="form-group">
                        <label>📝 Canal de Tickets</label>
                        <select id="ticket-channel-edit" class="form-select">
                            <option value="">Seleccionar canal...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>📋 Canal de Logs</label>
                        <select id="log-channel-edit" class="form-select">
                            <option value="">Seleccionar canal...</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <button class="btn-primary" id="config-permissions-btn">
                        <span class="btn-icon">🔒</span>
                        Configurar Permisos
                    </button>
                </div>
            </div>
            
            <div class="config-section">
                <h3>📝 Mensaje para Abrir Tickets</h3>
                <p>Configura el mensaje que verán los usuarios para abrir un ticket.</p>
                <button class="btn-primary" id="config-open-message-btn">
                    <span class="btn-icon">📝</span>
                    Configurar Mensaje
                </button>
            </div>
            
            <div class="config-section">
                <h3>💬 Mensajes de Tickets Abiertos</h3>
                <p>Configura los mensajes que aparecen cuando se abre un ticket.</p>
                <div id="opened-messages-list"></div>
                <button class="btn-secondary" id="config-opened-messages-btn">
                    <span class="btn-icon">💬</span>
                    Configurar Mensajes
                </button>
            </div>
        </div>
    `;
    
    loadChannelsForEdit();
    setupTicketConfigListeners();
    renderOpenedMessagesList();
}

async function loadChannelsForEdit() {
    if (channelsData.length === 0) {
        await loadChannelsData();
    }
    
    const ticketChannelSelect = document.getElementById('ticket-channel-edit');
    const logChannelSelect = document.getElementById('log-channel-edit');
    
    channelsData.forEach(channel => {
        const option1 = new Option(channel.name, channel.id);
        const option2 = new Option(channel.name, channel.id);
        
        if (channel.id === String(currentTicketConfig.ticket_channel)) {
            option1.selected = true;
        }
        if (channel.id === String(currentTicketConfig.log_channel)) {
            option2.selected = true;
        }
        
        ticketChannelSelect.add(option1);
        logChannelSelect.add(option2);
    });
}

function setupTicketConfigListeners() {
    document.getElementById('config-permissions-btn')?.addEventListener('click', () => {
        if (currentEditingTicket) {
            loadTicketPermissions(currentEditingTicket);
        } else {
            configureNewTicketPermissions();
        }
    });
    
    document.getElementById('config-open-message-btn')?.addEventListener('click', () => {
        currentMessageType = 'open_message';
        openMessageConfigModal();
    });
    
    document.getElementById('config-opened-messages-btn')?.addEventListener('click', () => {
        configureOpenedMessages();
    });
    
    document.getElementById('ticket-channel-edit')?.addEventListener('change', function() {
        saveSnapshot('Cambio de canal de tickets');
        currentTicketConfig.ticket_channel = parseInt(this.value);
        checkForChanges();
    });
    
    document.getElementById('log-channel-edit')?.addEventListener('change', function() {
        saveSnapshot('Cambio de canal de logs');
        currentTicketConfig.log_channel = parseInt(this.value);
        checkForChanges();
    });
}

function renderOpenedMessagesList() {
    const container = document.getElementById('opened-messages-list');
    if (!currentTicketConfig.open_message || !currentTicketConfig.open_message.buttons) {
        container.innerHTML = '<p>Primero configura el mensaje para abrir tickets.</p>';
        return;
    }
    
    const buttons = currentTicketConfig.open_message.buttons;
    const html = buttons.map((button, index) => `
        <div class="button-item">
            <div class="button-info">
                <div class="button-preview button-style-${button.style}">
                    ${button.emoji} ${button.label}
                </div>
                <div class="button-details">
                    <div><strong>Formato:</strong> ${button.name_format}</div>
                    <div><strong>Descripción:</strong> ${button.description || 'Sin descripción'}</div>
                </div>
            </div>
            <div class="button-actions">
                <button class="btn-secondary btn-small" onclick="configureOpenedMessage('${button.id}')">
                    💬 Configurar Mensaje
                </button>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function configureOpenedMessages() {
    if (!currentTicketConfig.open_message || !currentTicketConfig.open_message.buttons) {
        showToast('Primero configura el mensaje para abrir tickets', 'warning');
        return;
    }
    
    const buttons = currentTicketConfig.open_message.buttons;
    if (buttons.length === 1) {
        configureOpenedMessage(buttons[0].id);
    } else {
        showToast('Configura individualmente cada mensaje desde la lista superior', 'info');
    }
}

function configureOpenedMessage(buttonId) {
    currentMessageType = `opened_message_${buttonId}`;
    
    if (!currentTicketConfig.opened_messages) {
        currentTicketConfig.opened_messages = {};
    }
    
    if (!currentTicketConfig.opened_messages[buttonId]) {
        const button = currentTicketConfig.open_message.buttons.find(b => b.id === buttonId);
        currentTicketConfig.opened_messages[buttonId] = {
            embed: true,
            title: `Ticket de ${button ? button.label : 'Soporte'}`,
            description: `Gracias por abrir un ticket de ${button ? button.label : 'soporte'}. Un miembro del equipo te atenderá lo antes posible.`,
            footer: '',
            color: 'green',
            fields: [],
            image: { url: '', enabled: false },
            thumbnail: { url: '', enabled: false },
            plain_message: ''
        };
        saveSnapshot('Mensaje de ticket abierto creado');
        checkForChanges();
    }
    
    openMessageConfigModal();
}

function createNewTicket() {
    resetHistory();
    
    currentTicketConfig = {
        ticket_channel: null,
        log_channel: null,
        auto_increment: {},
        permissions: {
            manage: { roles: [], users: [] },
            view: { roles: [], users: [] }
        },
        open_message: {
            embed: true,
            title: 'Sistema de Tickets',
            description: 'Haz clic en el botón correspondiente para abrir un ticket de soporte.',
            footer: '',
            color: 'blue',
            fields: [],
            image: { url: '', enabled: false },
            thumbnail: { url: '', enabled: false },
            buttons: [{
                id: 'default',
                label: 'Abrir Ticket',
                emoji: '🎫',
                style: 3,
                name_format: 'ticket-{id}',
                description: 'Abrir un ticket de soporte general'
            }],
            plain_message: ''
        },
        opened_messages: {
            default: {
                embed: true,
                title: 'Ticket Abierto',
                description: 'Gracias por abrir un ticket. Un miembro del equipo te atenderá lo antes posible.',
                footer: '',
                color: 'green',
                fields: [],
                image: { url: '', enabled: false },
                thumbnail: { url: '', enabled: false },
                plain_message: ''
            }
        }
    };
    originalTicketConfig = null;
    currentEditingTicket = null;
    
    saveSnapshot('Ticket creado');
    updatePreviewButton();
    checkForChanges();
    openChannelSelectModal();
}

function saveCurrentTicket() {
    if (!currentTicketConfig || !currentTicketConfig.ticket_channel) {
        showToast('Debes seleccionar un canal para tickets', 'error');
        return;
    }
    
    if (!currentTicketConfig.permissions.manage.roles.length && !currentTicketConfig.permissions.manage.users.length) {
        showToast('Debes configurar al menos un rol o usuario con permisos de gestión', 'error');
        return;
    }
    
    const openMessage = currentTicketConfig.open_message;
    if (openMessage.embed) {
        if (!openMessage.description || !openMessage.description.trim()) {
            showToast('El mensaje de apertura debe tener una descripción', 'error');
            return;
        }
    } else {
        if (!openMessage.plain_message || !openMessage.plain_message.trim()) {
            showToast('El mensaje de apertura debe tener contenido', 'error');
            return;
        }
    }
    
    saveTicketConfig();
}

async function saveTicketConfig() {
    try {
        const channelId = currentEditingTicket || currentTicketConfig.ticket_channel;
        const response = await fetch(`/api/server/${window.serverId}/tickets/${channelId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentTicketConfig)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Ticket guardado correctamente en Firebase', 'success');
            loadTicketsData();
            if (!currentEditingTicket) {
                currentEditingTicket = String(channelId);
            }
            
            originalTicketConfig = JSON.parse(JSON.stringify(currentTicketConfig));
            resetHistory();
            saveSnapshot('Configuración guardada');
        } else {
            showToast(result.error || 'Error al guardar ticket', 'error');
        }
    } catch (error) {
        console.error('Error saving ticket:', error);
        showToast('Error al guardar ticket', 'error');
    }
}

function cancelTicketEdit() {
    currentTicketConfig = null;
    originalTicketConfig = null;
    currentEditingTicket = null;
    resetHistory();
    
    document.querySelectorAll('.ticket-item').forEach(item => {
        item.classList.remove('active');
    });
    
    renderTicketEditor();
    closePreview();
}

function togglePreview() {
    if (!currentTicketConfig) {
        showToast('Selecciona un ticket para ver la vista previa', 'warning');
        return;
    }
    
    const preview = document.getElementById('tickets-preview');
    const btn = document.getElementById('toggle-preview-btn');
    
    if (preview.classList.contains('active')) {
        preview.classList.remove('active');
        btn.innerHTML = '<span class="btn-icon">👁️</span> Mostrar Vista Previa';
    } else {
        preview.classList.add('active');
        btn.innerHTML = '<span class="btn-icon">👁️</span> Ocultar Vista Previa';
        updatePreview();
    }
}

function closePreview() {
    const preview = document.getElementById('tickets-preview');
    const btn = document.getElementById('toggle-preview-btn');
    
    preview.classList.remove('active');
    btn.innerHTML = '<span class="btn-icon">👁️</span> Mostrar Vista Previa';
}

function updatePreview() {
    if (!currentTicketConfig) return;
    
    const openPreview = document.getElementById('open-message-preview');
    const openedPreview = document.getElementById('opened-message-preview');
    
    openPreview.innerHTML = generateMessagePreview(currentTicketConfig.open_message, 'open');
    
    const buttons = currentTicketConfig.open_message?.buttons || [];
    if (buttons.length > 0 && currentTicketConfig.opened_messages) {
        const firstButtonId = buttons[0].id;
        let openedMessage = currentTicketConfig.opened_messages[firstButtonId];
        
        if (!openedMessage) {
            openedMessage = currentTicketConfig.opened_messages.default || {
                embed: true,
                title: 'Ticket Abierto',
                description: 'Gracias por abrir un ticket. Un miembro del equipo te atenderá lo antes posible.',
                footer: '',
                color: 'green',
                fields: [],
                image: { url: '', enabled: false },
                thumbnail: { url: '', enabled: false },
                plain_message: ''
            };
        }
        
        openedPreview.innerHTML = generateMessagePreview(openedMessage, 'opened');
    } else {
        openedPreview.innerHTML = '<p>Configura primero el mensaje para abrir tickets</p>';
    }
}

function generateMessagePreview(messageConfig, type) {
    if (!messageConfig) return '<p>Sin configurar</p>';
    
    let html = '';
    
    if (messageConfig.plain_message) {
        html += `<div class="preview-content-text">${messageConfig.plain_message}</div>`;
    }
    
    if (messageConfig.embed) {
        const colorMap = {
            blue: '#3498db', red: '#ff0000', green: '#2ecc71', yellow: '#f1c40f',
            orange: '#e67e22', purple: '#9b59b6', pink: '#ff6b81', gray: '#95a5a6'
        };
        
        const color = colorMap[messageConfig.color] || '#3498db';
        
        html += `<div class="preview-embed" style="border-left-color: ${color};">`;
        
        if (messageConfig.title) {
            html += `<div class="embed-title">${messageConfig.title}</div>`;
        }
        
        if (messageConfig.description) {
            html += `<div class="embed-description">${messageConfig.description}</div>`;
        }
        
        if (messageConfig.fields && messageConfig.fields.length > 0) {
            html += '<div class="embed-fields">';
            messageConfig.fields.forEach(field => {
                html += `
                    <div class="embed-field ${field.inline ? 'inline' : ''}">
                        <div class="embed-field-name">${field.name}</div>
                        <div class="embed-field-value">${field.value}</div>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        if (messageConfig.footer) {
            html += `<div class="embed-footer">${messageConfig.footer}</div>`;
        }
        
        html += '</div>';
    }
    
    if (type === 'open' && messageConfig.buttons) {
        html += '<div class="preview-buttons">';
        messageConfig.buttons.forEach(button => {
            html += `<div class="preview-button button-style-${button.style}">
                ${button.emoji} ${button.label}
            </div>`;
        });
        html += '</div>';
    } else if (type === 'opened') {
        html += `<div class="preview-buttons">
            <div class="preview-button button-style-2">🔒 Archivar Ticket</div>
            <div class="preview-button button-style-1">➕ Añadir Usuario</div>
            <div class="preview-button button-style-1">➖ Eliminar Usuario</div>
        </div>`;
    }
    
    return html;
}

function initializeChannelSelectModal() {
    const confirmBtn = document.getElementById('confirm-channel-select');
    const cancelBtn = document.getElementById('cancel-channel-select');
    
    confirmBtn?.addEventListener('click', async function() {
        const ticketChannel = document.getElementById('ticket-channel').value;
        const logChannel = document.getElementById('log-channel').value;
        
        if (!ticketChannel || !logChannel) {
            showToast('Debes seleccionar ambos canales', 'error');
            return;
        }
        
        saveSnapshot('Canales configurados');
        currentTicketConfig.ticket_channel = parseInt(ticketChannel);
        currentTicketConfig.log_channel = parseInt(logChannel);
        
        closeAllModals();
        renderTicketEditor();
        checkForChanges();
    });
    
    cancelBtn?.addEventListener('click', function() {
        closeAllModals();
        if (!currentEditingTicket) {
            cancelTicketEdit();
        }
    });
}

function initializeLogChannelSelectModal() {
    const confirmBtn = document.getElementById('confirm-log-channel-select');
    const cancelBtn = document.getElementById('cancel-log-channel-select');
    
    confirmBtn?.addEventListener('click', async function() {
        const logChannel = document.getElementById('log-channel-select').value;
        
        if (!logChannel) {
            showToast('Debes seleccionar un canal', 'error');
            return;
        }
        
        saveLogSnapshot('Canal configurado');
        currentLogConfig.log_channel = parseInt(logChannel);
        
        closeAllModals();
        renderLogEditor();
        checkForLogChanges();
    });
    
    cancelBtn?.addEventListener('click', function() {
        closeAllModals();
    });
}

function initializeLogMessageConfigModal() {
    const messageTypeBtns = document.querySelectorAll('#log-message-config-modal .message-type-btn');
    const embedConfig = document.getElementById('log-embed-config');
    const textConfig = document.getElementById('log-text-config');
    const fieldsConfig = document.getElementById('log-fields-config');
    const saveBtn = document.getElementById('save-log-message-config');
    const cancelBtn = document.getElementById('cancel-log-message-config');
    const addFieldBtn = document.getElementById('add-log-field-btn');

    messageTypeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.getAttribute('data-type');
            
            messageTypeBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            if (type === 'embed') {
                embedConfig.style.display = 'block';
                textConfig.style.display = 'none';
                fieldsConfig.style.display = 'block';
            } else {
                embedConfig.style.display = 'none';
                textConfig.style.display = 'block';
                fieldsConfig.style.display = 'none';
            }
        });
    });
    
    document.querySelectorAll('#log-color-grid .color-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('#log-color-grid .color-option').forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
        });
    });
    
    document.getElementById('log-enable-image')?.addEventListener('change', function() {
        document.getElementById('log-image-url').disabled = !this.checked;
    });
    
    document.getElementById('log-enable-thumbnail')?.addEventListener('change', function() {
        document.getElementById('log-thumbnail-url').disabled = !this.checked;
    });
    
    addFieldBtn?.addEventListener('click', openLogFieldConfigModal);
    saveBtn?.addEventListener('click', saveLogMessageConfig);
    cancelBtn?.addEventListener('click', closeAllModals);
}

function initializeLogFieldConfigModal() {
    const saveBtn = document.getElementById('save-log-field-config');
    const cancelBtn = document.getElementById('cancel-log-field-config');
    
    saveBtn?.addEventListener('click', saveLogFieldConfig);
    cancelBtn?.addEventListener('click', closeAllModals);
}

let isEditingLogField = false;
let editingLogFieldId = null;

function openLogFieldConfigModal() {
    const modal = document.getElementById('log-field-config-modal');
    const overlay = document.getElementById('modal-overlay');
    
    if (!isEditingLogField) {
        document.getElementById('log-field-name').value = '';
        document.getElementById('log-field-value').value = '';
        document.getElementById('log-field-inline').checked = false;
    }
    
    modal.classList.add('active');
    overlay.classList.add('active');
}

function saveLogFieldConfig() {
    const name = document.getElementById('log-field-name').value.trim();
    const value = document.getElementById('log-field-value').value.trim();
    const inline = document.getElementById('log-field-inline').checked;
    
    if (!name || !value) {
        showToast('El nombre y valor del campo son obligatorios', 'error');
        return;
    }
    
    if (!currentLogConfig.message) {
        currentLogConfig.message = {};
    }
    
    if (!currentLogConfig.message.fields) {
        currentLogConfig.message.fields = {};
    }
    
    let fieldId;
    if (isEditingLogField) {
        fieldId = editingLogFieldId;
        saveLogSnapshot('Campo editado');
    } else {
        const existingIds = Object.keys(currentLogConfig.message.fields).map(id => parseInt(id)).filter(id => !isNaN(id));
        fieldId = existingIds.length > 0 ? Math.max(...existingIds) + 1 : 1;
        saveLogSnapshot('Campo añadido');
    }
    
    currentLogConfig.message.fields[fieldId] = {
        name: name,
        value: value,
        inline: inline
    };
    
    isEditingLogField = false;
    editingLogFieldId = null;
    
    closeAllModals();
    renderLogFieldsList();
    updateLogsPreview();
    checkForLogChanges();
    showToast('Campo guardado correctamente', 'success');
}

function renderLogFieldsList() {
    const container = document.getElementById('log-fields-list');
    const fields = currentLogConfig?.message?.fields || {};
    
    if (Object.keys(fields).length === 0) {
        container.innerHTML = '<p>No hay campos configurados</p>';
        return;
    }
    
    const html = Object.entries(fields).map(([fieldId, field]) => `
        <div class="field-item">
            <div class="field-info">
                <div class="field-name">${field.name} ${field.inline ? '(inline)' : ''}</div>
                <div class="field-value">${field.value}</div>
            </div>
            <div class="field-actions">
                <button class="btn-secondary btn-small" onclick="editLogField('${fieldId}')">Editar</button>
                <button class="btn-danger btn-small" onclick="deleteLogField('${fieldId}')">Eliminar</button>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function editLogField(fieldId) {
    const field = currentLogConfig.message.fields[fieldId];
    if (!field) return;
    
    isEditingLogField = true;
    editingLogFieldId = fieldId;
    
    document.getElementById('log-field-name').value = field.name;
    document.getElementById('log-field-value').value = field.value;
    document.getElementById('log-field-inline').checked = field.inline || false;
    
    openLogFieldConfigModal();
}

function deleteLogField(fieldId) {
    if (!currentLogConfig.message.fields[fieldId]) return;
    
    saveLogSnapshot('Campo eliminado');
    delete currentLogConfig.message.fields[fieldId];
    
    renderLogFieldsList();
    updateLogsPreview();
    checkForLogChanges();
    showToast('Campo eliminado', 'success');
}

function openLogMessageConfigModal() {
    const modal = document.getElementById('log-message-config-modal');
    const overlay = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('log-message-modal-title');
    
    if (!currentLogConfig || !currentLogConfig.message) {
        currentLogConfig.message = {
            embed: true,
            title: '',
            description: '',
            footer: '',
            color: 'default',
            image: { has: false, param: '' },
            thumbnail: { has: false, param: '' },
            fields: {},
            message: ''
        };
    }
    
    const logInfo = currentLogConfig.log_info || {};
    modalTitle.textContent = `📝 Configurar Mensaje - ${logInfo.name || 'Log'}`;
    
    fillLogMessageConfigForm(currentLogConfig.message);
    renderLogFieldsList();
    renderLogParametersInfo();
    
    modal.classList.add('active');
    overlay.classList.add('active');
}

function fillLogMessageConfigForm(messageConfig) {
    const messageTypeBtns = document.querySelectorAll('#log-message-config-modal .message-type-btn');
    const embedConfig = document.getElementById('log-embed-config');
    const textConfig = document.getElementById('log-text-config');
    const fieldsConfig = document.getElementById('log-fields-config');
    
    messageTypeBtns.forEach(btn => btn.classList.remove('active'));
    
    if (messageConfig.embed) {
        document.querySelector('#log-message-config-modal [data-type="embed"]').classList.add('active');
        embedConfig.style.display = 'block';
        textConfig.style.display = 'none';
        fieldsConfig.style.display = 'block';
        
        document.getElementById('log-embed-title').value = messageConfig.title || '';
        document.getElementById('log-embed-description').value = messageConfig.description || '';
        document.getElementById('log-embed-footer').value = messageConfig.footer || '';
        
        document.querySelectorAll('#log-color-grid .color-option').forEach(opt => opt.classList.remove('selected'));
        document.querySelector(`#log-color-grid [data-color="${messageConfig.color || 'default'}"]`)?.classList.add('selected');
        
        document.getElementById('log-enable-image').checked = messageConfig.image?.has || false;
        document.getElementById('log-image-url').value = messageConfig.image?.param || '';
        document.getElementById('log-image-url').disabled = !messageConfig.image?.has;
        
        document.getElementById('log-enable-thumbnail').checked = messageConfig.thumbnail?.has || false;
        document.getElementById('log-thumbnail-url').value = messageConfig.thumbnail?.param || '';
        document.getElementById('log-thumbnail-url').disabled = !messageConfig.thumbnail?.has;
    } else {
        document.querySelector('#log-message-config-modal [data-type="text"]').classList.add('active');
        embedConfig.style.display = 'none';
        textConfig.style.display = 'block';
        fieldsConfig.style.display = 'none';
        
        document.getElementById('log-plain-message').value = messageConfig.message || '';
    }
}

function renderLogParametersInfo() {
    const container = document.getElementById('log-parameters-info');
    const logInfo = currentLogConfig?.log_info || {};
    const params = logInfo.params || [];
    
    if (params.length === 0) {
        container.innerHTML = '<p>No hay parámetros disponibles para este tipo de log</p>';
        return;
    }
    
    const html = params.map(param => `
        <div class="parameter-item">${param}</div>
    `).join('');
    
    container.innerHTML = html;
}

function saveLogMessageConfig() {
    const isEmbed = document.querySelector('#log-message-config-modal [data-type="embed"]').classList.contains('active');
    
    if (!currentLogConfig.message) {
        currentLogConfig.message = {};
    }
    
    saveLogSnapshot(`Mensaje configurado`);
    
    currentLogConfig.message.embed = isEmbed;
    
    if (isEmbed) {
        currentLogConfig.message.title = document.getElementById('log-embed-title').value;
        currentLogConfig.message.description = document.getElementById('log-embed-description').value;
        currentLogConfig.message.footer = document.getElementById('log-embed-footer').value;
        
        const selectedColor = document.querySelector('#log-color-grid .color-option.selected');
        currentLogConfig.message.color = selectedColor?.getAttribute('data-color') || 'default';
        
        currentLogConfig.message.image = {
            has: document.getElementById('log-enable-image').checked,
            param: document.getElementById('log-image-url').value
        };
        
        currentLogConfig.message.thumbnail = {
            has: document.getElementById('log-enable-thumbnail').checked,
            param: document.getElementById('log-thumbnail-url').value
        };
        
        currentLogConfig.message.message = '';
    } else {
        currentLogConfig.message.message = document.getElementById('log-plain-message').value;
        currentLogConfig.message.title = '';
        currentLogConfig.message.description = '';
        currentLogConfig.message.footer = '';
        currentLogConfig.message.image = { has: false, param: '' };
        currentLogConfig.message.thumbnail = { has: false, param: '' };
        currentLogConfig.message.fields = {};
    }
    
    closeAllModals();
    updateLogsPreview();
    checkForLogChanges();
    showToast('Mensaje configurado correctamente', 'success');
}

function openChannelSelectModal() {
    loadChannelsData().then(() => {
        const modal = document.getElementById('channel-select-modal');
        const overlay = document.getElementById('modal-overlay');
        const ticketChannelSelect = document.getElementById('ticket-channel');
        const logChannelSelect = document.getElementById('log-channel');
        
        ticketChannelSelect.innerHTML = '<option value="">Selecciona un canal...</option>';
        logChannelSelect.innerHTML = '<option value="">Selecciona un canal...</option>';
        
        channelsData.forEach(channel => {
            const option1 = new Option(channel.name, channel.id);
            const option2 = new Option(channel.name, channel.id);
            ticketChannelSelect.add(option1);
            logChannelSelect.add(option2);
        });
        
        modal.classList.add('active');
        overlay.classList.add('active');
    });
}

async function loadChannelsData() {
    try {
        if (channelsData.length > 0) {
            return;
        }
        
        const response = await fetch(`/api/server/${window.serverId}/channels`);
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
            channelsData = [];
            return;
        }
        
        channelsData = data.channels || [];
    } catch (error) {
        console.error('Error loading channels:', error);
        showToast('Error al cargar canales', 'error');
        channelsData = [];
    }
}

function initializePermissionsModal() {
    const tabBtns = document.querySelectorAll('.permissions-tabs .tab-btn');
    const tabContents = document.querySelectorAll('.permission-tab');
    const saveBtn = document.getElementById('save-permissions');
    const cancelBtn = document.getElementById('cancel-permissions');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.getAttribute('data-tab');
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(t => t.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById(`${tab}-tab`).classList.add('active');
            
            currentPermissionType = tab;
        });
    });
    
    saveBtn?.addEventListener('click', function() {
        closeAllModals();
        showToast('Permisos guardados', 'success');
    });
    
    cancelBtn?.addEventListener('click', closeAllModals);
    
    setupPermissionButtons();
}

function setupPermissionButtons() {
    document.getElementById('add-manage-role')?.addEventListener('click', () => addRole('manage'));
    document.getElementById('add-view-role')?.addEventListener('click', () => addRole('view'));
    document.getElementById('add-manage-user')?.addEventListener('click', () => addUser('manage'));
    document.getElementById('add-view-user')?.addEventListener('click', () => addUser('view'));
}

function openPermissionsModal() {
    const modal = document.getElementById('permissions-modal');
    const overlay = document.getElementById('modal-overlay');
    
    renderPermissions();
    
    modal.classList.add('active');
    overlay.classList.add('active');
}

function renderPermissions() {
    if (!currentTicketConfig.permissions) {
        currentTicketConfig.permissions = {
            manage: { roles: [], users: [] },
            view: { roles: [], users: [] }
        };
    }
    
    renderTicketPermissionItems('manage');
    renderTicketPermissionItems('view');
}

function renderPermissionItems(type) {
    const rolesContainer = document.getElementById(`${type}-roles-list`);
    const usersContainer = document.getElementById(`${type}-users-list`);
    
    const permissions = currentTicketConfig.permissions[type];
    
    rolesContainer.innerHTML = permissions.roles.map(roleId => {
        const role = rolesData.find(r => r.id === String(roleId));
        return `
            <div class="selected-item">
                ${role ? role.name : `Rol ID: ${roleId}`}
                <button class="remove-btn" onclick="removeRole('${type}', '${roleId}')">✕</button>
            </div>
        `;
    }).join('');
    
    usersContainer.innerHTML = permissions.users.map(userId => `
        <div class="selected-item">
            Usuario ID: ${userId}
            <button class="remove-btn" onclick="removeUser('${type}', '${userId}')">✕</button>
        </div>
    `).join('');
}

function addRole(type) {
    currentPermissionType = type;
    openRoleSelectModal();
}

function addUser(type) {
    const input = document.getElementById(`${type}-user-input`);
    const userId = input.value.trim();
    
    if (!userId || !userId.match(/^\d+$/)) {
        showToast('Ingresa un ID de usuario válido', 'error');
        return;
    }
    
    if (!currentTicketConfig.permissions[type].users.includes(parseInt(userId))) {
        saveSnapshot(`Usuario añadido a permisos de ${type}`);
        currentTicketConfig.permissions[type].users.push(parseInt(userId));
        renderPermissionItems(type);
        input.value = '';
    }
}

function removeRole(type, roleId) {
    const index = currentTicketConfig.permissions[type].roles.indexOf(parseInt(roleId));
    if (index > -1) {
        saveSnapshot(`Rol eliminado de permisos de ${type}`);
        currentTicketConfig.permissions[type].roles.splice(index, 1);
        renderPermissionItems(type);
    }
}

function removeUser(type, userId) {
    const index = currentTicketConfig.permissions[type].users.indexOf(parseInt(userId));
    if (index > -1) {
        saveSnapshot(`Usuario eliminado de permisos de ${type}`);
        currentTicketConfig.permissions[type].users.splice(index, 1);
        renderPermissionItems(type);
    }
}

function initializeRoleSelectModal() {
    const cancelBtn = document.getElementById('cancel-role-select');
    cancelBtn?.addEventListener('click', closeAllModals);
}

function openRoleSelectModal() {
    loadRolesData().then(() => {
        const modal = document.getElementById('role-select-modal');
        const overlay = document.getElementById('modal-overlay');
        const rolesList = document.getElementById('roles-list');
        
        rolesList.innerHTML = rolesData.map(role => `
            <div class="role-item" onclick="selectRole('${role.id}')">
                <div class="role-color" style="background-color: ${role.color};"></div>
                <div class="role-name">${role.name}</div>
            </div>
        `).join('');
        
        modal.classList.add('active');
        overlay.classList.add('active');
    });
}

function selectRole(roleId) {
    if (!currentTicketConfig.permissions[currentPermissionType].roles.includes(parseInt(roleId))) {
        saveSnapshot(`Rol añadido a permisos de ${currentPermissionType}`);
        currentTicketConfig.permissions[currentPermissionType].roles.push(parseInt(roleId));
        renderPermissionItems(currentPermissionType);
    }
    closeAllModals();
}

function initializeMessageConfigModal() {
    const messageTypeBtns = document.querySelectorAll('#message-config-modal .message-type-btn');
    const embedConfig = document.getElementById('embed-config');
    const textConfig = document.getElementById('text-config');
    const buttonsConfig = document.getElementById('buttons-config');
    const saveBtn = document.getElementById('save-message-config');
    const cancelBtn = document.getElementById('cancel-message-config');
    const addButtonBtn = document.getElementById('add-button-btn');
    
    messageTypeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.getAttribute('data-type');
            
            messageTypeBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            if (type === 'embed') {
                embedConfig.style.display = 'block';
                textConfig.style.display = 'none';
                if (currentMessageType === 'open_message') {
                    buttonsConfig.style.display = 'block';
                }
            } else {
                embedConfig.style.display = 'none';
                textConfig.style.display = 'block';
                buttonsConfig.style.display = 'none';
            }
        });
    });
    
    document.querySelectorAll('#color-grid .color-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('#color-grid .color-option').forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
        });
    });
    
    document.getElementById('enable-image')?.addEventListener('change', function() {
        document.getElementById('image-url').disabled = !this.checked;
    });
    
    document.getElementById('enable-thumbnail')?.addEventListener('change', function() {
        document.getElementById('thumbnail-url').disabled = !this.checked;
    });
    
    addButtonBtn?.addEventListener('click', openButtonConfigModal);
    saveBtn?.addEventListener('click', saveMessageConfig);
    cancelBtn?.addEventListener('click', closeAllModals);
}

function openMessageConfigModal() {
    const modal = document.getElementById('message-config-modal');
    const overlay = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('message-modal-title');
    const buttonsConfig = document.getElementById('buttons-config');
    
    let messageConfig;
    if (currentMessageType === 'open_message') {
        messageConfig = currentTicketConfig.open_message;
        modalTitle.textContent = '📝 Configurar Mensaje para Abrir Tickets';
        buttonsConfig.style.display = 'block';
    } else if (currentMessageType.startsWith('opened_message_')) {
        const buttonId = currentMessageType.substring('opened_message_'.length);
        messageConfig = currentTicketConfig.opened_messages[buttonId];
        modalTitle.textContent = '💬 Configurar Mensaje de Ticket Abierto';
        buttonsConfig.style.display = 'none';
    }
    
    if (!messageConfig) {
        showToast('Error: No se encontró la configuración del mensaje', 'error');
        return;
    }
    
    fillMessageConfigForm(messageConfig);
    renderButtonsList();
    
    modal.classList.add('active');
    overlay.classList.add('active');
}

function fillMessageConfigForm(messageConfig) {
    const messageTypeBtns = document.querySelectorAll('#message-config-modal .message-type-btn');
    const embedConfig = document.getElementById('embed-config');
    const textConfig = document.getElementById('text-config');
    
    messageTypeBtns.forEach(btn => btn.classList.remove('active'));
    
    if (messageConfig.embed) {
        document.querySelector('#message-config-modal [data-type="embed"]').classList.add('active');
        embedConfig.style.display = 'block';
        textConfig.style.display = 'none';
        
        document.getElementById('embed-title').value = messageConfig.title || '';
        document.getElementById('embed-description').value = messageConfig.description || '';
        document.getElementById('embed-footer').value = messageConfig.footer || '';
        
        document.querySelectorAll('#color-grid .color-option').forEach(opt => opt.classList.remove('selected'));
        document.querySelector(`#color-grid [data-color="${messageConfig.color || 'blue'}"]`)?.classList.add('selected');
        
        document.getElementById('enable-image').checked = messageConfig.image?.enabled || false;
        document.getElementById('image-url').value = messageConfig.image?.url || '';
        document.getElementById('image-url').disabled = !messageConfig.image?.enabled;
        
        document.getElementById('enable-thumbnail').checked = messageConfig.thumbnail?.enabled || false;
        document.getElementById('thumbnail-url').value = messageConfig.thumbnail?.url || '';
        document.getElementById('thumbnail-url').disabled = !messageConfig.thumbnail?.enabled;
    } else {
        document.querySelector('#message-config-modal [data-type="text"]').classList.add('active');
        embedConfig.style.display = 'none';
        textConfig.style.display = 'block';
        
        document.getElementById('plain-message').value = messageConfig.plain_message || '';
    }
}

function renderButtonsList() {
    if (currentMessageType !== 'open_message') return;
    
    const container = document.getElementById('buttons-list');
    const buttons = currentTicketConfig.open_message.buttons || [];
    
    const html = buttons.map((button, index) => `
        <div class="button-item">
            <div class="button-info">
                <div class="button-preview button-style-${button.style}">
                    ${button.emoji} ${button.label}
                </div>
                <div class="button-details">
                    <div><strong>Formato:</strong> ${button.name_format}</div>
                    <div><strong>Descripción:</strong> ${button.description || 'Sin descripción'}</div>
                </div>
            </div>
            <div class="button-actions">
                <button class="btn-secondary btn-small" onclick="editButton(${index})">Editar</button>
                <button class="btn-danger btn-small" onclick="deleteButton(${index})">Eliminar</button>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function saveMessageConfig() {
    const isEmbed = document.querySelector('#message-config-modal [data-type="embed"]').classList.contains('active');
    
    let messageConfig;
    if (currentMessageType === 'open_message') {
        messageConfig = currentTicketConfig.open_message;
    } else if (currentMessageType.startsWith('opened_message_')) {
        const buttonId = currentMessageType.substring('opened_message_'.length);
        if (!currentTicketConfig.opened_messages) {
            currentTicketConfig.opened_messages = {};
        }
        if (!currentTicketConfig.opened_messages[buttonId]) {
            const button = currentTicketConfig.open_message.buttons.find(b => b.id === buttonId);
            currentTicketConfig.opened_messages[buttonId] = {
                embed: true,
                title: `Ticket de ${button ? button.label : 'Soporte'}`,
                description: `Gracias por abrir un ticket de ${button ? button.label : 'soporte'}. Un miembro del equipo te atenderá lo antes posible.`,
                footer: '',
                color: 'green',
                fields: [],
                image: { url: '', enabled: false },
                thumbnail: { url: '', enabled: false },
                plain_message: ''
            };
        }
        messageConfig = currentTicketConfig.opened_messages[buttonId];
    }
    
    if (!messageConfig) {
        showToast('Error: No se encontró la configuración del mensaje', 'error');
        return;
    }
    
    saveSnapshot(`Mensaje ${currentMessageType} configurado`);
    
    messageConfig.embed = isEmbed;
    
    if (isEmbed) {
        messageConfig.title = document.getElementById('embed-title').value;
        messageConfig.description = document.getElementById('embed-description').value;
        messageConfig.footer = document.getElementById('embed-footer').value;
        
        const selectedColor = document.querySelector('#color-grid .color-option.selected');
        messageConfig.color = selectedColor?.getAttribute('data-color') || 'blue';
        
        messageConfig.image = {
            enabled: document.getElementById('enable-image').checked,
            url: document.getElementById('image-url').value
        };
        
        messageConfig.thumbnail = {
            enabled: document.getElementById('enable-thumbnail').checked,
            url: document.getElementById('thumbnail-url').value
        };
        
        messageConfig.plain_message = '';
    } else {
        messageConfig.plain_message = document.getElementById('plain-message').value;
        messageConfig.title = '';
        messageConfig.description = '';
        messageConfig.footer = '';
        messageConfig.image = { enabled: false, url: '' };
        messageConfig.thumbnail = { enabled: false, url: '' };
    }
    
    closeAllModals();
    updatePreview();
    renderOpenedMessagesList();
    checkForChanges();
    showToast('Mensaje configurado correctamente', 'success');
}

function initializeButtonConfigModal() {
    const styleOptions = document.querySelectorAll('.style-option');
    const saveBtn = document.getElementById('save-button-config');
    const cancelBtn = document.getElementById('cancel-button-config');
    
    styleOptions.forEach(option => {
        option.addEventListener('click', function() {
            styleOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
        });
    });
    
    saveBtn?.addEventListener('click', saveButtonConfig);
    cancelBtn?.addEventListener('click', closeAllModals);
}

function openButtonConfigModal() {
    const modal = document.getElementById('button-config-modal');
    const overlay = document.getElementById('modal-overlay');
    
    if (isEditingButton) {
        const button = currentTicketConfig.open_message.buttons[editingButtonIndex];
        document.getElementById('button-label').value = button.label;
        document.getElementById('button-emoji').value = button.emoji;
        document.getElementById('button-name-format').value = button.name_format;
        document.getElementById('button-description').value = button.description || '';
        
        document.querySelectorAll('.style-option').forEach(opt => opt.classList.remove('selected'));
        document.querySelector(`[data-style="${button.style}"]`)?.classList.add('selected');
    } else {
        document.getElementById('button-label').value = '';
        document.getElementById('button-emoji').value = '🎫';
        document.getElementById('button-name-format').value = 'ticket-{id}';
        document.getElementById('button-description').value = '';
        
        document.querySelectorAll('.style-option').forEach(opt => opt.classList.remove('selected'));
        document.querySelector('[data-style="3"]')?.classList.add('selected');
    }
    
    modal.classList.add('active');
    overlay.classList.add('active');
}

function editButton(index) {
    isEditingButton = true;
    editingButtonIndex = index;
    openButtonConfigModal();
}

function deleteButton(index) {
    if (currentTicketConfig.open_message.buttons.length <= 1) {
        showToast('Debe haber al menos un botón', 'error');
        return;
    }
    
    saveSnapshot('Botón eliminado');
    
    const button = currentTicketConfig.open_message.buttons[index];
    currentTicketConfig.open_message.buttons.splice(index, 1);
    
    if (currentTicketConfig.opened_messages && currentTicketConfig.opened_messages[button.id]) {
        delete currentTicketConfig.opened_messages[button.id];
    }
    
    renderButtonsList();
    renderOpenedMessagesList();
    updatePreview();
}

function saveButtonConfig() {
    const label = document.getElementById('button-label').value.trim();
    const emoji = document.getElementById('button-emoji').value.trim();
    const nameFormat = document.getElementById('button-name-format').value.trim();
    const description = document.getElementById('button-description').value.trim();
    const selectedStyle = document.querySelector('.style-option.selected');
    
    if (!label) {
        showToast('El texto del botón es obligatorio', 'error');
        return;
    }
    
    if (!nameFormat) {
        showToast('El formato del nombre es obligatorio', 'error');
        return;
    }
    
    const style = selectedStyle ? parseInt(selectedStyle.getAttribute('data-style')) : 3;
    
    const buttonData = {
        label,
        emoji,
        style,
        name_format: nameFormat,
        description
    };
    
    if (isEditingButton) {
        saveSnapshot('Botón editado');
        const oldButton = currentTicketConfig.open_message.buttons[editingButtonIndex];
        buttonData.id = oldButton.id;
        currentTicketConfig.open_message.buttons[editingButtonIndex] = buttonData;
    } else {
        saveSnapshot('Botón añadido');
        buttonData.id = `btn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        currentTicketConfig.open_message.buttons.push(buttonData);
        
        if (!currentTicketConfig.opened_messages) {
            currentTicketConfig.opened_messages = {};
        }
        
        currentTicketConfig.opened_messages[buttonData.id] = {
            embed: true,
            title: `Ticket de ${label}`,
            description: `Gracias por abrir un ticket de ${label}. Un miembro del equipo te atenderá lo antes posible.`,
            footer: '',
            color: 'green',
            fields: [],
            image: { url: '', enabled: false },
            thumbnail: { url: '', enabled: false },
            plain_message: ''
        };
    }
    
    isEditingButton = false;
    editingButtonIndex = -1;
    
    closeAllModals();
    renderButtonsList();
    renderOpenedMessagesList();
    updatePreview();
    checkForChanges();
    showToast('Botón configurado correctamente', 'success');
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    const overlay = document.getElementById('modal-overlay');
    
    modals.forEach(modal => modal.classList.remove('active'));
    overlay.classList.remove('active');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

let currentTicketPermissions = null;
let currentTicketChannelId = null;

async function loadTicketPermissions(channelId) {
    try {
        currentTicketChannelId = channelId;
        const response = await fetch(`/api/server/${window.serverId}/tickets/${channelId}/permissions`);
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
            return;
        }
        
        currentTicketPermissions = data.permissions;
        renderTicketPermissionsEditor();
    } catch (error) {
        console.error('Error loading ticket permissions:', error);
        showToast('Error al cargar permisos del ticket', 'error');
    }
}

function renderTicketPermissionsEditor() {
    const editorTitle = document.getElementById('editor-title');
    const editorContent = document.getElementById('editor-content');
    
    if (!currentTicketPermissions) {
        return;
    }
    
    const ticketInfo = currentTicketChannelId === 'new' ? 
        { channel_name: 'Nuevo Ticket' } : 
        ticketsData.find(t => t.channel_id === currentTicketChannelId);
    
    editorTitle.textContent = `Permisos: ${ticketInfo ? ticketInfo.channel_name : 'Ticket'}`;
    
    editorContent.innerHTML = `
        <div class="config-form">
            <div class="config-section">
                <h3>🔒 Permisos del Ticket</h3>
                <p>Configura quién puede gestionar y ver este ticket.</p>
                
                <div class="permissions-tabs">
                    <button class="tab-btn active" data-tab="manage">🔑 Gestionar Tickets</button>
                    <button class="tab-btn" data-tab="view">👁️ Ver Tickets</button>
                </div>
                
                <div class="permission-tab active" id="manage-permissions-tab">
                    <div class="permission-description">
                        <strong>🔑 Gestionar Tickets:</strong> Permite el control total sobre los tickets, incluyendo ver, escribir, añadir/eliminar usuarios y archivar tickets.
                    </div>
                    
                    <div class="permission-section">
                        <h4>👥 Roles con permisos de gestión</h4>
                        <div class="selected-items" id="manage-roles-list"></div>
                        <div class="add-permission-controls">
                            <select id="manage-role-select" class="form-select">
                                <option value="">Selecciona un rol...</option>
                            </select>
                            <button class="btn-secondary" id="add-manage-role-btn">
                                <span class="btn-icon">➕</span>
                                Añadir Rol
                            </button>
                        </div>
                    </div>
                    
                    <div class="permission-section">
                        <h4>👤 Usuarios con permisos de gestión</h4>
                        <div class="selected-items" id="manage-users-list"></div>
                        <div class="add-permission-controls">
                            <input type="text" id="manage-user-input" placeholder="ID del usuario" class="form-input">
                            <button class="btn-secondary" id="add-manage-user-btn">
                                <span class="btn-icon">➕</span>
                                Añadir Usuario
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="permission-tab" id="view-permissions-tab">
                    <div class="permission-description">
                        <strong>👁️ Ver Tickets:</strong> Permite únicamente ver los tickets, sin poder escribir ni interactuar con los botones.
                    </div>
                    
                    <div class="permission-section">
                        <h4>👥 Roles con permisos de visualización</h4>
                        <div class="selected-items" id="view-roles-list"></div>
                        <div class="add-permission-controls">
                            <select id="view-role-select" class="form-select">
                                <option value="">Selecciona un rol...</option>
                            </select>
                            <button class="btn-secondary" id="add-view-role-btn">
                                <span class="btn-icon">➕</span>
                                Añadir Rol
                            </button>
                        </div>
                    </div>
                    
                    <div class="permission-section">
                        <h4>👤 Usuarios con permisos de visualización</h4>
                        <div class="selected-items" id="view-users-list"></div>
                        <div class="add-permission-controls">
                            <input type="text" id="view-user-input" placeholder="ID del usuario" class="form-input">
                            <button class="btn-secondary" id="add-view-user-btn">
                                <span class="btn-icon">➕</span>
                                Añadir Usuario
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="form-group" style="margin-top: 20px;">
                    <button class="btn-secondary" id="back-to-ticket-config">
                        <span class="btn-icon">⬅️</span>
                        Volver a Configuración
                    </button>
                </div>
            </div>
        </div>
    `;
    
    setupTicketPermissionsListeners();
    populateTicketRoleSelects();
    renderTicketPermissionItems();
    
    document.getElementById('back-to-ticket-config')?.addEventListener('click', () => {
        renderTicketEditor();
    });
    
    const saveBtn = document.getElementById('save-ticket-btn');
    const cancelBtn = document.getElementById('cancel-edit-btn');
    
    if (saveBtn) saveBtn.style.display = 'block';
    if (cancelBtn) cancelBtn.style.display = 'block';
}

function setupTicketPermissionsListeners() {
    document.querySelectorAll('.permissions-tabs .tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tab = this.getAttribute('data-tab');
            
            document.querySelectorAll('.permissions-tabs .tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.permission-tab').forEach(t => t.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById(`${tab}-permissions-tab`).classList.add('active');
        });
    });
    
    document.getElementById('add-manage-role-btn')?.addEventListener('click', () => addTicketRole('manage'));
    document.getElementById('add-view-role-btn')?.addEventListener('click', () => addTicketRole('view'));
    document.getElementById('add-manage-user-btn')?.addEventListener('click', () => addTicketUser('manage'));
    document.getElementById('add-view-user-btn')?.addEventListener('click', () => addTicketUser('view'));
}

function populateTicketRoleSelects() {
    const manageSelect = document.getElementById('manage-role-select');
    const viewSelect = document.getElementById('view-role-select');
    
    if (rolesData.length === 0) {
        loadRolesData().then(() => {
            populateRoleOptions(manageSelect);
            populateRoleOptions(viewSelect);
        });
    } else {
        populateRoleOptions(manageSelect);
        populateRoleOptions(viewSelect);
    }
}

function populateRoleOptions(selectElement) {
    if (!selectElement) return;
    
    selectElement.innerHTML = '<option value="">Selecciona un rol...</option>';
    
    rolesData.forEach(role => {
        const option = new Option(role.name, role.id);
        selectElement.add(option);
    });
}

function renderTicketPermissionItems() {
    ['manage', 'view'].forEach(permType => {
        renderTicketRolesList(permType);
        renderTicketUsersList(permType);
    });
}

function renderTicketRolesList(permType) {
    const container = document.getElementById(`${permType}-roles-list`);
    const roles = currentTicketPermissions[permType]?.roles || [];
    
    container.innerHTML = roles.map(role => `
        <div class="selected-item">
            <div class="item-info">
                <div class="item-color" style="background-color: ${role.color};"></div>
                <span class="item-name">${role.name}</span>
            </div>
            <button class="remove-btn" onclick="removeTicketRole('${permType}', '${role.id}')">✕</button>
        </div>
    `).join('') || '<div class="empty-state">No hay roles configurados</div>';
}

function renderTicketUsersList(permType) {
    const container = document.getElementById(`${permType}-users-list`);
    const users = currentTicketPermissions[permType]?.users || [];
    
    container.innerHTML = users.map(user => `
        <div class="selected-item">
            <div class="item-info">
                <img src="${user.avatar}" alt="Avatar" class="item-avatar">
                <span class="item-name">${user.name}</span>
            </div>
            <button class="remove-btn" onclick="removeTicketUser('${permType}', '${user.id}')">✕</button>
        </div>
    `).join('') || '<div class="empty-state">No hay usuarios configurados</div>';
}

async function addTicketRole(permType) {
    const selectElement = document.getElementById(`${permType}-role-select`);
    const roleId = selectElement.value;
    
    if (!roleId) {
        showToast('Selecciona un rol', 'error');
        return;
    }
    
    if (currentTicketChannelId === 'new') {
        const role = rolesData.find(r => r.id === roleId);
        if (!role) {
            showToast('Rol no encontrado', 'error');
            return;
        }
        
        if (!currentTicketConfig.permissions[permType].roles.includes(parseInt(roleId))) {
            saveSnapshot(`Rol añadido a permisos de ${permType}`);
            currentTicketConfig.permissions[permType].roles.push(parseInt(roleId));
            
            currentTicketPermissions[permType].roles.push({
                id: parseInt(roleId),
                name: role.name,
                color: role.color || '#99aab5'
            });
            
            selectElement.value = '';
            renderTicketPermissionItems();
            checkForChanges();
            showToast('Rol añadido correctamente', 'success');
        } else {
            showToast('El rol ya existe en este permiso', 'error');
        }
        return;
    }
    
    try {
        const response = await fetch(`/api/server/${window.serverId}/tickets/${currentTicketChannelId}/permissions/${permType}/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: roleId,
                item_type: 'roles'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Rol añadido correctamente', 'success');
            selectElement.value = '';
            loadTicketPermissions(currentTicketChannelId);
        } else {
            showToast(result.error || 'Error al añadir rol', 'error');
        }
    } catch (error) {
        console.error('Error adding role:', error);
        showToast('Error al añadir rol', 'error');
    }
}

async function addTicketUser(permType) {
    const inputElement = document.getElementById(`${permType}-user-input`);
    const userId = inputElement.value.trim();
    
    if (!userId || !userId.match(/^\d+$/)) {
        showToast('Ingresa un ID de usuario válido', 'error');
        return;
    }
    
    if (currentTicketChannelId === 'new') {
        if (!currentTicketConfig.permissions[permType].users.includes(parseInt(userId))) {
            saveSnapshot(`Usuario añadido a permisos de ${permType}`);
            currentTicketConfig.permissions[permType].users.push(parseInt(userId));
            
            currentTicketPermissions[permType].users.push({
                id: parseInt(userId),
                name: `Usuario ID: ${userId}`,
                avatar: 'https://cdn.discordapp.com/embed/avatars/0.png'
            });
            
            inputElement.value = '';
            renderTicketPermissionItems();
            checkForChanges();
            showToast('Usuario añadido correctamente', 'success');
        } else {
            showToast('El usuario ya existe en este permiso', 'error');
        }
        return;
    }
    
    try {
        const response = await fetch(`/api/server/${window.serverId}/tickets/${currentTicketChannelId}/permissions/${permType}/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: userId,
                item_type: 'users'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Usuario añadido correctamente', 'success');
            inputElement.value = '';
            loadTicketPermissions(currentTicketChannelId);
        } else {
            showToast(result.error || 'Error al añadir usuario', 'error');
        }
    } catch (error) {
        console.error('Error adding user:', error);
        showToast('Error al añadir usuario', 'error');
    }
}

async function removeTicketRole(permType, roleId) {
    if (currentTicketChannelId === 'new') {
        const roleIndex = currentTicketConfig.permissions[permType].roles.indexOf(parseInt(roleId));
        if (roleIndex > -1) {
            saveSnapshot(`Rol eliminado de permisos de ${permType}`);
            currentTicketConfig.permissions[permType].roles.splice(roleIndex, 1);
            
            const permRoleIndex = currentTicketPermissions[permType].roles.findIndex(r => r.id === parseInt(roleId));
            if (permRoleIndex > -1) {
                currentTicketPermissions[permType].roles.splice(permRoleIndex, 1);
            }
            
            renderTicketPermissionItems();
            checkForChanges();
            showToast('Rol eliminado correctamente', 'success');
        }
        return;
    }
    
    try {
        const response = await fetch(`/api/server/${window.serverId}/tickets/${currentTicketChannelId}/permissions/${permType}/remove`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: roleId,
                item_type: 'roles'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Rol eliminado correctamente', 'success');
            loadTicketPermissions(currentTicketChannelId);
        } else {
            showToast(result.error || 'Error al eliminar rol', 'error');
        }
    } catch (error) {
        console.error('Error removing role:', error);
        showToast('Error al eliminar rol', 'error');
    }
}

async function removeTicketUser(permType, userId) {
    if (currentTicketChannelId === 'new') {
        const userIndex = currentTicketConfig.permissions[permType].users.indexOf(parseInt(userId));
        if (userIndex > -1) {
            saveSnapshot(`Usuario eliminado de permisos de ${permType}`);
            currentTicketConfig.permissions[permType].users.splice(userIndex, 1);
            
            const permUserIndex = currentTicketPermissions[permType].users.findIndex(u => u.id === parseInt(userId));
            if (permUserIndex > -1) {
                currentTicketPermissions[permType].users.splice(permUserIndex, 1);
            }
            
            renderTicketPermissionItems();
            checkForChanges();
            showToast('Usuario eliminado correctamente', 'success');
        }
        return;
    }
    
    try {
        const response = await fetch(`/api/server/${window.serverId}/tickets/${currentTicketChannelId}/permissions/${permType}/remove`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                item_id: userId,
                item_type: 'users'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Usuario eliminado correctamente', 'success');
            loadTicketPermissions(currentTicketChannelId);
        } else {
            showToast(result.error || 'Error al eliminar usuario', 'error');
        }
    } catch (error) {
        console.error('Error removing user:', error);
        showToast('Error al eliminar usuario', 'error');
    }
}

function configureNewTicketPermissions() {
    if (!currentTicketConfig.permissions) {
        currentTicketConfig.permissions = {
            manage: { roles: [], users: [] },
            view: { roles: [], users: [] }
        };
    }
    
    currentTicketPermissions = {
        manage: {
            roles: currentTicketConfig.permissions.manage.roles.map(roleId => {
                const role = rolesData.find(r => r.id === String(roleId));
                return role ? {
                    id: roleId,
                    name: role.name,
                    color: role.color || '#99aab5'
                } : null;
            }).filter(Boolean),
            users: []
        },
        view: {
            roles: currentTicketConfig.permissions.view.roles.map(roleId => {
                const role = rolesData.find(r => r.id === String(roleId));
                return role ? {
                    id: roleId,
                    name: role.name,
                    color: role.color || '#99aab5'
                } : null;
            }).filter(Boolean),
            users: []
        }
    };
    
    currentTicketChannelId = 'new';
    renderTicketPermissionsEditor();
}

function resetCurrentStates() {
    resetPermissionsState();
    resetLogsState();
    resetTicketsState();
    resetCommandsState();
    closeAllModals();
}

function resetPermissionsState() {
    permissionsData = {};
    currentPermissionKey = null;
    currentPermissionDetails = null;
    rolesData = [];
    
    const editorContent = document.getElementById('permissions-editor-content');
    const editorTitle = document.getElementById('permissions-editor-title');
    const deleteBtn = document.getElementById('delete-permission-btn');
    
    if (editorContent) {
        editorContent.innerHTML = `
            <div class="welcome-state">
                <div class="welcome-icon">🔑</div>
                <h3>Gestión de Permisos</h3>
                <p>Selecciona una categoría y permiso para configurar quién puede usar las funciones específicas del bot.</p>
                <div class="welcome-features">
                    <div class="feature-item">
                        <span class="feature-icon">👥</span>
                        <span>Gestión de roles</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">👤</span>
                        <span>Gestión de usuarios</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">🛡️</span>
                        <span>Control granular</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">⚙️</span>
                        <span>Permisos personalizados</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    if (editorTitle) editorTitle.textContent = 'Selecciona un permiso para configurar';
    if (deleteBtn) deleteBtn.style.display = 'none';
}

function resetLogsState() {
    logsData = {};
    currentLogConfig = null;
    originalLogConfig = null;
    currentEditingLog = null;
    logChangeHistory = [];
    currentLogHistoryIndex = -1;
    hasLogChanges = false;
    
    const editorContent = document.getElementById('logs-editor-content');
    const editorTitle = document.getElementById('logs-editor-title');
    const cancelBtn = document.getElementById('cancel-logs-edit-btn');
    
    if (editorContent) {
        editorContent.innerHTML = `
            <div class="welcome-state">
                <div class="welcome-icon">📋</div>
                <h3>Configuración de Logs</h3>
                <p>Selecciona un tipo de log para configurarlo y comenzar a registrar eventos en tu servidor.</p>
                <div class="welcome-features">
                    <div class="feature-item">
                        <span class="feature-icon">⚙️</span>
                        <span>Personalización completa</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">📝</span>
                        <span>Mensajes personalizados</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">🎨</span>
                        <span>Embeds y colores</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">📊</span>
                        <span>Campos y parámetros</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    if (editorTitle) editorTitle.textContent = 'Selecciona un log para configurar';
    if (cancelBtn) cancelBtn.style.display = 'none';
    
    closeLogsPreview();
    updateLogUndoButton();
    updateLogSaveButton();
}

function resetTicketsState() {
    ticketsData = [];
    currentTicketConfig = null;
    originalTicketConfig = null;
    currentEditingTicket = null;
    channelsData = [];
    currentPermissionType = 'manage';
    isEditingButton = false;
    editingButtonIndex = -1;
    currentMessageType = 'open_message';
    hasTicketChanges = false;
    changeHistory = [];
    currentHistoryIndex = -1;
    currentTicketPermissions = null;
    currentTicketChannelId = null;
    
    const editorContent = document.getElementById('editor-content');
    const editorTitle = document.getElementById('editor-title');
    const cancelBtn = document.getElementById('cancel-edit-btn');
    
    if (editorContent) {
        editorContent.innerHTML = `
            <div class="welcome-state">
                <div class="welcome-icon">🎫</div>
                <h3>Configuración de Tickets</h3>
                <p>Selecciona un ticket existente para editarlo o crea uno nuevo para comenzar.</p>
                <div class="welcome-features">
                    <div class="feature-item">
                        <span class="feature-icon">⚙️</span>
                        <span>Personalización completa</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">🔒</span>
                        <span>Control de permisos</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">📝</span>
                        <span>Mensajes personalizados</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    if (editorTitle) editorTitle.textContent = 'Selecciona un ticket para editar';
    if (cancelBtn) cancelBtn.style.display = 'none';
    
    closePreview();
    updateUndoButton();
    updateSaveButton();
    updatePreviewButton();
}

function resetCommandsState() {
    commandsData = {};
    commandsChanges = {};
    updateSaveActions();
}
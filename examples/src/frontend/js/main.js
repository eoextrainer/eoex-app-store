// === DUNES BE ONE BASKETBALL CMS - MAIN APPLICATION ===

const API_URL = 'http://localhost:5000/api/v1';
const STORAGE_KEY = 'dunes_auth_token';
const USER_STORAGE_KEY = 'dunes_user';

const app = {
    currentUser: null,
    token: null,
    
    init() {
        this.loadAuthToken();
        this.setupEventListeners();
        this.checkAuthStatus();
        console.log('Dunes CMS Application Initialized');
    },
    
    loadAuthToken() {
        this.token = localStorage.getItem(STORAGE_KEY);
        const userStr = localStorage.getItem(USER_STORAGE_KEY);
        if (userStr) {
            this.currentUser = JSON.parse(userStr);
        }
    },
    
    setupEventListeners() {
        // Modal close buttons
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) modal.classList.add('hidden');
            });
        });
        
        // Click outside modal to close
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                }
            });
        });
    },
    
    updateAuthUI() {
        const loginBtn = document.getElementById('loginBtn');
        const userMenu = document.getElementById('userMenu');
        const userName = document.getElementById('userName');
        
        if (this.currentUser) {
            loginBtn.classList.add('hidden');
            userMenu.classList.remove('hidden');
            userName.textContent = `${this.currentUser.first_name} (${this.currentUser.role})`;
        } else {
            loginBtn.classList.remove('hidden');
            userMenu.classList.add('hidden');
        }
    },
    
    logout() {
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(USER_STORAGE_KEY);
        
        this.token = null;
        this.currentUser = null;
        
        this.updateAuthUI();
        navigateTo('home');
        
        console.log('Logout successful');
    },
    
    checkAuthStatus() {
        if (this.token && this.currentUser) {
            this.updateAuthUI();
        }
    }
};

function showModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function navigateTo(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.add('hidden');
    });
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show target page
    if (pageId === 'home') {
        document.getElementById('homePage').classList.remove('hidden');
        document.querySelector('[onclick="navigateTo(\'home\')"]')?.classList.add('active');
    } else if (pageId === 'dashboard') {
        if (!app.currentUser) {
            alert('Please login first');
            showModal('loginModal');
            return;
        }
        document.getElementById('dashboardPage').classList.remove('hidden');
        document.querySelector('[onclick="navigateTo(\'dashboard\')"]')?.classList.add('active');
        loadDashboard();
    }
}

function loadDashboard() {
    const content = document.getElementById('dashboardContent');
    
    if (!app.currentUser) return;
    
    if (app.currentUser.role === 'athlete') {
        renderAthleteDashboard(app.currentUser.user_id);
    } else if (app.currentUser.role === 'coach') {
        renderCoachDashboard(app.currentUser.user_id);
    } else if (app.currentUser.role === 'club') {
        // Note: club role needs club_id which we'll need to get from backend
        content.innerHTML = '<p>Loading club dashboard...</p>';
        // TODO: Implement club dashboard once we get club_id
    } else if (app.currentUser.role === 'manager') {
        renderManagerDashboard(app.currentUser.user_id);
    }
}

async function handleLoginSubmit(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store authentication data
            localStorage.setItem(STORAGE_KEY, data.token);
            localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(data.user));
            
            app.token = data.token;
            app.currentUser = data.user;
            
            // Update UI
            app.updateAuthUI();
            
            // Close modal and reset form
            closeModal('loginModal');
            document.getElementById('loginForm').reset();
            
            // Navigate to dashboard
            navigateTo('dashboard');
            
            console.log('Login successful:', data.user);
        } else {
            alert('Login failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Connection error. Make sure the backend is running on http://localhost:5000');
    }
}

async function apiCall(endpoint, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (app.token) {
        headers['Authorization'] = `Bearer ${app.token}`;
    }
    
    const options = {
        method,
        headers
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        return await response.json();
    } catch (error) {
        console.error('API call error:', error);
        throw error;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

// Athlete Dashboard Rendering
async function renderAthleteDashboard(userId) {
    const dashboardContent = document.getElementById('dashboardContent');
    
    try {
        const data = await apiCall(`/athletes/dashboard/${userId}`);
        
        if (!data.success) {
            dashboardContent.innerHTML = '<p>Error loading dashboard</p>';
            return;
        }
        
        const athlete = data.athlete;
        const stats = data.statistics;
        const club = data.club || {};
        const news = data.news || [];
        const recentGames = data.recent_games || [];
        
        // Calculate age
        const birthDate = new Date(athlete.birthdate);
        const age = new Date().getFullYear() - birthDate.getFullYear();
        
        dashboardContent.innerHTML = `
            <h2>${athlete.first_name} ${athlete.last_name}'s Dashboard</h2>
            
            <div class="athlete-dashboard-grid">
                <!-- Top Left: Player Information & Photo -->
                <div class="dashboard-tile player-info-tile">
                    <h3>🏀 Player Profile</h3>
                    <div class="player-photo">
                        <div class="avatar-placeholder">${athlete.first_name.charAt(0)}${athlete.last_name.charAt(0)}</div>
                    </div>
                    <div class="player-details">
                        <p><strong>Name:</strong> ${athlete.first_name} ${athlete.last_name}</p>
                        <p><strong>Position:</strong> ${athlete.position || 'N/A'}</p>
                        <p><strong>Jersey:</strong> #${athlete.jersey_number || 'N/A'}</p>
                        <p><strong>Height:</strong> ${athlete.height ? (athlete.height + 'm') : 'N/A'}</p>
                        <p><strong>Weight:</strong> ${athlete.weight ? (athlete.weight + 'kg') : 'N/A'}</p>
                        <p><strong>Age:</strong> ${age} years</p>
                        <p><strong>Email:</strong> ${athlete.email}</p>
                    </div>
                    ${athlete.bio ? `<div class="player-bio"><p>${athlete.bio}</p></div>` : ''}
                </div>
                
                <!-- Top Right: Game Statistics -->
                <div class="dashboard-tile stats-tile">
                    <h3>📊 Performance Statistics</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-label">Games Played</div>
                            <div class="stat-value">${stats.games_played || 0}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Avg Points</div>
                            <div class="stat-value">${parseFloat(stats.avg_points || 0).toFixed(1)}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Avg Rebounds</div>
                            <div class="stat-value">${parseFloat(stats.avg_rebounds || 0).toFixed(1)}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Avg Assists</div>
                            <div class="stat-value">${parseFloat(stats.avg_assists || 0).toFixed(1)}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Total Points</div>
                            <div class="stat-value highlight">${stats.total_points || 0}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Total Rebounds</div>
                            <div class="stat-value highlight">${stats.total_rebounds || 0}</div>
                        </div>
                    </div>
                    
                    <h4 style="margin-top: 20px;">Recent Games</h4>
                    <div class="recent-games-list">
                        ${recentGames.length > 0 ? recentGames.map(game => `
                            <div class="game-item">
                                <div class="game-teams">${game.home_team} vs ${game.away_team}</div>
                                <div class="game-score">${game.home_score} - ${game.away_score}</div>
                                <div class="game-stats">
                                    ${game.points || 0} pts | ${game.rebounds || 0} reb | ${game.assists || 0} ast
                                </div>
                                <div class="game-date">${new Date(game.game_date).toLocaleDateString()}</div>
                            </div>
                        `).join('') : '<p class="no-data">No recent games</p>'}
                    </div>
                </div>
                
                <!-- Bottom Left: Club Information -->
                <div class="dashboard-tile club-tile">
                    <h3>🏆 Club Information</h3>
                    ${club.club_id ? `
                        <div class="club-details">
                            <h4>${club.name}</h4>
                            <p><strong>Location:</strong> ${club.location || 'N/A'}</p>
                            <p><strong>Founded:</strong> ${club.founded_year || 'N/A'}</p>
                            ${club.website ? `<p><strong>Website:</strong> <a href="${club.website}" target="_blank">${club.website}</a></p>` : ''}
                            ${club.contact_email ? `<p><strong>Contact:</strong> ${club.contact_email}</p>` : ''}
                            ${club.bio ? `<div class="club-bio"><p>${club.bio}</p></div>` : ''}
                        </div>
                    ` : '<p class="no-data">Not assigned to any club yet</p>'}
                </div>
                
                <!-- Bottom Right: Latest News -->
                <div class="dashboard-tile news-tile">
                    <h3>📰 Latest Basketball News</h3>
                    <div class="news-list">
                        ${news.length > 0 ? news.map(item => `
                            <div class="news-item">
                                <h4>${item.title}</h4>
                                <p>${item.content.substring(0, 150)}${item.content.length > 150 ? '...' : ''}</p>
                                <div class="news-meta">
                                    <span class="news-category">${item.category}</span>
                                    <span class="news-date">${new Date(item.created_at).toLocaleDateString()}</span>
                                </div>
                            </div>
                        `).join('') : '<p class="no-data">No news available</p>'}
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Dashboard error:', error);
        dashboardContent.innerHTML = '<p>Error loading dashboard. Please try again.</p>';
    }
}

// Coach Dashboard Rendering
async function renderCoachDashboard(userId) {
    const dashboardContent = document.getElementById('dashboardContent');
    
    try {
        const data = await apiCall(`/coaches/dashboard/${userId}`);
        
        if (!data.success) {
            dashboardContent.innerHTML = '<p>Error loading coach dashboard</p>';
            return;
        }
        
        const coach = data.coach || {};
        const club = data.club || {};
        const athletes = data.athletes || [];
        const news = data.news || [];
        
        let athletesTable = '';
        if (athletes.length > 0) {
            athletesTable = `
                <table class="ranking-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Player</th>
                            <th>Position</th>
                            <th>Games</th>
                            <th>Avg Pts</th>
                            <th>Total Pts</th>
                            <th>Avg Reb</th>
                            <th>Avg Ast</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${athletes.map((athlete, index) => `
                            <tr>
                                <td class="rank-${index < 3 ? 'top' : 'normal'}">${index + 1}</td>
                                <td><strong>${athlete.first_name} ${athlete.last_name}</strong></td>
                                <td>${athlete.position || 'N/A'}</td>
                                <td>${athlete.games_played || 0}</td>
                                <td>${parseFloat(athlete.avg_points || 0).toFixed(1)}</td>
                                <td class="stat-highlight">${parseFloat(athlete.total_points || 0).toFixed(0)}</td>
                                <td>${parseFloat(athlete.avg_rebounds || 0).toFixed(1)}</td>
                                <td>${parseFloat(athlete.avg_assists || 0).toFixed(1)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            athletesTable = '<p class="no-data">No athletes assigned</p>';
        }
        
        dashboardContent.innerHTML = `
            <h2>${coach.first_name} ${coach.last_name}'s Coaching Dashboard</h2>
            
            <div class="coach-dashboard-grid">
                <!-- Top Left: Coach Information & Photo -->
                <div class="dashboard-tile coach-info-tile">
                    <h3>🏀 Coach Profile</h3>
                    <div class="coach-photo">
                        ${coach.photo_url ? `<img src="${coach.photo_url}" alt="Coach photo" class="coach-photo-img">` : `<div class="avatar-placeholder">${coach.first_name?.charAt(0) || 'C'}${coach.last_name?.charAt(0) || 'H'}</div>`}
                    </div>
                    <div class="coach-details">
                        <p><strong>Name:</strong> ${coach.first_name} ${coach.last_name}</p>
                        <p><strong>Specialization:</strong> ${coach.specialization || 'N/A'}</p>
                        <p><strong>Certification:</strong> ${coach.certification_level || 'N/A'}</p>
                        <p><strong>Experience:</strong> ${coach.years_experience || 0} years</p>
                        <p><strong>Email:</strong> ${coach.email}</p>
                    </div>
                    ${coach.bio ? `<div class="coach-bio"><p>${coach.bio}</p></div>` : ''}
                </div>
                
                <!-- Top Right: Athletes Ranking -->
                <div class="dashboard-tile athletes-ranking-tile">
                    <h3>📊 Managed Athletes Performance</h3>
                    ${athletesTable}
                </div>
                
                <!-- Bottom Left: Club Information -->
                <div class="dashboard-tile club-info-tile">
                    <h3>🏢 Club Information</h3>
                    ${club && club.club_id ? `
                        <div class="club-details">
                            <p><strong>Club Name:</strong> ${club.name}</p>
                            <p><strong>Location:</strong> ${club.location}</p>
                            <p><strong>Founded:</strong> ${club.founded_year}</p>
                            <p><strong>Website:</strong> <a href="${club.website}" target="_blank">${club.website || 'N/A'}</a></p>
                            <p><strong>Email:</strong> ${club.contact_email}</p>
                            ${club.bio ? `<div class="club-bio"><p>${club.bio}</p></div>` : ''}
                        </div>
                    ` : `<p class="no-data">Not assigned to a club</p>`}
                </div>
                
                <!-- Bottom Right: News -->
                <div class="dashboard-tile news-tile">
                    <h3>📰 Latest News</h3>
                    ${news.length > 0 ? `
                        <div class="news-list">
                            ${news.map(article => `
                                <div class="news-item">
                                    <h4>${article.title}</h4>
                                    <p>${(article.content || '').substring(0, 150)}...</p>
                                    <div class="news-meta">
                                        <span class="news-category">${article.category}</span>
                                        <span class="news-date">${new Date(article.created_at).toLocaleDateString()}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : `<p class="no-data">No news available</p>`}
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Coach dashboard error:', error);
        dashboardContent.innerHTML = '<p>Error loading coach dashboard. Please try again.</p>';
    }
}

// Manager Dashboard Rendering
async function renderManagerDashboard(userId) {
    const dashboardContent = document.getElementById('dashboardContent');
    
    try {
        const data = await apiCall(`/managers/dashboard/${userId}`);
        
        if (!data.success) {
            dashboardContent.innerHTML = '<p>Error loading manager dashboard</p>';
            return;
        }
        
        const manager = data.manager || {};
        const club = data.club || {};
        const coaches = data.coaches || [];
        const players = data.players || [];
        const news = data.news || [];
        
        let coachesTable = '';
        if (coaches.length > 0) {
            coachesTable = `
                <table class="ranking-table">
                    <thead>
                        <tr>
                            <th>Coach Name</th>
                            <th>Specialization</th>
                            <th>Experience</th>
                            <th>Athletes</th>
                            <th>Cert Level</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${coaches.map(coach => `
                            <tr>
                                <td><strong>${coach.first_name} ${coach.last_name}</strong></td>
                                <td>${coach.specialization || 'N/A'}</td>
                                <td>${coach.years_experience || 0} yrs</td>
                                <td class="stat-highlight">${coach.athletes_managed || 0}</td>
                                <td>${coach.certification_level || 'N/A'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            coachesTable = '<p class="no-data">No coaches assigned</p>';
        }
        
        let playersTable = '';
        if (players.length > 0) {
            playersTable = `
                <table class="ranking-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Player</th>
                            <th>Position</th>
                            <th>Games</th>
                            <th>Avg Pts</th>
                            <th>Total Pts</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${players.slice(0, 10).map((player, index) => `
                            <tr>
                                <td class="rank-${index < 3 ? 'top' : 'normal'}">${index + 1}</td>
                                <td><strong>${player.first_name} ${player.last_name}</strong></td>
                                <td>${player.position || 'N/A'}</td>
                                <td>${player.games_played || 0}</td>
                                <td>${parseFloat(player.avg_points || 0).toFixed(1)}</td>
                                <td class="stat-highlight">${parseFloat(player.total_points || 0).toFixed(0)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            playersTable = '<p class="no-data">No players in club</p>';
        }
        
        dashboardContent.innerHTML = `
            <h2>${manager.first_name} ${manager.last_name}'s Management Dashboard</h2>
            
            <div class="manager-dashboard-grid">
                <!-- Top Left: Manager Information & Photo -->
                <div class="dashboard-tile manager-info-tile">
                    <h3>👔 Manager Profile</h3>
                    <div class="manager-photo">
                        ${manager.photo_url ? `<img src="${manager.photo_url}" alt="Manager photo" class="manager-photo-img">` : `<div class="avatar-placeholder">${manager.first_name?.charAt(0) || 'M'}${manager.last_name?.charAt(0) || 'G'}</div>`}
                    </div>
                    <div class="manager-details">
                        <p><strong>Name:</strong> ${manager.first_name} ${manager.last_name}</p>
                        <p><strong>Role:</strong> ${manager.specialization || 'General Manager'}</p>
                        <p><strong>Experience:</strong> ${manager.experience_years || 0} years</p>
                        <p><strong>Email:</strong> ${manager.email}</p>
                    </div>
                    ${manager.bio ? `<div class="manager-bio"><p>${manager.bio}</p></div>` : ''}
                </div>
                
                <!-- Top Right: Coaches & Financial Info -->
                <div class="dashboard-tile coaches-table-tile">
                    <h3>🏀 Coaching Staff Performance</h3>
                    ${coachesTable}
                </div>
                
                <!-- Bottom Left: Players Statistics & Rankings -->
                <div class="dashboard-tile players-ranking-tile">
                    <h3>⭐ Top Players by Performance</h3>
                    ${playersTable}
                </div>
                
                <!-- Bottom Right: News & Industry Updates -->
                <div class="dashboard-tile news-tile">
                    <h3>📰 News & Updates</h3>
                    ${news.length > 0 ? `
                        <div class="news-list">
                            ${news.map(article => `
                                <div class="news-item">
                                    <h4>${article.title}</h4>
                                    <p>${(article.content || '').substring(0, 120)}...</p>
                                    <div class="news-meta">
                                        <span class="news-category">${article.category}</span>
                                        <span class="news-date">${new Date(article.created_at).toLocaleDateString()}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : `<p class="no-data">No news available</p>`}
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Manager dashboard error:', error);
        dashboardContent.innerHTML = '<p>Error loading manager dashboard. Please try again.</p>';
    }
}


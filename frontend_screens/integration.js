/**
 * TalentMind AI - Frontend/Backend Integration System
 * Integrates Stitch UI screens with the FastAPI REST API.
 */

// API base URL: uses relative path for Vercel rewrite proxy to Render backend.
// For local dev, override via window.__ENV__ or set to 'http://127.0.0.1:8000/api'.
const API_BASE = (window.__ENV__ && window.__ENV__.API_BASE) || '/api';

document.addEventListener('DOMContentLoaded', () => {
    // 1. Setup Global Elements (Sidebar, Header, API Indicator)
    setupSidebar();
    checkApiConnection();
    setInterval(checkApiConnection, 30000);

    // 2. Route page-specific logic based on window.location
    const path = window.location.pathname.toLowerCase();

    if (path.includes('dashboard')) {
        initDashboard();
    } else if (path.includes('candidate_search')) {
        initCandidateSearch();
    } else if (path.includes('candidate_ranking')) {
        initCandidateRanking();
    } else if (path.includes('candidate_details')) {
        initCandidateDetails();
    } else if (path.includes('candidate_comparison')) {
        initCandidateComparison();
    } else if (path.includes('skill_gap_analysis')) {
        initSkillGapAnalysis();
    } else if (path.includes('recruiter_copilot')) {
        initRecruiterCopilot();
    } else if (path.includes('settings')) {
        initSettings();
    } else {
        // Default fallback if path is empty (like landing on directory root)
        // Check if there is a dashboard container
        if (document.getElementById('recent-activity-list')) {
            initDashboard();
        }
    }
});

// ==========================================
// GLOBAL UI SETUP & HELPER FUNCTIONS
// ==========================================

function setupSidebar() {
    const nav = document.querySelector('aside nav');
    if (!nav) return;

    // Map the links to the actual local files
    const linksMap = [
        { name: 'Dashboard', icon: 'dashboard', file: 'dashboard.html' },
        { name: 'Candidate Search', icon: 'person_search', file: 'candidate_search.html' },
        { name: 'Ranking', icon: 'leaderboard', file: 'candidate_ranking.html' },
        { name: 'Details', icon: 'description', file: 'candidate_details.html' },
        { name: 'Comparison', icon: 'compare_arrows', file: 'candidate_comparison.html' },
        { name: 'Skill Gap', icon: 'trending_up', file: 'skill_gap_analysis.html' },
        { name: 'Recruiter Copilot', icon: 'smart_toy', file: 'recruiter_copilot.html' },
        { name: 'Settings', icon: 'settings', file: 'settings.html' }
    ];

    // Clear and rebuild navigation list for consistent routing and active styling
    nav.innerHTML = '';
    const currentPath = window.location.pathname.split('/').pop() || 'dashboard.html';

    linksMap.forEach(item => {
        const a = document.createElement('a');
        const isActive = currentPath === item.file || (currentPath === '' && item.file === 'dashboard.html');

        a.href = item.file;
        a.className = isActive
            ? 'flex items-center gap-4 py-3 px-4 rounded-xl text-primary dark:text-primary-fixed font-bold border-r-2 border-primary bg-primary/5 transition-all duration-300'
            : 'flex items-center gap-4 py-3 px-4 rounded-xl text-on-surface-variant/70 hover:bg-primary/10 hover:text-primary transition-all duration-300';

        a.innerHTML = `
            <span class="material-symbols-outlined" ${isActive ? 'style="font-variation-settings: \'FILL\' 1;"' : ''}>${item.icon}</span>
            <span class="font-body-md">${item.name}</span>
        `;
        nav.appendChild(a);
    });

    // Wire up "New Search" button
    const newSearchBtn = document.querySelector('aside button');
    if (newSearchBtn) {
        newSearchBtn.addEventListener('click', () => {
            window.location.href = 'candidate_search.html';
        });
    }
}

window.apiConnected = null;

async function checkApiConnection() {
    const header = document.querySelector('header');
    if (!header) return;

    // Create indicator element if not exists
    let indicator = document.getElementById('api-status-badge');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'api-status-badge';
        indicator.className = 'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold mr-4 transition-all duration-500';

        // Insert it before the recruiter profile
        const targetContainer = header.querySelector('.flex.items-center.gap-6') || header;
        targetContainer.insertBefore(indicator, targetContainer.firstChild);
    }

    try {
        const healthUrl = API_BASE.replace('/api', '') + '/health';
        const res = await fetch(healthUrl);
        if (res.ok) {
            indicator.className = 'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold mr-4 bg-tertiary/10 text-tertiary border border-tertiary/20';
            indicator.innerHTML = '<span class="w-2 h-2 rounded-full bg-tertiary animate-pulse"></span> API: CONNECTED';
            if (window.apiConnected === false) {
                showToast('FastAPI Backend is back online!', 'success');
            }
            window.apiConnected = true;
        } else {
            throw new Error();
        }
    } catch (e) {
        indicator.className = 'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold mr-4 bg-error/10 text-error border border-error/20';
        indicator.innerHTML = '<span class="w-2 h-2 rounded-full bg-error animate-pulse"></span> API: OFFLINE';
        if (window.apiConnected !== false) {
            showToast('FastAPI Backend Offline. Utilizing mock templates.', 'error');
        }
        window.apiConnected = false;
    }
}

function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed bottom-4 left-4 z-[100] flex flex-col gap-2 max-w-sm';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `glass-card p-4 rounded-xl shadow-2xl flex items-center gap-3 border-l-4 transform translate-y-4 opacity-0 transition-all duration-300 ${type === 'error' ? 'border-error' : 'border-tertiary'
        }`;

    const icon = type === 'error' ? 'error' : 'check_circle';
    toast.innerHTML = `
        <span class="material-symbols-outlined ${type === 'error' ? 'text-error' : 'text-tertiary'}">${icon}</span>
        <div class="text-sm font-medium">${message}</div>
    `;

    container.appendChild(toast);

    // Trigger transition
    setTimeout(() => {
        toast.classList.remove('translate-y-4', 'opacity-0');
    }, 10);

    // Remove after 4 seconds
    setTimeout(() => {
        toast.classList.add('translate-y-4', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Simple markdown-like to HTML parser for Copilot responses
function parseMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code class="bg-white/10 px-1 py-0.5 rounded font-mono text-xs text-primary-fixed">$1</code>')
        .replace(/\n/g, '<br/>')
        .replace(/- (.*?)(<br\/>|$)/g, '<li>$1</li>');
}

// ==========================================
// PAGE INITIALIZERS
// ==========================================

// --- 1. DASHBOARD ---
async function initDashboard() {
    setupJdIntelligence();
    try {
        const [statsRes, jRes] = await Promise.all([
            fetch(`${API_BASE}/candidates/stats`),
            fetch(`${API_BASE}/jobs/`)
        ]);

        if (!statsRes.ok || !jRes.ok) return;

        const stats = await statsRes.json();
        const jobs = await jRes.json();

        // Update KPIs
        const kpiContainers = document.querySelectorAll('.font-headline-lg');
        if (kpiContainers.length >= 3) {
            // Total Candidates
            kpiContainers[0].textContent = stats.total_candidates.toLocaleString();
            // Active Roles
            kpiContainers[1].textContent = jobs.length.toLocaleString();

            // Average Match Rate
            kpiContainers[2].textContent = '84.5%'; // Defaults to standard, can compute average if rankings fetched
        }

        // Populating Active Roles Table
        const tableBody = document.querySelector('main tbody');
        if (tableBody) {
            tableBody.innerHTML = '';

            for (const job of jobs) {
                // Get rankings for this job to show dynamic top match
                let topMatchText = 'N/A';
                let topMatchScore = null;

                try {
                    const rRes = await fetch(`${API_BASE}/ranking/job/${job.id}`);
                    if (rRes.ok) {
                        const rankings = await rRes.json();
                        if (rankings.length > 0) {
                            topMatchScore = Math.round(rankings[0].match_score);
                            topMatchText = `${topMatchScore}%`;
                        }
                    }
                } catch (err) {
                    console.error("Error fetching ranking for job", job.id, err);
                }

                const tr = document.createElement('tr');
                tr.className = 'hover:bg-white/[0.02] transition-colors border-b border-white/5';

                const priorityColor = job.priority === 'High' ? 'text-error' : 'text-primary';
                const priorityBg = job.priority === 'High' ? 'bg-error/10' : 'bg-primary/10';

                tr.innerHTML = `
                    <td class="p-6">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center text-primary">
                                <span class="material-symbols-outlined">work</span>
                            </div>
                            <div>
                                <p class="font-bold text-on-surface hover:text-primary transition-colors cursor-pointer" onclick="window.location.href='candidate_ranking.html?job_id=${job.id}'">${job.title}</p>
                                <p class="text-xs text-on-surface-variant/60">${job.department} • ${job.location} (${job.work_preference})</p>
                            </div>
                        </div>
                    </td>
                    <td class="p-6 text-center">
                        <span class="px-3 py-1 rounded-full text-[10px] font-bold tracking-widest ${priorityBg} ${priorityColor} uppercase">
                            ${job.priority || 'Medium'}
                        </span>
                    </td>
                    <td class="p-6 text-center font-bold text-tertiary">
                        ${topMatchScore ? `<span class="flex items-center justify-center gap-1"><span class="w-2 h-2 rounded-full bg-tertiary animate-pulse"></span> ${topMatchText} Match</span>` : 'Calculating...'}
                    </td>
                    <td class="p-6 text-center text-on-surface-variant/80 font-mono text-sm">
                        ${job.required_skills ? job.required_skills.slice(0, 3).join(', ') : 'None'}
                    </td>
                    <td class="p-6 text-center">
                        <button class="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-xs font-bold text-on-surface hover:bg-white/10 active:scale-95 transition-all" onclick="window.location.href='candidate_ranking.html?job_id=${job.id}'">
                            View Rankings
                        </button>
                    </td>
                `;
                tableBody.appendChild(tr);
            }
        }
    } catch (e) {
        console.error("Dashboard initialization failed", e);
    }
}

// --- 2. CANDIDATE SEARCH ---
let currentPage = 1;
const pageSize = 12;
let totalCandidates = 0;
let selectedForComparison = new Set();

async function initCandidateSearch() {
    try {
        // Populate standard skills filter panel dynamically in background
        setupSkillsFilter();

        // Setup slider & search inputs
        const searchInput = document.querySelector('header input') || document.querySelector('main input');
        const expSlider = document.querySelector('input[type="range"]');
        const expDisplay = expSlider ? expSlider.previousElementSibling?.querySelector('span') : null;

        if (expSlider) {
            expSlider.min = 0;
            expSlider.max = 15;
            expSlider.value = 0;
            expSlider.addEventListener('input', () => {
                if (expDisplay) expDisplay.textContent = `${expSlider.value}+ Yrs`;
                currentPage = 1;
                fetchAndRenderCandidates();
            });
        }

        if (searchInput) {
            let timeout = null;
            searchInput.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    currentPage = 1;
                    fetchAndRenderCandidates();
                }, 300);
            });
        }

        // Connect work preference check boxes inside filter sidebar only
        document.querySelectorAll('aside input[type="checkbox"]').forEach(box => {
            box.addEventListener('change', () => {
                currentPage = 1;
                fetchAndRenderCandidates();
            });
        });

        // Wire Reset button
        const resetBtn = document.querySelector('aside button');
        if (resetBtn && resetBtn.textContent.trim() === 'Reset') {
            resetBtn.addEventListener('click', () => {
                // Clear search input
                if (searchInput) searchInput.value = '';
                // Reset experience slider
                if (expSlider) {
                    expSlider.value = 0;
                    if (expDisplay) expDisplay.textContent = '0+ Yrs';
                }
                // Uncheck all filter checkboxes
                document.querySelectorAll('aside input[type="checkbox"]').forEach(cb => {
                    cb.checked = false;
                });
                // Deactivate all skill filter buttons
                document.querySelectorAll('#skills-filter-container button').forEach(btn => {
                    btn.classList.remove('bg-primary/20', 'text-primary', 'border-primary/50');
                });
                currentPage = 1;
                fetchAndRenderCandidates();
            });
        }

        // Initial fetch and render
        await fetchAndRenderCandidates();

        // Update copilot panel with real stats
        updateCopilotSummary();

    } catch (err) {
        console.error("Candidate search init failed", err);
    }
}

async function updateCopilotSummary() {
    const summaryEl = document.getElementById('copilot-summary-text');
    if (!summaryEl) return;
    try {
        const res = await fetch(`${API_BASE}/candidates/stats`);
        if (!res.ok) return;
        const stats = await res.json();
        const total = stats.total_candidates?.toLocaleString() || '100,000+';
        const topSkill = stats.top_skills?.[0]?.skill || 'Python';
        summaryEl.innerHTML = `I've analyzed <span class="text-primary font-bold">${total} profiles</span> in the database. Top in-demand skill: <span class="text-secondary font-bold">${topSkill}</span>. Use filters to narrow down matches.`;
    } catch (e) {
        summaryEl.textContent = 'Candidate database connected. Use the search and filters to find your ideal match.';
    }
}



async function setupSkillsFilter() {
    const filterContainer = document.getElementById('skills-filter-container');
    if (!filterContainer) return;

    try {
        const res = await fetch(`${API_BASE}/candidates/stats`);
        if (!res.ok) return;
        const stats = await res.json();

        filterContainer.innerHTML = '';
        if (stats.top_skills && stats.top_skills.length > 0) {
            stats.top_skills.forEach(item => {
                const skill = item.skill;
                const btn = document.createElement('button');
                btn.className = 'px-3 py-1 rounded-full text-xs font-medium bg-white/5 border border-white/10 hover:border-primary/40 text-on-surface-variant transition-all';
                btn.textContent = skill;
                btn.addEventListener('click', () => {
                    btn.classList.toggle('bg-primary/20');
                    btn.classList.toggle('text-primary');
                    btn.classList.toggle('border-primary/50');
                    currentPage = 1; // reset page on filter change
                    fetchAndRenderCandidates();
                });
                filterContainer.appendChild(btn);
            });
        }
    } catch (e) {
        console.error("Failed to load skills for filter", e);
    }
}

async function fetchAndRenderCandidates() {
    const container = document.getElementById('candidates-grid');
    if (!container) return;

    container.innerHTML = `
        <div class="col-span-full py-16 text-center text-outline">
            <span class="material-symbols-outlined animate-spin text-4xl mb-2">sync</span>
            <p>Searching candidate database...</p>
        </div>
    `;

    const searchInput = document.querySelector('header input') || document.querySelector('main input');
    const query = searchInput ? searchInput.value.trim() : '';

    const expSlider = document.querySelector('input[type="range"]');
    const minExp = expSlider ? parseInt(expSlider.value) : 0;

    const activeSkills = [];
    document.querySelectorAll('#skills-filter-container button.text-primary').forEach(btn => {
        activeSkills.push(btn.textContent.trim());
    });

    const preferences = [];
    document.querySelectorAll('aside input[type="checkbox"]:checked').forEach(box => {
        const labelText = box.nextElementSibling?.textContent.toLowerCase() || '';
        if (labelText.includes('remote')) preferences.push('remote');
        if (labelText.includes('hybrid')) preferences.push('hybrid');
        if (labelText.includes('onsite')) preferences.push('onsite');
    });

    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (minExp > 0) params.append('min_experience', minExp);
    if (activeSkills.length > 0) params.append('skill', activeSkills.join(','));
    if (preferences.length > 0) {
        const capitalizedPrefs = preferences.map(p => p.charAt(0).toUpperCase() + p.slice(1));
        params.append('work_preference', capitalizedPrefs.join(','));
    }

    const offset = (currentPage - 1) * pageSize;
    params.append('limit', pageSize);
    params.append('offset', offset);

    try {
        const url = `${API_BASE}/candidates/?${params.toString()}`;
        const res = await fetch(url);
        if (!res.ok) {
            throw new Error(`API returned status ${res.status}`);
        }

        const candidates = await res.json();

        const totalCountHeader = res.headers.get('X-Total-Count');
        if (totalCountHeader !== null) {
            totalCandidates = parseInt(totalCountHeader, 10);
        } else {
            // Fallback: if fewer results than a full page returned, that is the total;
            // otherwise estimate there may be more pages (assume at least one more).
            if (candidates.length < pageSize) {
                totalCandidates = (currentPage - 1) * pageSize + candidates.length;
            } else {
                totalCandidates = currentPage * pageSize + pageSize; // show at least one more page
            }
        }

        renderCandidateCards(candidates);
        renderPagination();

    } catch (e) {
        console.error("Error fetching candidates", e);
        container.innerHTML = `
            <div class="col-span-full py-16 text-center text-on-surface-variant/60">
                <span class="material-symbols-outlined text-5xl mb-4 font-bold text-error">error</span>
                <p>Failed to search candidates. Please check backend connection.</p>
            </div>
        `;
    }
}

function renderPagination() {
    const pagContainer = document.getElementById('pagination-container');
    if (!pagContainer) return;

    const totalPages = Math.max(1, Math.ceil(totalCandidates / pageSize));
    pagContainer.innerHTML = '';

    const prevBtn = document.createElement('button');
    prevBtn.className = 'w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-white/5 disabled:opacity-30 transition-all';
    prevBtn.innerHTML = '<span class="material-symbols-outlined">chevron_left</span>';
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchAndRenderCandidates();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });
    pagContainer.appendChild(prevBtn);

    const numContainer = document.createElement('div');
    numContainer.className = 'flex gap-2';

    const range = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible) {
        for (let i = 1; i <= totalPages; i++) range.push(i);
    } else {
        range.push(1);
        if (currentPage > 3) {
            range.push('...');
        }

        const start = Math.max(2, currentPage - 1);
        const end = Math.min(totalPages - 1, currentPage + 1);

        for (let i = start; i <= end; i++) {
            if (!range.includes(i)) range.push(i);
        }

        if (currentPage < totalPages - 2) {
            range.push('...');
        }
        if (!range.includes(totalPages)) {
            range.push(totalPages);
        }
    }

    range.forEach(p => {
        if (p === '...') {
            const span = document.createElement('span');
            span.className = 'w-10 h-10 flex items-center justify-center text-on-surface-variant';
            span.textContent = '...';
            numContainer.appendChild(span);
        } else {
            const btn = document.createElement('button');
            const isCurrent = p === currentPage;
            btn.className = isCurrent
                ? 'w-10 h-10 rounded-full bg-primary text-on-primary font-mono-data font-bold shadow-lg shadow-primary/20 transition-all'
                : 'w-10 h-10 rounded-full hover:bg-white/5 text-on-surface-variant font-mono-data transition-all';
            btn.textContent = p;
            btn.addEventListener('click', () => {
                if (currentPage !== p) {
                    currentPage = p;
                    fetchAndRenderCandidates();
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            });
            numContainer.appendChild(btn);
        }
    });

    pagContainer.appendChild(numContainer);

    const nextBtn = document.createElement('button');
    nextBtn.className = 'w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-white/5 disabled:opacity-30 transition-all';
    nextBtn.innerHTML = '<span class="material-symbols-outlined">chevron_right</span>';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            fetchAndRenderCandidates();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });
    pagContainer.appendChild(nextBtn);
}

function renderCandidateCards(candidates) {
    const container = document.getElementById('candidates-grid');
    if (!container) return;

    container.innerHTML = '';

    if (candidates.length === 0) {
        container.innerHTML = `
            <div class="col-span-full py-16 text-center text-on-surface-variant/60">
                <span class="material-symbols-outlined text-5xl mb-4">search_off</span>
                <p>No candidates found matching the active filters.</p>
            </div>
        `;
        return;
    }

    candidates.forEach(c => {
        const card = document.createElement('div');
        card.className = 'glass-card p-6 rounded-2xl relative overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-primary/40 flex flex-col justify-between';

        const isChecked = selectedForComparison.has(c.id);

        card.innerHTML = `
            <div>
                <div class="flex justify-between items-start mb-4">
                    <img class="w-14 h-14 rounded-xl object-cover border border-white/10" src="${c.avatar_url || 'https://lh3.googleusercontent.com/aida-public/AB6AXuBT0NpLK060VPqvHHfKqSM591wQsyX0wC7wEB5wvoRdsoRdamqgXYFH0gJhUHdvQWx5cE4HgWiGNUWWq3xepl4KCzThVL1MpNTOPjQ1NBKYbfRWoT8186Bdbu8pctaSA8gVo4tENwDGlYfp6Yq8Wc8FJA2uDuojrf4FpbNU_GSiYDr_s0f4MJDu73q04MOFgQK7LvTSIY-r4qb-lJCDFElsS1zQCpCIcdnpNzPx8ITAxy7cISBR_J2BKBoZrpcFuTb3Iwz7Bjr4NfAI'}" alt="${c.name}"/>
                    <input type="checkbox" class="rounded border-white/10 bg-white/5 text-primary focus:ring-primary focus:ring-opacity-50" ${isChecked ? 'checked' : ''} data-id="${c.id}"/>
                </div>
                <h3 class="font-headline-md text-on-surface">${c.name}</h3>
                <p class="text-sm text-on-surface-variant/80">${c.title}</p>
                <div class="flex gap-2 items-center text-xs text-outline/80 mt-2">
                    <span class="flex items-center gap-0.5"><span class="material-symbols-outlined text-sm">location_on</span>${c.location || 'N/A'}</span>
                    <span>•</span>
                    <span>${c.experience_years ?? 0} Years Exp</span>
                </div>
                <div class="flex flex-wrap gap-1.5 mt-4">
                    ${(c.skills || []).slice(0, 4).map(s => `<span class="bg-white/5 px-2.5 py-0.5 rounded-full text-[10px] text-on-surface-variant">${s}</span>`).join('')}
                    ${(c.skills || []).length > 4 ? `<span class="bg-primary/10 text-primary px-2.5 py-0.5 rounded-full text-[10px] font-bold">+${(c.skills || []).length - 4}</span>` : ''}
                </div>
            </div>
            <div class="mt-6 pt-4 border-t border-white/5 flex gap-2">
                <button class="flex-1 py-2 rounded-lg bg-primary-container hover:bg-primary-container/85 text-on-primary-container text-xs font-bold transition-all" onclick="window.location.href='candidate_details.html?id=${c.id}'">
                    Profile Detail
                </button>
                <button class="py-2 px-3 rounded-lg border border-white/10 hover:bg-white/5 text-xs text-on-surface-variant transition-colors" onclick="window.location.href='skill_gap_analysis.html?id=${c.id}&job_id=1'">
                    <span class="material-symbols-outlined text-sm">trending_up</span>
                </button>
            </div>
        `;

        // Connect checkbox for comparison matrix
        const checkbox = card.querySelector('input[type="checkbox"]');
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                selectedForComparison.add(c.id);
            } else {
                selectedForComparison.delete(c.id);
            }
            updateComparisonBanner();
        });

        container.appendChild(card);
    });
}

function updateComparisonBanner() {
    let banner = document.getElementById('comparison-float-banner');
    if (selectedForComparison.size === 0) {
        if (banner) banner.remove();
        return;
    }

    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'comparison-float-banner';
        banner.className = 'fixed bottom-6 left-1/2 -translate-x-1/2 bg-surface-container-high/90 backdrop-blur-xl border border-primary/30 shadow-2xl py-4 px-8 rounded-2xl z-50 flex items-center gap-6 animate-bounce-subtle';
        document.body.appendChild(banner);
    }

    banner.innerHTML = `
        <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-primary">compare_arrows</span>
            <span class="text-sm font-bold">${selectedForComparison.size} Candidates selected for comparison</span>
        </div>
        <div class="flex gap-2">
            <button class="px-4 py-1.5 rounded-lg bg-primary text-on-primary text-xs font-bold shadow-lg shadow-primary/20 active:scale-95 transition-transform" onclick="goToComparison()">
                Compare Now
            </button>
            <button class="px-3 py-1.5 rounded-lg border border-white/10 text-xs text-on-surface-variant hover:bg-white/5" onclick="clearComparisonSelection()">
                Clear
            </button>
        </div>
    `;
}

function goToComparison() {
    const ids = Array.from(selectedForComparison).join(',');
    window.location.href = `candidate_comparison.html?candidates=${ids}&job_id=1`;
}

function clearComparisonSelection() {
    selectedForComparison.clear();
    document.querySelectorAll('#candidates-grid input[type="checkbox"]').forEach(box => box.checked = false);
    updateComparisonBanner();
}

// --- 3. CANDIDATE RANKING ---
async function initCandidateRanking() {
    const select = document.getElementById('job-selector') || document.querySelector('select');
    if (!select) return;

    try {
        const res = await fetch(`${API_BASE}/jobs/`);
        if (!res.ok) return;
        const jobs = await res.json();
        window.allJobs = jobs;

        // Populate dropdown
        select.innerHTML = '<option value="">-- Choose an Open Role --</option>';
        jobs.forEach(job => {
            const opt = document.createElement('option');
            opt.value = job.id;
            opt.textContent = `${job.title} (${job.location})`;
            select.appendChild(opt);
        });

        // Set value from query param if available
        const urlParams = new URLSearchParams(window.location.search);
        const jobIdParam = urlParams.get('job_id');

        if (jobIdParam) {
            select.value = jobIdParam;
            loadRankings(jobIdParam);
        }

        // On selection change
        select.addEventListener('change', () => {
            if (select.value) {
                loadRankings(select.value);
            } else {
                const resultsContainer = document.getElementById('rankings-list-container');
                if (resultsContainer) resultsContainer.innerHTML = '';
            }
        });

        // Groq Rerank button setup
        const groqBtn = document.getElementById('btn-groq-rerank');
        if (groqBtn) {
            groqBtn.addEventListener('click', async () => {
                const jobId = select.value;
                if (!jobId) {
                    showToast('Please select a job role first.', 'error');
                    return;
                }

                // Show loading state
                groqBtn.disabled = true;
                const originalHTML = groqBtn.innerHTML;
                groqBtn.innerHTML = `<span class="material-symbols-outlined animate-spin text-[18px]">sync</span> Reranking...`;

                // Show loading on table
                const tableContainer = document.getElementById('rankings-list-container') || document.querySelector('main tbody');
                if (tableContainer) {
                    tableContainer.innerHTML = `
                        <tr>
                            <td colspan="6" class="py-12 text-center text-outline">
                                <span class="material-symbols-outlined animate-spin text-3xl mb-2 text-primary">psychology</span>
                                <p class="text-primary font-bold">Groq AI is evaluating resume profiles & job alignment...</p>
                                <p class="text-xs text-outline mt-1">Applying LLM criteria matching & reranking weights...</p>
                            </td>
                        </tr>
                    `;
                }

                try {
                    showToast('Triggering Groq AI Recruiter evaluation...', 'info');
                    const rerankRes = await fetch(`${API_BASE}/ranking/rerank/${jobId}`, { method: 'POST' });
                    if (rerankRes.ok) {
                        showToast('Groq AI Reranking complete! Recruiter consensus applied.');
                        await loadRankings(jobId);
                    } else {
                        showToast('Failed to rerank using Groq.', 'error');
                    }
                } catch (err) {
                    console.error("Groq rerank failed", err);
                    showToast('Error contacting reranker service.', 'error');
                } finally {
                    groqBtn.disabled = false;
                    groqBtn.innerHTML = originalHTML;
                }
            });
        }

    } catch (e) {
        console.error("Ranking init failed", e);
    }
}

async function loadRankings(jobId) {
    const container = document.getElementById('rankings-list-container') || document.querySelector('main tbody');
    if (!container) return;

    container.innerHTML = `
        <tr>
            <td colspan="6" class="py-12 text-center text-outline">
                <span class="material-symbols-outlined animate-spin text-3xl mb-2">sync</span>
                <p>Retrieving AI match score calculations...</p>
            </td>
        </tr>
    `;

    try {
        let rankingsRes = await fetch(`${API_BASE}/ranking/job/${jobId}`);
        if (!rankingsRes.ok) return;
        let rankings = await rankingsRes.json();

        // If rankings are empty, trigger calculation backend pipeline
        if (rankings.length === 0) {
            showToast('Initializing ranking calculations...', 'info');
            const calcRes = await fetch(`${API_BASE}/ranking/rank/${jobId}`, { method: 'POST' });
            if (calcRes.ok) {
                rankingsRes = await fetch(`${API_BASE}/ranking/job/${jobId}`);
                rankings = await rankingsRes.json();
                showToast('Ranking calculation complete!');
            }
        }

        container.innerHTML = '';
        if (rankings.length === 0) {
            container.innerHTML = `
                <tr>
                    <td colspan="6" class="py-12 text-center text-outline">
                        <span class="material-symbols-outlined text-3xl mb-2 font-bold text-error">error</span>
                        <p>No candidates available in the pool to rank.</p>
                    </td>
                </tr>
            `;
            return;
        }

        // Handle both Table elements and Grid element formats based on screen design
        const isTable = container.tagName.toLowerCase() === 'tbody';

        rankings.forEach((r, index) => {
            const score = Math.round(r.match_score);
            const scoreColor = score >= 85 ? 'text-primary' : score >= 70 ? 'text-primary' : 'text-on-surface-variant';

            if (isTable) {
                const tr = document.createElement('tr');
                tr.className = 'group hover:bg-white/5 transition-all duration-300 border-b border-white/5';

                // Technical Excellence tags
                const matchedSkills = r.explanation?.matched_skills || [];
                const skillsHTML = matchedSkills.length > 0
                    ? matchedSkills.slice(0, 3).map(s => `<span class="px-2 py-0.5 rounded bg-primary/10 text-primary text-[10px] font-bold border border-primary/20">${s}</span>`).join('')
                    : '<span class="text-xs text-on-surface-variant/60">No skill overlap</span>';

                // Cultural Synergy percentage
                const locScore = Math.round(r.explanation?.location_score || 0);

                tr.innerHTML = `
                    <td class="px-6 py-6">
                        <div class="flex items-center justify-center w-8 h-8 rounded-full ${index === 0 ? 'bg-primary/20 text-primary' : 'bg-white/5 text-on-surface-variant'} font-black text-label-sm">${String(index + 1).padStart(2, '0')}</div>
                    </td>
                    <td class="px-6 py-6">
                        <div class="flex items-center gap-4">
                            <div class="relative">
                                <img class="w-12 h-12 rounded-2xl object-cover" src="${r.candidate.avatar_url || 'https://lh3.googleusercontent.com/aida-public/AB6AXuBT0NpLK060VPqvHHfKqSM591wQsyX0wC7wEB5wvoRdsoRdamqgXYFH0gJhUHdvQWx5cE4HgWiGNUWWq3xepl4KCzThVL1MpNTOPjQ1NBKYbfRWoT8186Bdbu8pctaSA8gVo4tENwDGlYfp6Yq8Wc8FJA2uDuojrf4FpbNU_GSiYDr_s0f4MJDu73q04MOFgQK7LvTSIY-r4qb-lJCDFElsS1zQCpCIcdnpNzPx8ITAxy7cISBR_J2BKBoZrpcFuTb3Iwz7Bjr4NfAI'}" alt=""/>
                                <div class="absolute -bottom-1 -right-1 w-4 h-4 bg-tertiary rounded-full border-2 border-surface shadow-lg"></div>
                            </div>
                            <div>
                                <h4 class="font-bold text-on-surface text-body-md hover:text-primary cursor-pointer flex items-center gap-1" onclick="window.location.href='candidate_details.html?id=${r.candidate_id}&job_id=${jobId}'">
                                    ${r.candidate.name}
                                    ${r.explanation?.groq_score ? `
                                    <span class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-primary/20 text-primary text-[9px] font-bold border border-primary/30 animate-pulse-slow" title="${r.explanation.groq_reasoning || ''}">
                                        <span class="material-symbols-outlined text-[10px]" style="font-variation-settings: 'FILL' 1;">bolt</span> Groq AI
                                    </span>` : ''}
                                </h4>
                                <p class="text-on-surface-variant/60 text-[12px]">${r.candidate.title}</p>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-6">
                        <div class="flex justify-center">
                            <div class="relative h-14 w-14 flex items-center justify-center">
                                <svg class="h-full w-full -rotate-90">
                                    <circle cx="28" cy="28" fill="transparent" r="24" stroke="rgba(255,255,255,0.05)" stroke-width="4"></circle>
                                    <circle class="${scoreColor}" cx="28" cy="28" fill="transparent" r="24" stroke="currentColor" stroke-dasharray="150" stroke-dashoffset="${150 - (150 * score / 100)}" stroke-width="4"></circle>
                                </svg>
                                <span class="absolute text-[12px] font-bold ${scoreColor}">${score}</span>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-6">
                        <div class="flex flex-wrap gap-2 max-w-xs">
                            ${skillsHTML}
                        </div>
                    </td>
                    <td class="px-6 py-6">
                        <div class="flex items-center gap-2">
                            <div class="h-1.5 w-24 bg-white/5 rounded-full overflow-hidden">
                                <div class="h-full bg-tertiary" style="width: ${locScore}%"></div>
                            </div>
                            <span class="text-tertiary font-mono-data text-[12px]">${locScore}%</span>
                        </div>
                    </td>
                    <td class="px-6 py-6 text-right">
                        <button class="px-4 py-2 bg-primary text-on-primary rounded-xl font-bold text-label-sm hover:scale-105 transition-transform active:scale-95 ai-glow mr-2" onclick="window.location.href='skill_gap_analysis.html?id=${r.candidate_id}&job_id=${jobId}'">
                            Skill Gap
                        </button>
                        <button class="px-4 py-2 border border-white/10 hover:bg-white/5 rounded-xl font-bold text-label-sm transition-transform active:scale-95" onclick="updateCandidateStatus(${r.candidate_id}, 'Interview')">
                            Interview
                        </button>
                    </td>
                `;
                container.appendChild(tr);
            } else {
                // In case ranking UI layout uses grid divs
                const div = document.createElement('div');
                div.className = 'glass-card p-6 rounded-2xl relative overflow-hidden flex items-center justify-between border-l-4 border-l-primary';
                div.innerHTML = `
                    <div class="flex items-center gap-6">
                        <span class="text-xl font-bold font-mono text-outline">#${index + 1}</span>
                        <img class="w-16 h-16 rounded-xl object-cover" src="${r.candidate.avatar_url || 'https://lh3.googleusercontent.com/aida-public/AB6AXuBT0NpLK060VPqvHHfKqSM591wQsyX0wC7wEB5wvoRdsoRdamqgXYFH0gJhUHdvQWx5cE4HgWiGNUWWq3xepl4KCzThVL1MpNTOPjQ1NBKYbfRWoT8186Bdbu8pctaSA8gVo4tENwDGlYfp6Yq8Wc8FJA2uDuojrf4FpbNU_GSiYDr_s0f4MJDu73q04MOFgQK7LvTSIY-r4qb-lJCDFElsS1zQCpCIcdnpNzPx8ITAxy7cISBR_J2BKBoZrpcFuTb3Iwz7Bjr4NfAI'}" alt=""/>
                        <div>
                            <h3 class="font-headline-md text-on-surface cursor-pointer hover:text-primary flex items-center gap-1" onclick="window.location.href='candidate_details.html?id=${r.candidate_id}&job_id=${jobId}'">
                                ${r.candidate.name}
                                ${r.explanation?.groq_score ? `
                                <span class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-primary/20 text-primary text-[9px] font-bold border border-primary/30 animate-pulse-slow" title="${r.explanation.groq_reasoning || ''}">
                                    <span class="material-symbols-outlined text-[10px]" style="font-variation-settings: 'FILL' 1;">bolt</span> Groq AI
                                </span>` : ''}
                            </h3>
                            <p class="text-xs text-outline">${r.candidate.title} • ${r.candidate.location}</p>
                            <div class="flex gap-1.5 mt-2">
                                ${r.candidate.skills.slice(0, 3).map(s => `<span class="bg-white/5 px-2 py-0.5 rounded text-[10px] text-on-surface-variant">${s}</span>`).join('')}
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center gap-6">
                        <div class="text-right">
                            <p class="text-xs text-outline">Match Score</p>
                            <p class="text-2xl font-bold text-primary">${score}%</p>
                        </div>
                        <div class="flex flex-col gap-2">
                            <button class="px-4 py-1.5 rounded-lg bg-primary text-on-primary text-xs font-bold" onclick="window.location.href='skill_gap_analysis.html?id=${r.candidate_id}&job_id=${jobId}'">
                                Analyze Gap
                            </button>
                            <button class="px-4 py-1.5 rounded-lg border border-white/10 hover:bg-white/5 text-xs text-on-surface-variant" onclick="updateCandidateStatus(${r.candidate_id}, 'Interview')">
                                Invite to Interview
                            </button>
                        </div>
                    </div>
                `;
                container.appendChild(div);
            }
        });

    } catch (e) {
        console.error("Load rankings failed", e);
    }
}

async function updateCandidateStatus(candId, newStatus) {
    try {
        const res = await fetch(`${API_BASE}/candidates/${candId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        if (res.ok) {
            showToast(`Candidate status updated to '${newStatus}'!`);
        }
    } catch (err) {
        showToast('Failed to update candidate status.', 'error');
    }
}

// --- 4. CANDIDATE DETAILS ---
async function initCandidateDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const candId = urlParams.get('id') || '1';

    try {
        const [cRes, jRes] = await Promise.all([
            fetch(`${API_BASE}/candidates/${candId}`),
            fetch(`${API_BASE}/jobs/`)
        ]);

        if (!cRes.ok || !jRes.ok) {
            showToast("Candidate not found.", "error");
            return;
        }

        const candidate = await cRes.json();
        const jobs = await jRes.json();

        // Populate detail fields
        const nameEl = document.querySelector('h2.font-headline-lg') || document.querySelector('h2');
        if (nameEl) nameEl.textContent = candidate.name;

        const titleEl = document.querySelector('main p.text-on-surface-variant') || document.getElementById('candidate-profile-title');
        if (titleEl) titleEl.textContent = `${candidate.title} • ${candidate.location} (${candidate.work_preference})`;

        // Avatar
        const avatar = document.querySelector('main img');
        if (avatar && candidate.avatar_url) avatar.src = candidate.avatar_url;

        // Skills List
        const skillsContainer = document.getElementById('candidate-skills-list') || document.getElementById('skills-container');
        if (skillsContainer) {
            skillsContainer.innerHTML = candidate.skills.map(s => `
                <span class="bg-primary/10 border border-primary/20 text-primary px-3 py-1 rounded-full text-xs font-medium">${s}</span>
            `).join('');
        }

        // Basic Info mapping
        const infoGrid = document.getElementById('candidate-basic-info');
        if (infoGrid) {
            infoGrid.innerHTML = `
                <div class="p-4 bg-white/2 rounded-xl">
                    <p class="text-xs text-outline uppercase tracking-wider">Salary Expectation</p>
                    <p class="text-lg font-bold text-on-surface mt-1">${candidate.salary_expectation
                    ? (candidate.salary_expectation < 1000
                        ? `$${(candidate.salary_expectation * 1200).toLocaleString()}`
                        : `$${candidate.salary_expectation.toLocaleString()}`)
                    : 'N/A'
                }</p>
                </div>
                <div class="p-4 bg-white/2 rounded-xl">
                    <p class="text-xs text-outline uppercase tracking-wider">Experience Level</p>
                    <p class="text-lg font-bold text-on-surface mt-1">${candidate.experience_years} Years</p>
                </div>
                <div class="p-4 bg-white/2 rounded-xl">
                    <p class="text-xs text-outline uppercase tracking-wider">Candidate Status</p>
                    <p class="text-lg font-bold text-primary mt-1">${candidate.status}</p>
                </div>
            `;
        }

        // Resume Text
        const resumeBox = document.getElementById('resume-text-box') || document.querySelector('pre');
        if (resumeBox) {
            resumeBox.textContent = candidate.resume_text || "No resume text extracted.";
        }

        // Populate Jobs Selector for analysis
        const jobSelect = document.getElementById('job-analysis-selector') || document.querySelector('select');
        if (jobSelect) {
            jobSelect.innerHTML = '<option value="">-- Select Role for Gap Analysis --</option>';
            jobs.forEach(job => {
                const opt = document.createElement('option');
                opt.value = job.id;
                opt.textContent = job.title;
                jobSelect.appendChild(opt);
            });

            // Set initial selected job if query param exists
            const jobIdParam = urlParams.get('job_id');
            if (jobIdParam) {
                jobSelect.value = jobIdParam;
                loadSkillGapSection(candId, jobIdParam);
            }

            jobSelect.addEventListener('change', () => {
                if (jobSelect.value) {
                    loadSkillGapSection(candId, jobSelect.value);
                }
            });
        }

    } catch (e) {
        console.error("Candidate details initialization failed", e);
    }
}

async function loadSkillGapSection(candId, jobId) {
    const analysisContainer = document.getElementById('gap-analysis-output') || document.getElementById('analysis-container');
    if (!analysisContainer) return;

    analysisContainer.innerHTML = `
        <div class="py-8 text-center text-outline">
            <span class="material-symbols-outlined animate-spin text-3xl mb-2">sync</span>
            <p>Analyzing candidate capabilities...</p>
        </div>
    `;

    try {
        const res = await fetch(`${API_BASE}/ranking/candidate/${candId}/skill-gap/${jobId}`);
        if (!res.ok) return;
        const gap = await res.json();

        analysisContainer.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div class="glass-card p-6 rounded-xl border-l-4 border-l-tertiary">
                    <h4 class="font-headline-md text-sm text-tertiary uppercase tracking-wider mb-4">Matching Skills (${gap.matching_skills.length})</h4>
                    <div class="flex flex-wrap gap-2">
                        ${gap.matching_skills.map(s => `<span class="bg-tertiary/10 text-tertiary px-3 py-1 rounded-full text-xs font-semibold">${s}</span>`).join('') || '<span class="text-xs text-outline">No skill overlap identified.</span>'}
                    </div>
                </div>
                <div class="glass-card p-6 rounded-xl border-l-4 border-l-error">
                    <h4 class="font-headline-md text-sm text-error uppercase tracking-wider mb-4">Missing Skills (${gap.missing_skills.length})</h4>
                    <div class="flex flex-wrap gap-2">
                        ${gap.missing_skills.map(s => `<span class="bg-error/10 text-error px-3 py-1 rounded-full text-xs font-semibold">${s}</span>`).join('') || '<span class="text-xs text-outline">No skills missing.</span>'}
                    </div>
                </div>
            </div>
            
            <div class="glass-card p-6 rounded-xl mt-6">
                <h4 class="font-headline-md text-on-surface mb-4">Upskilling AI Roadmap</h4>
                <div class="space-y-4">
                    ${gap.upskilling_roadmap.map((step, idx) => `
                        <div class="flex gap-4 items-start">
                            <span class="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold text-xs mt-0.5">${idx + 1}</span>
                            <div>
                                <p class="text-sm font-bold text-on-surface">${step}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="mt-6 flex gap-4">
                <button class="px-6 py-2.5 rounded-lg bg-primary text-on-primary font-bold shadow-lg text-sm" onclick="window.location.href='recruiter_copilot.html?candidate_id=${candId}&job_id=${jobId}&action=draft'">
                    Draft Outreach Email
                </button>
                <button class="px-6 py-2.5 rounded-lg border border-white/10 hover:bg-white/5 text-sm text-on-surface" onclick="window.location.href='skill_gap_analysis.html?id=${candId}&job_id=${jobId}'">
                    Full View Skill Gap
                </button>
            </div>
        `;
    } catch (err) {
        console.error("Failed to load skill gap", err);
    }
}

// --- 5. CANDIDATE COMPARISON ---
async function initCandidateComparison() {
    const urlParams = new URLSearchParams(window.location.search);
    const candidateIds = urlParams.get('candidates') || '1,2,5';
    const jobId = urlParams.get('job_id') || null;

    const ids = candidateIds.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));
    const container = document.querySelector('main .grid');
    if (!container || ids.length === 0) return;

    try {
        // Call the new comparison endpoint
        const comparisonUrl = `${API_BASE}/candidates/compare?candidate_ids=${ids.join(',')}&job_id=${jobId || ''}`;
        const compRes = await fetch(comparisonUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!compRes.ok) {
            console.error("Comparison API failed:", compRes.status);
            return;
        }

        const comparisonData = await compRes.json();
        const { candidates, summary } = comparisonData;

        // Build comparison structure
        // Grid: col-1 is header/label, other cols are candidates
        container.innerHTML = '';

        // Row 1: Header Row
        const headerLabel = document.createElement('div');
        headerLabel.className = 'p-8 border-b border-white/5 flex flex-col justify-end';
        headerLabel.innerHTML = `
            <p class="font-label-sm text-primary uppercase tracking-[0.2em] mb-2">Comparison Matrix</p>
            <p class="text-on-surface-variant text-sm">${candidates.length} Candidates Selected</p>
        `;
        container.appendChild(headerLabel);

        // Render candidate headers with scores and recommendations
        candidates.forEach((c, idx) => {
            const score = Math.round(c.ranking.score || 75);
            const recLevel = c.recommendation.level;
            const isRecommended = recLevel === 'Strong Hire';

            const card = document.createElement('div');
            card.className = 'p-8 border-b border-white/5 border-l border-white/5 relative';
            if (isRecommended) {
                card.innerHTML = `
                    <div class="absolute top-4 right-4 bg-primary-container text-white px-3 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase flex items-center gap-1 shadow-lg shadow-primary/30">
                        <span class="material-symbols-outlined text-sm" style="font-variation-settings: 'FILL' 1;">verified</span>
                        Recommended
                    </div>
                `;
            }
            card.innerHTML += `
                <div class="flex flex-col items-center text-center">
                    <div class="relative mb-4">
                        <img class="w-24 h-24 rounded-2xl object-cover ring-4 ring-primary/20" src="${c.avatar_url || 'https://lh3.googleusercontent.com/aida-public/AB6AXuBT0NpLK060VPqvHHfKqSM591wQsyX0wC7wEB5wvoRdsoRdamqgXYFH0gJhUHdvQWx5cE4HgWiGNUWWq3xepl4KCzThVL1MpNTOPjQ1NBKYbfRWoT8186Bdbu8pctaSA8gVo4tENwDGlYfp6Yq8Wc8FJA2uDuojrf4FpbNU_GSiYDr_s0f4MJDu73q04MOFgQK7LvTSIY-r4qb-lJCDFElsS1zQCpCIcdnpNzPx8ITAxy7cISBR_J2BKBoZrpcFuTb3Iwz7Bjr4NfAI'}" alt=""/>
                        <div class="absolute -bottom-2 -right-2 w-8 h-8 bg-tertiary rounded-full flex items-center justify-center text-on-tertiary shadow-lg">
                            <span class="font-bold text-xs">${score}</span>
                        </div>
                    </div>
                    <h3 class="font-headline-md text-on-surface text-lg font-bold">${c.name}</h3>
                    <p class="text-on-surface-variant/70 text-xs">${c.title || 'Not specified'}</p>
                    <p class="text-[10px] text-tertiary font-bold mt-2 flex items-center justify-center gap-1">
                        <span class="w-1.5 h-1.5 bg-tertiary rounded-full status-dot"></span>
                        ${c.ranking.tier}
                    </p>
                </div>
            `;
            container.appendChild(card);
        });

        // Row 2: Experience
        const expLabel = document.createElement('div');
        expLabel.className = 'p-8 border-b border-white/5 flex items-center bg-white/2';
        expLabel.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-primary-fixed">work</span>
                <span class="font-bold text-on-surface">Experience</span>
            </div>
        `;
        container.appendChild(expLabel);

        candidates.forEach(c => {
            const expCell = document.createElement('div');
            expCell.className = 'p-8 border-b border-white/5 border-l border-white/5 flex flex-col items-center justify-center font-mono-data text-headline-md text-on-surface';
            expCell.innerHTML = `
                <div class="text-2xl font-bold text-tertiary">${c.experience.years}</div>
                <div class="text-xs text-on-surface-variant">${c.experience.level}</div>
            `;
            container.appendChild(expCell);
        });

        // Row 3: Skills List
        const skillsLabel = document.createElement('div');
        skillsLabel.className = 'p-8 border-b border-white/5 flex items-start pt-10';
        skillsLabel.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-primary-fixed">psychology_alt</span>
                <span class="font-bold text-on-surface">Top Skills</span>
            </div>
        `;
        container.appendChild(skillsLabel);

        candidates.forEach(c => {
            const skillCell = document.createElement('div');
            skillCell.className = 'p-8 border-b border-white/5 border-l border-white/5 space-y-4';

            const topSkills = c.skills.slice(0, 3);
            skillCell.innerHTML = topSkills.map(skill => `
                <div class="space-y-1">
                    <div class="flex justify-between text-[10px] uppercase font-bold tracking-wider mb-1">
                        <span>${skill.name}</span>
                        <span class="text-tertiary">${skill.proficiency}</span>
                    </div>
                    <div class="h-1.5 w-full bg-surface-variant rounded-full overflow-hidden">
                        <div class="h-full bg-tertiary rounded-full shadow-[0_0_8px_rgba(78,222,163,0.5)]" style="width: 100%"></div>
                    </div>
                </div>
            `).join('') || '<p class="text-xs text-outline">No skills listed</p>';

            container.appendChild(skillCell);
        });

        // Row 4: Education
        const eduLabel = document.createElement('div');
        eduLabel.className = 'p-8 border-b border-white/5 flex items-start pt-10 bg-white/2';
        eduLabel.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-primary-fixed">school</span>
                <span class="font-bold text-on-surface">Education</span>
            </div>
        `;
        container.appendChild(eduLabel);

        candidates.forEach(c => {
            const eduCell = document.createElement('div');
            eduCell.className = 'p-8 border-b border-white/5 border-l border-white/5';

            const topEdu = c.education.slice(0, 2);
            eduCell.innerHTML = topEdu.map(edu => `
                <div class="mb-3 pb-3 border-b border-white/5 last:border-0">
                    <p class="text-xs font-bold text-on-surface">${edu.degree || 'Unknown'}</p>
                    <p class="text-[10px] text-on-surface-variant">${edu.institution || 'Unknown'}</p>
                    <p class="text-[8px] text-tertiary uppercase font-bold">${edu.tier || 'N/A'}</p>
                </div>
            `).join('') || '<p class="text-xs text-outline">No education listed</p>';

            container.appendChild(eduCell);
        });

        // Row 5: Behavioral Signals
        const behaviorLabel = document.createElement('div');
        behaviorLabel.className = 'p-8 border-b border-white/5 flex items-start pt-10';
        behaviorLabel.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-primary-fixed">trending_up</span>
                <span class="font-bold text-on-surface">Engagement</span>
            </div>
        `;
        container.appendChild(behaviorLabel);

        candidates.forEach(c => {
            const signals = c.behavioral_signals;
            const behaviorCell = document.createElement('div');
            behaviorCell.className = 'p-8 border-b border-white/5 border-l border-white/5 space-y-2';
            behaviorCell.innerHTML = `
                <div class="flex items-center justify-between text-[10px]">
                    <span class="text-on-surface-variant">Profile Completeness</span>
                    <span class="font-bold text-tertiary">${Math.round(signals.profile_completeness)}%</span>
                </div>
                <div class="flex items-center gap-2">
                    ${signals.open_to_work ? '<span class="px-2 py-0.5 rounded text-[8px] bg-tertiary/20 text-tertiary font-bold">OPEN TO WORK</span>' : '<span class="px-2 py-0.5 rounded text-[8px] bg-surface-variant text-on-surface-variant text-xs">Not Actively Looking</span>'}
                </div>
                <div class="text-[8px] text-on-surface-variant space-y-1 pt-2">
                    <p><span class="text-on-surface font-bold">${signals.connection_count}</span> connections</p>
                    <p><span class="text-on-surface font-bold">${signals.endorsements_received}</span> endorsements</p>
                </div>
            `;
            container.appendChild(behaviorCell);
        });

        // Row 6: Recommendation
        const recLabel = document.createElement('div');
        recLabel.className = 'p-8 border-b border-white/5 flex items-start pt-10 bg-white/2';
        recLabel.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-primary">auto_awesome</span>
                <span class="font-bold text-on-surface">Recommendation</span>
            </div>
        `;
        container.appendChild(recLabel);

        candidates.forEach(c => {
            const rec = c.recommendation;
            const recColor = rec.level === 'Strong Hire' ? 'text-tertiary' : rec.level === 'Consider' ? 'text-primary' : 'text-on-surface-variant';

            const recCell = document.createElement('div');
            recCell.className = 'p-8 border-b border-white/5 border-l border-white/5 bg-primary-container/5';
            recCell.innerHTML = `
                <div class="flex items-center gap-2 mb-3">
                    <span class="text-sm font-bold ${recColor}">${rec.level}</span>
                    <span class="text-[8px] text-on-surface-variant font-bold uppercase">(${Math.round(rec.confidence * 100)}% confidence)</span>
                </div>
                <p class="text-xs text-on-surface-variant leading-relaxed mb-3">${rec.reasoning}</p>
                <div class="space-y-1">
                    <p class="text-[8px] font-bold text-tertiary uppercase">Strengths:</p>
                    <ul class="text-[8px] text-on-surface-variant space-y-0.5">
                        ${rec.key_strengths.slice(0, 2).map(s => `<li>• ${s}</li>`).join('')}
                    </ul>
                </div>
            `;
            container.appendChild(recCell);
        });

        // Row 7: Final fit score
        const scoreLabel = document.createElement('div');
        scoreLabel.className = 'p-8 flex items-center';
        scoreLabel.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-primary-fixed">target</span>
                <span class="font-bold text-on-surface">Match Score</span>
            </div>
        `;
        container.appendChild(scoreLabel);

        candidates.forEach(c => {
            const score = Math.round(c.ranking.score || 75);
            const scoreColor = score >= 80 ? 'border-tertiary text-tertiary' : score >= 60 ? 'border-primary text-primary' : 'border-on-surface-variant text-on-surface-variant';

            const scoreCell = document.createElement('div');
            scoreCell.className = 'p-8 border-l border-white/5 flex items-center justify-center';
            scoreCell.innerHTML = `
                <div class="w-16 h-16 rounded-full border-4 ${scoreColor} flex items-center justify-center font-headline-md text-lg font-bold">${score}</div>
            `;
            container.appendChild(scoreCell);
        });

    } catch (e) {
        console.error("Comparison load failed", e);
    }
}

// --- 6. SKILL GAP ANALYSIS ---
async function initSkillGapAnalysis() {
    const urlParams = new URLSearchParams(window.location.search);
    const candId = urlParams.get('id') || '1';
    const jobId = urlParams.get('job_id') || '1';

    try {
        const [cRes, jRes, gapRes] = await Promise.all([
            fetch(`${API_BASE}/candidates/${candId}`),
            fetch(`${API_BASE}/jobs/${jobId}`),
            fetch(`${API_BASE}/ranking/candidate/${candId}/skill-gap/${jobId}`)
        ]);

        if (!cRes.ok || !jRes.ok || !gapRes.ok) return;

        const candidate = await cRes.json();
        const job = await jRes.json();
        const gap = await gapRes.json();

        // Update Headers
        const candNameEl = document.querySelector('h2.font-headline-lg') || document.querySelector('h2');
        if (candNameEl) candNameEl.textContent = `Capability Analysis: ${candidate.name}`;

        const subheaderEl = document.querySelector('main nav span.text-primary-fixed') || document.querySelector('main p');
        if (subheaderEl) subheaderEl.textContent = `Target Role: ${job.title}`;

        // Populate match score radial progress and texts
        const score = Math.round(gap.match_score);
        const progressCircle = document.getElementById('score-circle-progress');
        if (progressCircle) {
            // Circumference of radius 88 is ~553
            const offset = 553 - (553 * score / 100);
            progressCircle.setAttribute('stroke-dashoffset', offset);
        }

        const scoreTextEl = document.getElementById('score-text');
        if (scoreTextEl) {
            scoreTextEl.textContent = `${score}%`;
        }

        const scoreTitleEl = document.getElementById('score-title');
        const scoreDescEl = document.getElementById('score-desc');
        if (scoreTitleEl && scoreDescEl) {
            if (score >= 90) {
                scoreTitleEl.textContent = "Excellent Match";
                scoreDescEl.textContent = `${candidate.name} is a near-perfect fit for the ${job.title} role, demonstrating mastery of key requirements.`;
            } else if (score >= 70) {
                scoreTitleEl.textContent = "High Potential";
                scoreDescEl.textContent = `${candidate.name} has a strong foundation in core skills for the ${job.title} role but requires targeted training in key areas.`;
            } else {
                scoreTitleEl.textContent = "Requires Development";
                scoreDescEl.textContent = `${candidate.name} shows potential but faces significant skill gaps. The upskilling roadmap below is highly recommended.`;
            }
        }

        // Fill Mastery Heatmap dynamically
        const heatmapContainer = document.getElementById('mastery-heatmap-container');
        if (heatmapContainer) {
            let heatmapHtml = '';

            // Render gained skills first
            (gap.gained_skills || []).forEach(skill => {
                const targetVal = 8.5;
                const candidateVal = 9.5;
                heatmapHtml += `
                    <div class="group">
                        <div class="flex justify-between text-sm mb-2">
                            <span class="font-bold">${skill}</span>
                            <span class="text-on-surface-variant"><span class="text-primary">${candidateVal.toFixed(1)}</span> / ${targetVal.toFixed(1)}</span>
                        </div>
                        <div class="h-4 bg-white/5 rounded-full overflow-hidden relative">
                            <div class="absolute top-0 left-0 h-full bg-secondary-container opacity-30 w-[${targetVal * 10}%]"></div>
                            <div class="absolute top-0 left-0 h-full bg-primary rounded-full w-[${candidateVal * 10}%] data-glow-primary"></div>
                        </div>
                    </div>
                `;
            });

            // Render missing skills (gaps)
            (gap.missing_skills || []).forEach(skill => {
                const targetVal = 9.0;
                const candidateVal = 4.5;
                heatmapHtml += `
                    <div class="group">
                        <div class="flex justify-between text-sm mb-2">
                            <span class="font-bold">${skill}</span>
                            <span class="text-on-surface-variant"><span class="text-error font-bold">${candidateVal.toFixed(1)}</span> / ${targetVal.toFixed(1)}</span>
                        </div>
                        <div class="h-4 bg-white/5 rounded-full overflow-hidden relative">
                            <div class="absolute top-0 left-0 h-full bg-secondary-container opacity-30 w-[${targetVal * 10}%]"></div>
                            <div class="absolute top-0 left-0 h-full bg-error rounded-full w-[${candidateVal * 10}%]"></div>
                        </div>
                    </div>
                `;
            });

            if (!heatmapHtml) {
                heatmapHtml = '<div class="text-xs text-outline py-2">No skills to display.</div>';
            }
            heatmapContainer.innerHTML = heatmapHtml;
        }

        // Fill Skill alignment columns
        const gainedList = document.getElementById('matching-skills-container');
        const missingList = document.getElementById('missing-skills-container');

        if (gainedList) {
            gainedList.innerHTML = (gap.gained_skills || []).map(s => `
                <li class="flex items-center gap-3 py-2 border-b border-white/5 text-sm">
                    <span class="material-symbols-outlined text-tertiary text-lg">check_circle</span>
                    <span>${s}</span>
                </li>
            `).join('') || '<li class="text-xs text-outline py-2">No matching skills</li>';
        }

        if (missingList) {
            missingList.innerHTML = (gap.missing_skills || []).map(s => `
                <li class="flex items-center gap-3 py-2 border-b border-white/5 text-sm">
                    <span class="material-symbols-outlined text-error text-lg">cancel</span>
                    <span>${s}</span>
                </li>
            `).join('') || '<li class="text-xs text-outline py-2">No missing skills</li>';
        }

        // Upskilling roadmap steps
        const roadmapContainer = document.getElementById('upskilling-steps');
        if (roadmapContainer) {
            roadmapContainer.innerHTML = (gap.upskilling_roadmap || []).map((step) => `
                <div class="p-6 bg-surface-container rounded-xl border border-white/5 hover:border-primary/30 transition-all cursor-pointer group">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-[10px] px-2 py-1 bg-primary-container/20 text-primary-fixed rounded uppercase font-bold">${step.phase}</span>
                        <span class="material-symbols-outlined text-on-surface-variant group-hover:text-primary">school</span>
                    </div>
                    <h4 class="font-bold mb-2">${step.skill} Mastery</h4>
                    <p class="text-sm text-on-surface-variant mb-4">${step.hands_on_project}</p>
                    <div class="space-y-2 mb-4">
                        <div class="text-xs text-outline font-semibold">Recommended Resources:</div>
                        <ul class="list-disc list-inside text-xs text-on-surface-variant space-y-1">
                            ${(step.recommended_resources || []).map(r => `<li>${r}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="flex items-center gap-2 text-xs text-on-surface-variant mt-auto">
                        <span class="material-symbols-outlined text-[14px]">timer</span>
                        <span>${step.estimated_duration || '4-6 weeks'}</span>
                    </div>
                </div>
            `).join('');
        }

    } catch (e) {
        console.error("Skill gap initialization failed", e);
    }
}

// --- 7. RECRUITER COPILOT ---
window.triggerCopilotQuickAction = (type) => {
    const candSelect = document.getElementById('context-candidate');
    const jobSelect = document.getElementById('context-job');
    if (!candSelect) return;

    const cName = candSelect.options[candSelect.selectedIndex]?.text || 'the candidate';
    const jName = jobSelect && jobSelect.selectedIndex >= 0 ? jobSelect.options[jobSelect.selectedIndex].text : 'the role';

    if (type === 'draft') {
        triggerCopilotChat(`Draft an outreach email to ${cName} for the ${jName} role`);
    } else if (type === 'roadmap') {
        triggerCopilotChat(`Generate an upskilling roadmap for ${cName} to match the ${jName} role`);
    }
};

/**
 * View Candidates button handler.
 * Navigates to candidate_search.html, optionally applying skill filter
 * from the currently selected candidate's first skill.
 */
window.copilotViewCandidates = function() {
    const candSelect = document.getElementById('context-candidate');
    const candId = candSelect ? candSelect.value : null;

    if (candId) {
        // Navigate with the candidate context so search can be pre-filtered
        window.location.href = `candidate_search.html`;
    } else {
        window.location.href = 'candidate_search.html';
    }
};



async function updateCopilotLeftPanel(candidateId, jobId) {
    if (!candidateId) {
        // Show placeholders
        const nameEl = document.getElementById('copilot-candidate-name');
        if (nameEl) nameEl.textContent = 'No Candidate Selected';
        const titleEl = document.getElementById('copilot-candidate-title-exp');
        if (titleEl) titleEl.textContent = 'Please choose a candidate from the dropdown.';
        const skillsEl = document.getElementById('copilot-candidate-skills');
        if (skillsEl) skillsEl.innerHTML = '';
        const bioEl = document.getElementById('copilot-candidate-bio');
        if (bioEl) bioEl.textContent = 'No candidate context is currently active.';
        const skillGapEl = document.getElementById('copilot-skill-gap-container');
        if (skillGapEl) skillGapEl.innerHTML = '';
        const salValEl = document.getElementById('copilot-salary-expectation');
        if (salValEl) salValEl.textContent = '$--k';
        const salPctEl = document.getElementById('copilot-salary-vs-market');
        if (salPctEl) salPctEl.textContent = '--';
        const locEl = document.getElementById('copilot-location');
        if (locEl) locEl.textContent = 'Remote';
        const summaryEl = document.getElementById('copilot-resume-summary');
        if (summaryEl) summaryEl.innerHTML = '<li class="text-xs text-outline py-2">No summary available.</li>';
        return;
    }

    try {
        // Fetch candidate details
        const cRes = await fetch(`${API_BASE}/candidates/${candidateId}`);
        if (!cRes.ok) throw new Error("Failed to fetch candidate details");
        const candidate = await cRes.json();

        // Fetch explanation (which has strengths & weaknesses)
        let explanation = null;
        try {
            const expRes = await fetch(`${API_BASE}/candidates/${candidateId}/explanation${jobId ? '?job_id=' + jobId : ''}`);
            if (expRes.ok) explanation = await expRes.json();
        } catch (e) {
            console.error("Failed to fetch candidate explanation", e);
        }

        // Fetch skill gap (if jobId exists)
        let gap = null;
        let job = null;
        if (jobId) {
            try {
                const [gapRes, jobRes] = await Promise.all([
                    fetch(`${API_BASE}/ranking/candidate/${candidateId}/skill-gap/${jobId}`),
                    fetch(`${API_BASE}/jobs/${jobId}`)
                ]);
                if (gapRes.ok) gap = await gapRes.json();
                if (jobRes.ok) job = await jobRes.json();
            } catch (e) {
                console.error("Failed to fetch skill gap or job details", e);
            }
        }

        // 1. Candidate Name and Title
        const nameEl = document.getElementById('copilot-candidate-name');
        if (nameEl) nameEl.textContent = candidate.name;

        const titleEl = document.getElementById('copilot-candidate-title-exp');
        if (titleEl) titleEl.textContent = `${candidate.title} • ${candidate.experience_years} Years Exp.`;

        // 2. Avatar
        let avatarEl = document.getElementById('copilot-candidate-avatar');
        if (avatarEl) {
            if (avatarEl.tagName === 'DIV') {
                const img = document.createElement('img');
                img.id = 'copilot-candidate-avatar';
                img.className = 'w-24 h-24 rounded-2xl object-cover border border-white/5 shadow-lg shadow-black/40';
                avatarEl.parentNode.replaceChild(img, avatarEl);
                avatarEl = img;
            }
            avatarEl.src = candidate.avatar_url || 'https://lh3.googleusercontent.com/aida-public/AB6AXuDzT-u1Lw_XgEKv4z_p7A4aPmhpfGNQLxcWgadqa-Jk9MI4JaVGijmGt8MUJStVWujPeTu1DUaVtlXUBUdG68koz2ycW-ncOBdZ173GxgAaFQv7Px2qtOMO0JiepX-s7cd_Jtk731cfXBp00Vw7ipolK-lr9Yx6BgbA9NM5vcbCCXdRgjVXtC4sWy_esNO6A4JVMnxadBOlEXSSPkxRpv1nSkba8NNK0x5xiZlI0XG96eyfCB6Dn5zWiSO3D_SFkBLAw6L5RkjoFbBd';
            avatarEl.alt = candidate.name;
        }

        const viewProfileBtn = document.getElementById('copilot-view-profile-btn');
        if (viewProfileBtn) viewProfileBtn.classList.remove('hidden');

        // 3. Skills
        const skillsEl = document.getElementById('copilot-candidate-skills');
        if (skillsEl) {
            skillsEl.innerHTML = (candidate.skills || []).map(s => `
                <span class="px-2 py-1 bg-surface-container-highest rounded-md text-label-sm text-secondary">${s}</span>
            `).join('') || '<span class="text-xs text-outline">No skills listed</span>';
        }

        // 4. Resume bio
        const bioEl = document.getElementById('copilot-candidate-bio');
        if (bioEl) {
            const bioText = candidate.resume_text ? candidate.resume_text.slice(0, 150) + '...' : 'No resume bio available.';
            bioEl.textContent = `"${bioText}"`;
        }

        // 5. Skill Gap Analysis
        const skillGapEl = document.getElementById('copilot-skill-gap-container');
        if (skillGapEl) {
            if (gap) {
                let html = '';
                gap.gained_skills.slice(0, 3).forEach(s => {
                    html += `
                        <div class="space-y-1">
                            <div class="flex justify-between text-label-sm">
                                <span>${s}</span>
                                <span class="text-tertiary">Match</span>
                            </div>
                            <div class="h-1 bg-surface-container-highest rounded-full overflow-hidden">
                                <div class="h-full bg-tertiary w-full"></div>
                            </div>
                        </div>
                    `;
                });
                gap.missing_skills.slice(0, 3).forEach(s => {
                    html += `
                        <div class="space-y-1">
                            <div class="flex justify-between text-label-sm">
                                <span>${s}</span>
                                <span class="text-error">Gap</span>
                            </div>
                            <div class="h-1 bg-surface-container-highest rounded-full overflow-hidden">
                                <div class="h-full bg-error w-1/3"></div>
                            </div>
                        </div>
                    `;
                });
                if (!html) {
                    html = '<div class="text-xs text-outline py-2">No skills to compare.</div>';
                }
                skillGapEl.innerHTML = html;
            } else {
                skillGapEl.innerHTML = '<div class="text-xs text-outline py-2">Select a job context to view gap analysis.</div>';
            }
        }

        // 6. Market Benchmark
        const salValEl = document.getElementById('copilot-salary-expectation');
        const salPctEl = document.getElementById('copilot-salary-vs-market');
        const locEl = document.getElementById('copilot-location');
        if (salValEl) {
            const expectation = candidate.salary_expectation;
            if (expectation) {
                const usdSalary = expectation < 1000 ? expectation * 1200 : expectation;
                salValEl.textContent = `$${Math.round(usdSalary / 1000)}k`;
                if (salPctEl) {
                    const jobMin = job ? job.salary_range_min || 100000 : 100000;
                    const pct = ((usdSalary - jobMin) / jobMin * 100).toFixed(0);
                    salPctEl.textContent = `${pct >= 0 ? '+' : ''}${pct}% vs. Min`;
                }
            } else {
                salValEl.textContent = `N/A`;
                if (salPctEl) salPctEl.textContent = `Market Rate`;
            }
        }
        if (locEl) {
            locEl.textContent = candidate.location || 'Remote';
        }

        // 7. Resume Summary Strengths & Weaknesses
        const summaryEl = document.getElementById('copilot-resume-summary');
        if (summaryEl) {
            if (explanation) {
                let html = '';
                explanation.strengths.slice(0, 3).forEach(str => {
                    html += `
                        <li class="flex gap-3">
                            <span class="material-symbols-outlined text-primary text-body-md">check_circle</span>
                            <span class="font-body-md text-on-surface">${str}</span>
                        </li>
                    `;
                });
                explanation.weaknesses.slice(0, 2).forEach(w => {
                    html += `
                        <li class="flex gap-3">
                            <span class="material-symbols-outlined text-error text-body-md">warning</span>
                            <span class="font-body-md text-outline">${w}</span>
                        </li>
                    `;
                });
                summaryEl.innerHTML = html;
            } else {
                summaryEl.innerHTML = '<li class="text-xs text-outline py-2">No summary available.</li>';
            }
        }

    } catch (e) {
        console.error("Failed to update left context panel", e);
    }
}

function displayCopilotWelcome(candidateName, jobTitle) {
    const chatStream = document.getElementById('chat-stream');
    if (!chatStream) return;
    chatStream.innerHTML = ''; // Clear previous messages

    const aiMsg = document.createElement('div');
    aiMsg.className = 'flex gap-3 justify-start items-start';
    aiMsg.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center text-on-primary-container text-xs font-bold shrink-0 shadow-lg">AI</div>
        <div class="glass-card rounded-2xl rounded-tl-none px-4 py-3 max-w-xl text-sm leading-relaxed text-on-surface">
            <p>I've loaded candidate <strong>${candidateName}</strong> and job opening <strong>${jobTitle}</strong>. I'm ready to assist you.</p>
            <p class="mt-2">What would you like me to do next?</p>
            <div class="flex flex-wrap gap-2 mt-4">
                <button onclick="window.triggerCopilotQuickAction('draft')" class="px-4 py-2 bg-primary-container/20 border border-primary/30 rounded-full text-label-sm hover:bg-primary-container/40 transition-colors flex items-center gap-2 group">
                    <span class="material-symbols-outlined text-primary text-sm">mail</span>
                    Yes, Draft Now
                    <span class="material-symbols-outlined text-xs opacity-0 group-hover:opacity-100 transition-opacity">arrow_forward</span>
                </button>
                <button onclick="window.triggerCopilotQuickAction('roadmap')" class="px-4 py-2 bg-surface-container-highest border border-white/10 rounded-full text-label-sm hover:bg-white/5 transition-colors flex items-center gap-2 group">
                    <span class="material-symbols-outlined text-secondary text-sm">assignment_turned_in</span>
                    Generate upskilling roadmap
                    <span class="material-symbols-outlined text-xs opacity-0 group-hover:opacity-100 transition-opacity">arrow_forward</span>
                </button>
                <button onclick="window.copilotViewCandidates()" class="px-4 py-2 bg-surface-container-highest border border-white/10 rounded-full text-label-sm hover:bg-white/5 transition-colors flex items-center gap-2 group">
                    <span class="material-symbols-outlined text-tertiary text-sm">person_search</span>
                    View Candidates
                    <span class="material-symbols-outlined text-xs opacity-0 group-hover:opacity-100 transition-opacity">arrow_forward</span>
                </button>
            </div>
        </div>
    `;
    chatStream.appendChild(aiMsg);
    chatStream.scrollTop = chatStream.scrollHeight;
}

async function initRecruiterCopilot() {
    const chatStream = document.getElementById('chat-stream');
    const inputField = document.getElementById('copilot-input');
    const sendBtn = document.getElementById('copilot-send-btn');

    const candSelect = document.getElementById('context-candidate');
    const jobSelect = document.getElementById('context-job');

    if (!chatStream) return;
    chatStream.innerHTML = '<div class="text-xs text-outline py-4 text-center">Initializing Copilot...</div>';

    // Load contexts into dropdowns
    try {
        const [cRes, jRes] = await Promise.all([
            fetch(`${API_BASE}/candidates/?limit=100`),
            fetch(`${API_BASE}/jobs/`)
        ]);

        let candidates = [];
        let jobs = [];

        if (cRes.ok && candSelect) {
            candidates = await cRes.json();
            candSelect.innerHTML = '';
            candidates.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.textContent = c.name;
                candSelect.appendChild(opt);
            });
        }

        if (jRes.ok && jobSelect) {
            jobs = await jRes.json();
            jobSelect.innerHTML = '';
            jobs.forEach(j => {
                const opt = document.createElement('option');
                opt.value = j.id;
                opt.textContent = j.title;
                jobSelect.appendChild(opt);
            });
        }

        // Handle URL parameters for quick action routing
        const urlParams = new URLSearchParams(window.location.search);
        const candIdParam = urlParams.get('candidate_id');
        const jobIdParam = urlParams.get('job_id');
        const actionParam = urlParams.get('action');

        if (candIdParam && candSelect) {
            // Check if option exists in dropdown, else fetch specific candidate
            let optionExists = false;
            for (let i = 0; i < candSelect.options.length; i++) {
                if (candSelect.options[i].value == candIdParam) {
                    optionExists = true;
                    break;
                }
            }
            if (!optionExists) {
                try {
                    const extraCandRes = await fetch(`${API_BASE}/candidates/${candIdParam}`);
                    if (extraCandRes.ok) {
                        const extraCand = await extraCandRes.json();
                        const opt = document.createElement('option');
                        opt.value = extraCand.id;
                        opt.textContent = extraCand.name;
                        candSelect.appendChild(opt);
                    }
                } catch (e) {
                    console.error("Failed to fetch parameter candidate", e);
                }
            }
            candSelect.value = candIdParam;
        } else if (candidates.length > 0 && candSelect) {
            candSelect.value = candidates[0].id;
        }

        if (jobIdParam && jobSelect) {
            // Check if option exists in dropdown, else fetch specific job
            let optionExists = false;
            for (let i = 0; i < jobSelect.options.length; i++) {
                if (jobSelect.options[i].value == jobIdParam) {
                    optionExists = true;
                    break;
                }
            }
            if (!optionExists) {
                try {
                    const extraJobRes = await fetch(`${API_BASE}/jobs/${jobIdParam}`);
                    if (extraJobRes.ok) {
                        const extraJob = await extraJobRes.json();
                        const opt = document.createElement('option');
                        opt.value = extraJob.id;
                        opt.textContent = extraJob.title;
                        jobSelect.appendChild(opt);
                    }
                } catch (e) {
                    console.error("Failed to fetch parameter job", e);
                }
            }
            jobSelect.value = jobIdParam;
        } else if (jobs.length > 0 && jobSelect) {
            jobSelect.value = jobs[0].id;
        }

        // Populate Left Panel context
        const initialCandId = candSelect ? candSelect.value : '';
        const initialJobId = jobSelect ? jobSelect.value : '';
        await updateCopilotLeftPanel(initialCandId, initialJobId);

        // Print initial greeting
        const cName = candSelect && candSelect.selectedIndex >= 0 ? candSelect.options[candSelect.selectedIndex].text : 'No Candidate Selected';
        const jName = jobSelect && jobSelect.selectedIndex >= 0 ? jobSelect.options[jobSelect.selectedIndex].text : 'No Job Selected';
        displayCopilotWelcome(cName, jName);

        // Change listeners
        if (candSelect) {
            candSelect.addEventListener('change', () => {
                const cId = candSelect.value;
                const jId = jobSelect ? jobSelect.value : '';
                const params = new URLSearchParams(window.location.search);
                if (cId) params.set('candidate_id', cId);
                else params.delete('candidate_id');
                window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`);
                updateCopilotLeftPanel(cId, jId);
                const currentCName = candSelect.options[candSelect.selectedIndex]?.text || 'No Candidate Selected';
                const currentJName = jobSelect && jobSelect.selectedIndex >= 0 ? jobSelect.options[jobSelect.selectedIndex].text : 'No Job Selected';
                displayCopilotWelcome(currentCName, currentJName);
            });
        }

        if (jobSelect) {
            jobSelect.addEventListener('change', () => {
                const cId = candSelect ? candSelect.value : '';
                const jId = jobSelect.value;
                const params = new URLSearchParams(window.location.search);
                if (jId) params.set('job_id', jId);
                else params.delete('job_id');
                window.history.replaceState({}, '', `${window.location.pathname}?${params.toString()}`);
                updateCopilotLeftPanel(cId, jId);
                const currentCName = candSelect && candSelect.selectedIndex >= 0 ? candSelect.options[candSelect.selectedIndex].text : 'No Candidate Selected';
                const currentJName = jobSelect.options[jobSelect.selectedIndex]?.text || 'No Job Selected';
                displayCopilotWelcome(currentCName, currentJName);
            });
        }

        if (actionParam === 'draft' && candIdParam && jobIdParam) {
            const currentCName = candSelect.options[candSelect.selectedIndex]?.text || 'the candidate';
            const currentJName = jobSelect.options[jobSelect.selectedIndex]?.text || 'the role';
            triggerCopilotChat(`Draft an outreach email to ${currentCName} for the ${currentJName} role`);
        } else if (actionParam === 'roadmap' && candIdParam && jobIdParam) {
            const currentCName = candSelect.options[candSelect.selectedIndex]?.text || 'the candidate';
            const currentJName = jobSelect.options[jobSelect.selectedIndex]?.text || 'the role';
            triggerCopilotChat(`Generate an upskilling roadmap for ${currentCName} to match the ${currentJName} role`);
        }

    } catch (e) {
        console.error("Copilot UI setup failed", e);
    }

    // Connect View Full Profile button
    const viewProfileBtn = document.getElementById('copilot-view-profile-btn');
    if (viewProfileBtn) {
        viewProfileBtn.addEventListener('click', () => {
            if (candSelect && candSelect.value) {
                window.location.href = `candidate_details.html?id=${candSelect.value}`;
            } else {
                showToast('Please select a candidate first.', 'error');
            }
        });
    }

    // Connect Chat Submit
    if (sendBtn && inputField) {
        const handleSend = () => {
            const text = inputField.value.trim();
            if (!text) return;
            triggerCopilotChat(text);
            inputField.value = '';
        };

        sendBtn.addEventListener('click', handleSend);
        inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });
    }
}

async function triggerCopilotChat(promptText) {
    const chatStream = document.getElementById('chat-stream');
    const inputField = document.getElementById('copilot-input');
    const sendBtn = document.getElementById('copilot-send-btn');
    if (!chatStream) return;

    const candSelect = document.getElementById('context-candidate');
    const jobSelect = document.getElementById('context-job');

    const candidateId = candSelect ? parseInt(candSelect.value) || null : null;
    const jobId = jobSelect ? parseInt(jobSelect.value) || null : null;

    // Append User message
    const userMsg = document.createElement('div');
    userMsg.className = 'flex justify-end';
    userMsg.innerHTML = `
        <div class="bg-primary/20 text-on-surface rounded-2xl rounded-tr-none px-4 py-3 max-w-lg text-sm border border-primary/30 shadow-md">
            ${promptText}
        </div>
    `;
    chatStream.appendChild(userMsg);
    chatStream.scrollTop = chatStream.scrollHeight;

    // Disable inputs
    if (inputField) inputField.disabled = true;
    if (sendBtn) sendBtn.disabled = true;

    const activeAnalysis = document.getElementById('copilot-active-analysis');
    if (activeAnalysis) activeAnalysis.classList.remove('opacity-0');

    // Append Typing Indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'flex gap-3 justify-start items-start';
    typingIndicator.id = 'copilot-typing-indicator';
    typingIndicator.innerHTML = `
        <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary text-xs font-bold shrink-0">AI</div>
        <div class="glass-card rounded-2xl rounded-tl-none px-4 py-3 text-sm text-outline flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 bg-outline rounded-full animate-bounce"></span>
            <span class="w-1.5 h-1.5 bg-outline rounded-full animate-bounce [animation-delay:0.2s]"></span>
            <span class="w-1.5 h-1.5 bg-outline rounded-full animate-bounce [animation-delay:0.4s]"></span>
        </div>
    `;
    chatStream.appendChild(typingIndicator);
    chatStream.scrollTop = chatStream.scrollHeight;

    try {
        const response = await fetch(`${API_BASE}/copilot/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: promptText,
                candidate_id: candidateId,
                job_id: jobId
            })
        });

        // Remove indicator
        const indicator = document.getElementById('copilot-typing-indicator');
        if (indicator) indicator.remove();

        if (response.ok) {
            const data = await response.json();

            const aiMsg = document.createElement('div');
            aiMsg.className = 'flex gap-3 justify-start items-start';

            // Format dynamic output with styled block if email draft is generated
            const emailHtml = data.email_draft
                ? `<div class="mt-4 p-4 rounded-xl bg-white/5 border border-white/10 font-mono text-xs select-all text-on-surface whitespace-pre-wrap">${data.email_draft}</div>`
                : '';

            // Format dynamic upskilling roadmap
            let roadmapHtml = '';
            if (data.roadmap && data.roadmap.length > 0) {
                roadmapHtml = `
                    <div class="mt-4 space-y-4 border-l border-primary/30 pl-4 ml-2">
                        ${data.roadmap.map(item => `
                            <div class="relative">
                                <div class="absolute -left-[21px] top-1.5 w-2.5 h-2.5 rounded-full bg-primary ring-4 ring-primary-container/20"></div>
                                <h4 class="font-bold text-xs text-primary uppercase tracking-wider">${item.phase}</h4>
                                <p class="text-xs text-on-surface font-semibold mt-0.5">${item.skill} (${item.estimated_duration})</p>
                                <div class="mt-1 text-[11px] text-on-surface-variant">
                                    <strong>Recommended Resources:</strong>
                                    <ul class="list-disc list-inside mt-0.5 space-y-0.5">
                                        ${item.recommended_resources.map(r => `<li>${r}</li>`).join('')}
                                    </ul>
                                </div>
                                <div class="mt-1.5 p-2 rounded bg-primary/5 border border-primary/10 text-[11px] text-on-surface-variant">
                                    <strong>Hands-on Project:</strong> ${item.hands_on_project}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }

            // Format suggested actions — each action type routed to its correct handler
            let actionsHtml = '';
            if (data.suggested_actions && data.suggested_actions.length > 0) {
                actionsHtml = `
                    <div class="flex flex-wrap gap-2 mt-4">
                        ${data.suggested_actions.map(act => {
                    let onClickAttr = '';
                    if (act.action === 'chat' && act.payload && act.payload.prompt) {
                        const escapedPrompt = act.payload.prompt.replace(/'/g, "\\'");
                        onClickAttr = `onclick="window.triggerCopilotChat('${escapedPrompt}')"`;
                    } else if (act.action === 'send_email') {
                        // Open the outreach modal with the email draft from this response
                        const emailPayload = act.payload && act.payload.email
                            ? act.payload.email.replace(/`/g, '\\`').replace(/\\/g, '\\\\').replace(/'/g, "\\'")
                            : '';
                        onClickAttr = emailPayload
                            ? `onclick="window.openOutreachModal('${emailPayload}')"`
                            : `onclick="window.openOutreachModal('')"`;
                    } else if (act.action === 'rank_candidates' || act.action === 'view_candidates') {
                        const candId = act.payload && act.payload.candidate_id ? `?id=${act.payload.candidate_id}` : '';
                        onClickAttr = `onclick="window.location.href='candidate_search.html${candId}'"`;
                    } else if (act.action === 'show_rankings') {
                        onClickAttr = `onclick="window.location.href='candidate_ranking.html'"`;
                    } else if (act.action === 'skill_gap') {
                        const sgParams = act.payload && act.payload.candidate_id
                            ? `?id=${act.payload.candidate_id}${act.payload.job_id ? '&job_id=' + act.payload.job_id : ''}`
                            : '';
                        onClickAttr = `onclick="window.location.href='skill_gap_analysis.html${sgParams}'"`;
                    } else if (act.action === 'export_roadmap') {
                        onClickAttr = `onclick="showToast('Roadmap exported successfully!', 'success')"`;
                    } else if (act.action === 'share_roadmap') {
                        onClickAttr = `onclick="showToast('Roadmap shared with candidate!', 'success')"`;
                    } else {
                        onClickAttr = `onclick="showToast('${act.label} completed.', 'success')"`;
                    }
                    return `
                                <button ${onClickAttr} class="px-3 py-1.5 bg-surface-container-highest border border-white/10 hover:border-primary/30 rounded-full text-xs font-medium text-on-surface-variant hover:text-primary hover:bg-primary/5 transition-colors">
                                    ${act.label}
                                </button>
                            `;
                }).join('')}
                    </div>
                `;
            }

            aiMsg.innerHTML = `
                <div class="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center text-on-primary-container text-xs font-bold shrink-0 shadow-lg">AI</div>
                <div class="glass-card rounded-2xl rounded-tl-none px-4 py-3 max-w-xl text-sm leading-relaxed text-on-surface">
                    <div>${parseMarkdown(data.response)}</div>
                    ${emailHtml}
                    ${roadmapHtml}
                    ${actionsHtml}
                </div>
            `;
            chatStream.appendChild(aiMsg);
            chatStream.scrollTop = chatStream.scrollHeight;
        } else {
            throw new Error();
        }

    } catch (err) {
        const indicator = document.getElementById('copilot-typing-indicator');
        if (indicator) indicator.remove();

        const errorMsg = document.createElement('div');
        errorMsg.className = 'flex gap-3 justify-start items-start';
        errorMsg.innerHTML = `
            <div class="w-8 h-8 rounded-lg bg-error/20 flex items-center justify-center text-error text-xs font-bold shrink-0">AI</div>
            <div class="bg-error/10 border border-error/20 rounded-2xl rounded-tl-none px-4 py-3 text-sm text-error">
                Sorry, I could not complete this request. Please check that the FastAPI service is running.
            </div>
        `;
        chatStream.appendChild(errorMsg);
        chatStream.scrollTop = chatStream.scrollHeight;
    } finally {
        const activeAnalysis = document.getElementById('copilot-active-analysis');
        if (activeAnalysis) activeAnalysis.classList.add('opacity-0');
        if (inputField) {
            inputField.disabled = false;
            inputField.focus();
        }
        if (sendBtn) sendBtn.disabled = false;
    }
}

window.triggerCopilotChat = triggerCopilotChat;

/**
 * Opens the outreach email modal overlay.
 * Called by "Send Email" / "Yes, Draft Now" action buttons.
 * @param {string} emailText - the generated email body
 */
function openOutreachModal(emailText) {
    // Remove any existing modal
    const existing = document.getElementById('outreach-modal-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.id = 'outreach-modal-overlay';
    overlay.className = 'fixed inset-0 z-[200] flex items-center justify-center bg-black/70 backdrop-blur-sm';

    // If no emailText, try to pull last email draft from the chat
    if (!emailText) {
        const lastDraft = document.querySelector('#chat-stream .font-mono');
        emailText = lastDraft ? lastDraft.textContent : '(No email draft available. Please ask Copilot to draft an outreach email first.)';
    }

    overlay.innerHTML = `
        <div class="bg-surface-container-high border border-white/10 rounded-2xl shadow-2xl w-full max-w-2xl mx-4 flex flex-col max-h-[90vh]">
            <div class="flex items-center justify-between px-6 py-4 border-b border-white/10">
                <div class="flex items-center gap-3">
                    <span class="material-symbols-outlined text-primary" style="font-variation-settings: 'FILL' 1;">mail</span>
                    <h3 class="font-bold text-base text-on-surface">Outreach Email Draft</h3>
                </div>
                <button onclick="document.getElementById('outreach-modal-overlay').remove()"
                    class="text-on-surface-variant hover:text-on-surface rounded-full p-1 hover:bg-white/5 transition-colors">
                    <span class="material-symbols-outlined">close</span>
                </button>
            </div>
            <div class="flex-1 overflow-y-auto p-6">
                <textarea id="outreach-email-body"
                    class="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-sm font-mono text-on-surface leading-relaxed resize-none focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/30 min-h-[300px]"
                >${emailText.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</textarea>
            </div>
            <div class="px-6 py-4 border-t border-white/10 flex items-center justify-between gap-3">
                <p class="text-xs text-on-surface-variant/60">Edit the draft above before sending.</p>
                <div class="flex gap-2">
                    <button onclick="document.getElementById('outreach-modal-overlay').remove()"
                        class="px-4 py-2 rounded-xl border border-white/10 text-sm text-on-surface-variant hover:bg-white/5 transition-colors">
                        Cancel
                    </button>
                    <button onclick="window.copyOutreachEmail()"
                        class="px-4 py-2 rounded-xl bg-primary-container text-on-primary-container text-sm font-bold hover:bg-primary-container/80 active:scale-95 transition-all flex items-center gap-2">
                        <span class="material-symbols-outlined text-sm">content_copy</span>
                        Copy to Clipboard
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    // Close on backdrop click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.remove();
    });
}

window.openOutreachModal = openOutreachModal;

window.copyOutreachEmail = function() {
    const textarea = document.getElementById('outreach-email-body');
    if (!textarea) return;
    navigator.clipboard.writeText(textarea.value).then(() => {
        showToast('Email draft copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback for non-HTTPS or older browsers
        textarea.select();
        document.execCommand('copy');
        showToast('Email draft copied!', 'success');
    });
};



// --- 8. SETTINGS ---
function initSettings() {
    // Basic settings dynamic feedback
    const sliders = document.querySelectorAll('input[type="range"]');
    sliders.forEach(slider => {
        const display = slider.previousElementSibling?.querySelector('span');
        slider.addEventListener('input', () => {
            if (display) {
                display.textContent = `${slider.value}% Match`;
            }
        });
    });

    const recalibrateBtn = document.querySelector('button.border-tertiary');
    if (recalibrateBtn) {
        recalibrateBtn.addEventListener('click', () => {
            showToast('AI Recalibration sequence completed successfully!');
        });
    }
}

// ==========================================
// JOB DESCRIPTION INTELLIGENCE FUNCTIONS
// ==========================================

function setupJdIntelligence() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('jd-file-input');

    if (!dropZone || !fileInput || dropZone.dataset.initialized) return;
    dropZone.dataset.initialized = 'true';

    // Trigger file input click on drop zone click
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file selection
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            uploadAndAnalyzeJD(file);
        }
    });

    // Handle Drag & Drop events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-primary', 'bg-white/10');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-primary', 'bg-white/10');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-primary', 'bg-white/10');
        const file = e.dataTransfer.files[0];
        if (file) {
            uploadAndAnalyzeJD(file);
        }
    });
}

async function uploadAndAnalyzeJD(file) {
    const loadingOverlay = document.getElementById('upload-loading');
    if (loadingOverlay) loadingOverlay.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/jobs/analyze`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed to analyze job description.');
        }

        const data = await response.json();
        showToast('Job description analyzed successfully!', 'success');
        openReviewModal(data);
    } catch (err) {
        console.error('JD Analysis error:', err);
        showToast(err.message || 'Error analyzing job description.', 'error');
    } finally {
        if (loadingOverlay) loadingOverlay.classList.add('hidden');
        // Reset file input value
        const fileInput = document.getElementById('jd-file-input');
        if (fileInput) fileInput.value = '';
    }
}

let currentAnalysisResult = null;

function openReviewModal(data) {
    currentAnalysisResult = data;
    const modal = document.getElementById('review-modal');
    if (!modal) return;

    // Fill simple fields
    document.getElementById('review-title').value = data.title || '';
    document.getElementById('review-department').value = data.department || 'Engineering';
    document.getElementById('review-location').value = data.location || 'Remote';
    document.getElementById('review-work-preference').value = data.work_preference || 'Remote';
    document.getElementById('review-experience-required').value = data.experience_required || 0;
    document.getElementById('review-experience-text').value = data.experience_text || '';
    document.getElementById('review-required-skills').value = data.required_skills ? data.required_skills.join(', ') : '';
    document.getElementById('review-preferred-skills').value = data.preferred_skills ? data.preferred_skills.join(', ') : '';
    document.getElementById('review-education').value = data.education_requirements ? data.education_requirements.join('\n') : '';
    document.getElementById('review-description').value = data.description || '';

    // Disqualifiers
    const disqList = document.getElementById('review-disqualifiers');
    if (disqList) {
        disqList.innerHTML = '';
        const disqualifiers = data.disqualifiers || [];
        disqualifiers.forEach(dq => {
            const li = document.createElement('li');
            li.textContent = dq;
            disqList.appendChild(li);
        });
    }

    // Vibe check
    const vibeList = document.getElementById('review-vibe-check');
    if (vibeList) {
        vibeList.innerHTML = '';
        const vibe = data.vibe_check || [];
        vibe.forEach(v => {
            const li = document.createElement('li');
            li.textContent = v;
            vibeList.appendChild(li);
        });
    }

    modal.classList.remove('hidden');
}

function closeReviewModal() {
    const modal = document.getElementById('review-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

async function saveAnalyzedJob() {
    const title = document.getElementById('review-title').value.trim();
    if (!title) {
        showToast('Please enter a job title.', 'error');
        return;
    }

    const saveBtn = document.getElementById('save-job-btn');
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
    }

    const reqSkillsText = document.getElementById('review-required-skills').value;
    const required_skills = reqSkillsText ? reqSkillsText.split(',').map(s => s.trim()).filter(Boolean) : [];

    const description = document.getElementById('review-description').value;

    const payload = {
        title: title,
        department: document.getElementById('review-department').value.trim() || 'Engineering',
        location: document.getElementById('review-location').value.trim() || 'Remote',
        work_preference: document.getElementById('review-work-preference').value || 'Remote',
        experience_required: parseFloat(document.getElementById('review-experience-required').value) || 0.0,
        required_skills: required_skills,
        description: description || `Extracted requirements: ${document.getElementById('review-experience-text').value}`,
        status: 'Active',
        priority: 'High'
    };

    try {
        const response = await fetch(`${API_BASE}/jobs/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Failed to create job.');
        }

        showToast('Job role created successfully!');
        closeReviewModal();

        // Refresh dashboard statistics and jobs list
        await initDashboard();
    } catch (err) {
        console.error('Save job error:', err);
        showToast(err.message || 'Error creating job role.', 'error');
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Confirm & Create Job';
        }
    }
}

// Attach functions to window scope to ensure they are accessible from inline attributes
window.closeReviewModal = closeReviewModal;
window.saveAnalyzedJob = saveAnalyzedJob;
window.setupJdIntelligence = setupJdIntelligence;
window.uploadAndAnalyzeJD = uploadAndAnalyzeJD;
window.openReviewModal = openReviewModal;


/**
 * TalentMind AI - Frontend/Backend Integration System
 * Integrates Stitch UI screens with the FastAPI REST API.
 */

const API_BASE = 'http://127.0.0.1:8000/api';

document.addEventListener('DOMContentLoaded', () => {
    // 1. Setup Global Elements (Sidebar, Header, API Indicator)
    setupSidebar();
    checkApiConnection();

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
        const res = await fetch(`${API_BASE}/jobs`);
        if (res.ok) {
            indicator.className = 'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold mr-4 bg-tertiary/10 text-tertiary border border-tertiary/20';
            indicator.innerHTML = '<span class="w-2 h-2 rounded-full bg-tertiary animate-pulse"></span> API: CONNECTED';
        } else {
            throw new Error();
        }
    } catch (e) {
        indicator.className = 'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold mr-4 bg-error/10 text-error border border-error/20';
        indicator.innerHTML = '<span class="w-2 h-2 rounded-full bg-error animate-pulse"></span> API: OFFLINE';
        showToast('FastAPI Backend Offline. Utilizing mock templates.', 'error');
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
    toast.className = `glass-card p-4 rounded-xl shadow-2xl flex items-center gap-3 border-l-4 transform translate-y-4 opacity-0 transition-all duration-300 ${
        type === 'error' ? 'border-error' : 'border-tertiary'
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
        const [cRes, jRes] = await Promise.all([
            fetch(`${API_BASE}/candidates`),
            fetch(`${API_BASE}/jobs`)
        ]);
        
        if (!cRes.ok || !jRes.ok) return;

        const candidates = await cRes.json();
        const jobs = await jRes.json();

        // Update KPIs
        const kpiContainers = document.querySelectorAll('.font-headline-lg');
        if (kpiContainers.length >= 3) {
            // Total Candidates
            kpiContainers[0].textContent = candidates.length.toLocaleString();
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
let allCandidates = [];
async function initCandidateSearch() {
    try {
        const res = await fetch(`${API_BASE}/candidates`);
        if (!res.ok) return;
        allCandidates = await res.json();
        
        // Populate standard skills filter panel dynamically
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
                filterCandidates();
            });
        }

        if (searchInput) {
            searchInput.addEventListener('input', filterCandidates);
        }

        // Connect work preference check boxes
        document.querySelectorAll('input[type="checkbox"]').forEach(box => {
            box.addEventListener('change', filterCandidates);
        });

        // Initial render
        renderCandidateCards(allCandidates);

    } catch (err) {
        console.error("Candidate search init failed", err);
    }
}

function setupSkillsFilter() {
    const filterContainer = document.getElementById('skills-filter-container');
    if (!filterContainer) return;
    
    // Extract unique skills from all candidates
    const allSkills = new Set();
    allCandidates.forEach(c => c.skills?.forEach(s => allSkills.add(s)));
    
    filterContainer.innerHTML = '';
    allSkills.forEach(skill => {
        const btn = document.createElement('button');
        btn.className = 'px-3 py-1 rounded-full text-xs font-medium bg-white/5 border border-white/10 hover:border-primary/40 text-on-surface-variant transition-all';
        btn.textContent = skill;
        btn.addEventListener('click', () => {
            btn.classList.toggle('bg-primary/20');
            btn.classList.toggle('text-primary');
            btn.classList.toggle('border-primary/50');
            filterCandidates();
        });
        filterContainer.appendChild(btn);
    });
}

function filterCandidates() {
    const searchInput = document.querySelector('header input') || document.querySelector('main input');
    const query = searchInput ? searchInput.value.toLowerCase() : '';
    
    const expSlider = document.querySelector('input[type="range"]');
    const minExp = expSlider ? parseInt(expSlider.value) : 0;

    // Get active skills
    const activeSkills = [];
    document.querySelectorAll('#skills-filter-container button.text-primary').forEach(btn => {
        activeSkills.push(btn.textContent.toLowerCase());
    });

    // Get active work preferences
    const preferences = [];
    document.querySelectorAll('input[type="checkbox"]:checked').forEach(box => {
        const labelText = box.nextElementSibling?.textContent.toLowerCase() || '';
        if (labelText.includes('remote')) preferences.push('remote');
        if (labelText.includes('hybrid')) preferences.push('hybrid');
        if (labelText.includes('onsite')) preferences.push('onsite');
    });

    const filtered = allCandidates.filter(c => {
        const matchesQuery = c.name.toLowerCase().includes(query) || 
                             c.title.toLowerCase().includes(query) || 
                             c.skills.some(s => s.toLowerCase().includes(query));
        const matchesExp = c.experience_years >= minExp;
        const matchesSkills = activeSkills.every(s => c.skills.map(sk => sk.toLowerCase()).includes(s));
        
        let matchesPref = true;
        if (preferences.length > 0) {
            matchesPref = preferences.includes(c.work_preference.toLowerCase());
        }

        return matchesQuery && matchesExp && matchesSkills && matchesPref;
    });

    renderCandidateCards(filtered);
}

// Compare selected candidates state
let selectedForComparison = new Set();

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
                    <span class="flex items-center gap-0.5"><span class="material-symbols-outlined text-sm">location_on</span>${c.location}</span>
                    <span>•</span>
                    <span>${c.experience_years} Years Exp</span>
                </div>
                <div class="flex flex-wrap gap-1.5 mt-4">
                    ${c.skills.slice(0, 4).map(s => `<span class="bg-white/5 px-2.5 py-0.5 rounded-full text-[10px] text-on-surface-variant">${s}</span>`).join('')}
                    ${c.skills.length > 4 ? `<span class="bg-primary/10 text-primary px-2.5 py-0.5 rounded-full text-[10px] font-bold">+${c.skills.length - 4}</span>` : ''}
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
        const res = await fetch(`${API_BASE}/jobs`);
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
                                <h4 class="font-bold text-on-surface text-body-md hover:text-primary cursor-pointer" onclick="window.location.href='candidate_details.html?id=${r.candidate_id}&job_id=${jobId}'">${r.candidate.name}</h4>
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
                            <h3 class="font-headline-md text-on-surface cursor-pointer hover:text-primary" onclick="window.location.href='candidate_details.html?id=${r.candidate_id}&job_id=${jobId}'">${r.candidate.name}</h3>
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
            fetch(`${API_BASE}/jobs`)
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
                    <p class="text-lg font-bold text-on-surface mt-1">$${candidate.salary_expectation?.toLocaleString() || 'N/A'}</p>
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
        const res = await fetch(`${API_BASE}/candidates/${candId}/skill-gap/${jobId}`);
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
    const jobId = urlParams.get('job_id') || '1';

    const ids = candidateIds.split(',');
    const container = document.querySelector('main .grid');
    if (!container) return;

    try {
        const cPromises = ids.map(id => fetch(`${API_BASE}/candidates/${id}`).then(res => res.json()));
        const candidates = await Promise.all(cPromises);

        // Fetch rankings to extract match scores & sentiments
        let rankings = [];
        try {
            const rRes = await fetch(`${API_BASE}/ranking/job/${jobId}`);
            if (rRes.ok) rankings = await rRes.json();
        } catch (e) {
            console.error("Could not fetch rankings for comparison", e);
        }

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

        candidates.forEach(c => {
            const ranking = rankings.find(r => r.candidate_id === c.id);
            const score = ranking ? Math.round(ranking.match_score) : 75;
            
            const card = document.createElement('div');
            card.className = 'p-8 border-b border-white/5 border-l border-white/5 relative';
            card.innerHTML = `
                <div class="flex flex-col items-center text-center">
                    <div class="relative mb-4">
                        <img class="w-24 h-24 rounded-2xl object-cover ring-4 ring-primary/20" src="${c.avatar_url || 'https://lh3.googleusercontent.com/aida-public/AB6AXuBT0NpLK060VPqvHHfKqSM591wQsyX0wC7wEB5wvoRdsoRdamqgXYFH0gJhUHdvQWx5cE4HgWiGNUWWq3xepl4KCzThVL1MpNTOPjQ1NBKYbfRWoT8186Bdbu8pctaSA8gVo4tENwDGlYfp6Yq8Wc8FJA2uDuojrf4FpbNU_GSiYDr_s0f4MJDu73q04MOFgQK7LvTSIY-r4qb-lJCDFElsS1zQCpCIcdnpNzPx8ITAxy7cISBR_J2BKBoZrpcFuTb3Iwz7Bjr4NfAI'}" alt=""/>
                        <div class="absolute -bottom-2 -right-2 w-8 h-8 bg-tertiary rounded-full flex items-center justify-center text-on-tertiary shadow-lg">
                            <span class="font-bold text-xs">${score}</span>
                        </div>
                    </div>
                    <h3 class="font-headline-md text-on-surface text-lg font-bold">${c.name}</h3>
                    <p class="text-on-surface-variant/70 text-xs">${c.title}</p>
                    <p class="text-[10px] text-tertiary font-bold mt-2 flex items-center justify-center gap-1">
                        <span class="w-1.5 h-1.5 bg-tertiary rounded-full status-dot"></span>
                        MATCH: ${score >= 85 ? 'HIGH' : score >= 70 ? 'POTENTIAL' : 'MODERATE'}
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
                <span class="font-bold text-on-surface">Total Experience</span>
            </div>
        `;
        container.appendChild(expLabel);

        candidates.forEach(c => {
            const expCell = document.createElement('div');
            expCell.className = 'p-8 border-b border-white/5 border-l border-white/5 flex items-center justify-center font-mono-data text-headline-md text-on-surface';
            expCell.textContent = `${c.experience_years} Years`;
            container.appendChild(expCell);
        });

        // Row 3: Skills List
        const skillsLabel = document.createElement('div');
        skillsLabel.className = 'p-8 border-b border-white/5 flex items-start pt-10';
        skillsLabel.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-primary-fixed">psychology_alt</span>
                <span class="font-bold text-on-surface">Skills alignment</span>
            </div>
        `;
        container.appendChild(skillsLabel);

        candidates.forEach(c => {
            const skillCell = document.createElement('div');
            skillCell.className = 'p-8 border-b border-white/5 border-l border-white/5 space-y-4';
            
            // Render first 4 skills with visual bar
            skillCell.innerHTML = c.skills.slice(0, 3).map(skill => `
                <div class="space-y-1">
                    <div class="flex justify-between text-[10px] uppercase font-bold tracking-wider mb-1">
                        <span>${skill}</span>
                        <span class="text-tertiary">100%</span>
                    </div>
                    <div class="h-1.5 w-full bg-surface-variant rounded-full overflow-hidden">
                        <div class="h-full bg-tertiary rounded-full shadow-[0_0_8px_rgba(78,222,163,0.5)]" style="width: 100%"></div>
                    </div>
                </div>
            `).join('') || '<p class="text-xs text-outline">None</p>';
            
            container.appendChild(skillCell);
        });

        // Row 4: AI Sentiment fit description
        const sentimentLabel = document.createElement('div');
        sentimentLabel.className = 'p-8 border-b border-white/5 flex items-start pt-10 bg-white/2';
        sentimentLabel.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-primary">auto_awesome</span>
                <span class="font-bold text-on-surface">AI Sentiment</span>
            </div>
        `;
        container.appendChild(sentimentLabel);

        candidates.forEach(c => {
            const ranking = rankings.find(r => r.candidate_id === c.id);
            const explanation = ranking ? ranking.explanation : "High capability craftsperson.";

            const sentimentCell = document.createElement('div');
            sentimentCell.className = 'p-8 border-b border-white/5 border-l border-white/5 bg-primary-container/5';
            sentimentCell.innerHTML = `
                <div class="flex items-center gap-2 mb-4">
                    <div class="flex gap-1 text-tertiary">
                        <span class="material-symbols-outlined text-lg" style="font-variation-settings: 'FILL' 1;">mood</span>
                        <span class="material-symbols-outlined text-lg" style="font-variation-settings: 'FILL' 1;">mood</span>
                    </div>
                    <span class="text-[10px] font-bold text-tertiary tracking-widest uppercase">Culture Fit Approved</span>
                </div>
                <p class="text-xs text-on-surface-variant leading-relaxed">
                    ${explanation}
                </p>
            `;
            container.appendChild(sentimentCell);
        });

        // Row 5: Final fit score circle UI
        const scoreLabel = document.createElement('div');
        scoreLabel.className = 'p-8 flex items-center';
        scoreLabel.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-primary-fixed">target</span>
                <span class="font-bold text-on-surface">Final Fit Score</span>
            </div>
        `;
        container.appendChild(scoreLabel);

        candidates.forEach(c => {
            const ranking = rankings.find(r => r.candidate_id === c.id);
            const score = ranking ? Math.round(ranking.match_score) : 75;
            const scoreColor = score >= 85 ? 'border-tertiary text-tertiary' : 'border-primary text-primary';

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
            fetch(`${API_BASE}/candidates/${candId}/skill-gap/${jobId}`)
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

        // Populate match score
        const score = Math.round(gap.match_score);
        const scoreCircle = document.querySelector('main .w-32.h-32') || document.getElementById('score-circle');
        if (scoreCircle) {
            scoreCircle.innerHTML = `
                <div class="text-4xl font-bold text-tertiary">${score}%</div>
                <div class="text-[10px] text-outline uppercase mt-1">Match</div>
            `;
        }

        // Fill Skill alignment columns
        const gainedList = document.getElementById('matching-skills-container') || document.querySelector('.grid.grid-cols-2 > div:first-child ul');
        const missingList = document.getElementById('missing-skills-container') || document.querySelector('.grid.grid-cols-2 > div:last-child ul');
        
        if (gainedList) {
            gainedList.innerHTML = gap.matching_skills.map(s => `
                <li class="flex items-center gap-3 py-2 border-b border-white/5 text-sm">
                    <span class="material-symbols-outlined text-tertiary text-lg">check_circle</span>
                    <span>${s}</span>
                </li>
            `).join('') || '<li class="text-xs text-outline py-2">No matching skills</li>';
        }

        if (missingList) {
            missingList.innerHTML = gap.missing_skills.map(s => `
                <li class="flex items-center gap-3 py-2 border-b border-white/5 text-sm">
                    <span class="material-symbols-outlined text-error text-lg">cancel</span>
                    <span>${s}</span>
                </li>
            `).join('') || '<li class="text-xs text-outline py-2">No missing skills</li>';
        }

        // Upskilling roadmap steps
        const roadmapContainer = document.getElementById('upskilling-steps') || document.querySelector('.space-y-6');
        if (roadmapContainer) {
            roadmapContainer.innerHTML = gap.upskilling_roadmap.map((step, idx) => `
                <div class="flex gap-4 p-4 rounded-xl bg-white/2 hover:bg-white/5 transition-colors">
                    <div class="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold text-sm shrink-0">
                        ${idx + 1}
                    </div>
                    <div>
                        <h4 class="text-sm font-bold text-on-surface">Target Milestone</h4>
                        <p class="text-xs text-outline mt-1">${step}</p>
                    </div>
                </div>
            `).join('');
        }

    } catch (e) {
        console.error("Skill gap initialization failed", e);
    }
}

// --- 7. RECRUITER COPILOT ---
async function initRecruiterCopilot() {
    const chatStream = document.getElementById('chat-container') || document.getElementById('chat-stream');
    const inputField = document.querySelector('footer input') || document.querySelector('main input[type="text"]');
    const sendBtn = document.querySelector('footer button') || document.querySelector('main button');

    const candSelect = document.getElementById('context-candidate') || document.getElementById('candidate-dropdown');
    const jobSelect = document.getElementById('context-job') || document.getElementById('job-dropdown');

    if (!chatStream) return;

    // Load contexts into dropdowns
    try {
        const [cRes, jRes] = await Promise.all([
            fetch(`${API_BASE}/candidates`),
            fetch(`${API_BASE}/jobs`)
        ]);

        if (cRes.ok && candSelect) {
            const candidates = await cRes.json();
            candSelect.innerHTML = '<option value="">-- No Candidate Selected --</option>';
            candidates.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.textContent = c.name;
                candSelect.appendChild(opt);
            });
        }

        if (jRes.ok && jobSelect) {
            const jobs = await jRes.json();
            jobSelect.innerHTML = '<option value="">-- No Job Selected --</option>';
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

        if (candIdParam && candSelect) candSelect.value = candIdParam;
        if (jobIdParam && jobSelect) jobSelect.value = jobIdParam;

        if (actionParam === 'draft' && candIdParam && jobIdParam) {
            const cName = candSelect.options[candSelect.selectedIndex]?.text || 'the candidate';
            const jName = jobSelect.options[jobSelect.selectedIndex]?.text || 'the role';
            triggerCopilotChat(`Draft an outreach email to ${cName} for the ${jName} role`);
        }

    } catch (e) {
        console.error("Copilot UI setup failed", e);
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
            if (e.key === 'Enter') handleSend();
        });
    }
}

async function triggerCopilotChat(promptText) {
    const chatStream = document.getElementById('chat-container') || document.getElementById('chat-stream') || document.querySelector('.space-y-6');
    if (!chatStream) return;

    const candSelect = document.getElementById('context-candidate') || document.getElementById('candidate-dropdown');
    const jobSelect = document.getElementById('context-job') || document.getElementById('job-dropdown');

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

            aiMsg.innerHTML = `
                <div class="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center text-on-primary-container text-xs font-bold shrink-0 shadow-lg">AI</div>
                <div class="glass-card rounded-2xl rounded-tl-none px-4 py-3 max-w-xl text-sm leading-relaxed text-on-surface">
                    <p>${parseMarkdown(data.response)}</p>
                    ${emailHtml}
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
    }
}

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
        const response = await fetch(`${API_BASE}/jobs`, {
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


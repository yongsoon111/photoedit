// Error Popup Function
function showErrorPopup(title, error, details = {}) {
    const errorInfo = {
        title: title,
        message: error?.message || String(error),
        stack: error?.stack || 'No stack trace',
        timestamp: new Date().toISOString(),
        url: window.location.href,
        ...details
    };

    const errorText = `
═══════════════════════════════════
🚨 ERROR: ${errorInfo.title}
═══════════════════════════════════
📅 Time: ${errorInfo.timestamp}
🌐 URL: ${errorInfo.url}

❌ Message:
${errorInfo.message}

📍 Stack Trace:
${errorInfo.stack}

📋 Additional Details:
${JSON.stringify(details, null, 2)}
═══════════════════════════════════
    `.trim();

    console.error(errorText);
    alert(errorText);
}

// Core Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const mapUrlInput = document.getElementById('map-url');
const urlSpinner = document.getElementById('url-spinner');
const latInput = document.getElementById('lat');
const lonInput = document.getElementById('lon');
const addressInput = document.getElementById('address-input');
const processBtn = document.getElementById('process-btn');
const downloadLink = document.getElementById('download-link');

const dashboard = document.getElementById('dashboard');
const previewOriginal = document.getElementById('preview-original');
const previewNormalized = document.getElementById('preview-normalized');
const resetBtn = document.getElementById('reset-btn');

// Copy Feature Elements
const locationText = document.getElementById('location-text');
const copyBtn = document.getElementById('copy-btn');
const copyIcon = document.getElementById('copy-icon');
const checkIcon = document.getElementById('check-icon');

// Inspector Elements
const inspectorDashboard = document.getElementById('inspector-dashboard');
const inspectorBody = document.getElementById('inspector-body');
const fileCount = document.getElementById('file-count');

// Queue Elements
const queuePanel = document.getElementById('queue-panel');
const queueList = document.getElementById('queue-list');
const queueProgress = document.getElementById('queue-progress');
const resultCount = document.getElementById('result-count');

// Drag & Drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
        handleFile(fileInput.files[0]);
    }
});

let selectedFile = null;

async function handleFile(file) {
    if (!file.type.startsWith('image/') && !file.name.toLowerCase().endsWith('.zip')) {
        alert('이미지 또는 ZIP 파일을 업로드해주세요.');
        return;
    }
    selectedFile = file;

    // Update Drop Zone UI
    const h3 = dropZone.querySelector('h3');
    const p = dropZone.querySelector('p');
    if (h3) h3.textContent = file.name;
    if (p) p.textContent = '메타데이터 분석 중...';

    // Reset Views
    dashboard.classList.add('hidden');
    inspectorBody.innerHTML = '<tr><td colspan="5" class="p-8 text-center text-slate-500 animate-pulse">분석 중...</td></tr>';

    // 1. Analyze Metadata
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/analyze', { method: 'POST', body: formData });
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        const report = await response.json();
        populateInspector(report);
        if (p) p.textContent = '분석 완료. 변환 준비됨.';
    } catch (e) {
        showErrorPopup('파일 분석 실패', e, { filename: file.name, fileType: file.type, fileSize: file.size });
        inspectorBody.innerHTML = '<tr><td colspan="5" class="p-8 text-center text-red-400">분석 실패</td></tr>';
        if (p) p.textContent = '분석 실패.';
    }

    // Preview (Image Only)
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => { previewOriginal.src = e.target.result; };
        reader.readAsDataURL(file);

        // Ensure result areas are images
        previewOriginal.style.display = 'block';
        previewNormalized.style.display = 'block';
    } else {
        // ZIP Preview placeholder
        previewOriginal.src = "";
        previewOriginal.style.display = 'none'; // Or show icon
        // We could just show nothing or a generic icon div, but sticking to simple logic
    }
}

function populateInspector(report) {
    fileCount.textContent = `${report.length}개 파일 발견`;
    fileCount.className = "text-xs px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20";

    // Store report for queue display
    window.currentReport = report;

    inspectorBody.innerHTML = report.map(item => `
        <tr class="hover:bg-white/5 transition-colors">
            <!-- 📸 Identity -->
            <td class="p-2 font-mono text-slate-300 truncate max-w-[100px]" title="${item.filename}">${item.filename}</td>
            <td class="p-2 text-slate-300 font-medium truncate max-w-[80px]" title="${item.model}">${item.model || '-'}</td>
            <td class="p-2 text-slate-400 truncate max-w-[60px]">${item.make || '-'}</td>
            <td class="p-2 text-slate-400 font-mono">${item.datetime || '-'}</td>
            <!-- 📍 Location & Security (FULL DISPLAY) -->
            <td class="p-2 font-mono ${item.has_gps ? 'text-red-400' : 'text-slate-600'}">${item.gps_coords || '-'}</td>
            <td class="p-2 text-green-400 text-xs">${item.address_tag || '-'}</td>
            <td class="p-2 font-mono text-slate-500">${item.file_hash || '-'}</td>
            <td class="p-2 text-slate-400">${item.resolution || '-'}</td>
            <!-- ⚙️ Camera Specs -->
            <td class="p-2 font-mono text-accent-500">${item.aperture || '-'}</td>
            <td class="p-2 font-mono text-slate-400">${item.focal_length || '-'}</td>
            <td class="p-2 font-mono text-slate-400">${item.iso || '-'}</td>
            <td class="p-2 font-mono text-slate-400">${item.shutter_speed || '-'}</td>
            <td class="p-2 text-slate-400 truncate max-w-[100px]" title="${item.lens_model}">${item.lens_model || '-'}</td>
            <!-- 🕵️ Deep Metadata -->
            <td class="p-2 font-mono text-slate-600 truncate max-w-[60px]" title="${item.body_serial}">${item.body_serial || '-'}</td>
            <td class="p-2 font-mono text-slate-600 truncate max-w-[60px]" title="${item.lens_serial}">${item.lens_serial || '-'}</td>
            <td class="p-2 text-slate-500 truncate max-w-[80px]" title="${item.software}">${item.software || '-'}</td>
        </tr>
    `).join('');
}

// === Job Queue System ===
let jobQueue = [];
let jobCounter = 0;

function addJob(filename, formData) {
    jobCounter++;
    const jobId = jobCounter;
    const job = {
        id: jobId,
        filename: filename,
        formData: formData,
        status: 'pending'
    };
    jobQueue.push(job);
    renderJobQueue();
    processJob(job);
    return jobId;
}

function renderJobQueue() {
    if (!queuePanel) return;
    queuePanel.classList.remove('hidden');

    const total = jobQueue.length;
    const done = jobQueue.filter(j => j.status === 'done').length;
    queueProgress.textContent = `${done}/${total}`;

    queueList.innerHTML = jobQueue.map((job, idx) => {
        let statusClass = 'text-yellow-500';
        let statusHtml = '<span class="text-yellow-500 text-[10px]">대기중</span>';
        let bgClass = 'bg-slate-800/50';

        if (job.status === 'processing') {
            statusClass = 'text-brand-500 animate-pulse font-bold';
            statusHtml = '<span class="text-brand-500 text-[10px] font-bold animate-pulse">⚡ 작동중</span>';
            bgClass = 'bg-brand-500/10 border border-brand-500/30';
        } else if (job.status === 'done' && job.downloadUrl) {
            bgClass = 'bg-green-500/10 border border-green-500/30';
            statusHtml = `<a href="${job.downloadUrl}" download="${job.filename.replace('.zip', '_normalized.zip')}" 
                class="px-2 py-1 rounded bg-green-500 hover:bg-green-600 text-white text-[10px] font-bold transition-colors flex items-center gap-1">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                </svg>
                다운로드
            </a>`;
        } else if (job.status === 'error') {
            statusHtml = '<span class="text-red-400 text-[10px]">❌ 오류</span>';
            bgClass = 'bg-red-500/10 border border-red-500/30';
        }

        return `
            <div class="flex items-center gap-2 p-2 rounded ${bgClass}">
                <span class="w-6 h-6 rounded-full bg-slate-700 flex items-center justify-center text-[10px] text-white font-bold">${job.id}</span>
                <span class="flex-1 truncate text-slate-300 text-xs">${job.filename}</span>
                ${statusHtml}
            </div>
        `;
    }).join('');
}

async function processJob(job) {
    job.status = 'processing';
    renderJobQueue();

    try {
        const response = await fetch('/normalize', {
            method: 'POST',
            body: job.formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        job.status = 'done';
        job.downloadUrl = url;
        job.blob = blob;
        renderJobQueue();

        // Check if all jobs are done
        const allDone = jobQueue.every(j => j.status === 'done' || j.status === 'error');
        if (allDone) {
            showAllCompleted();
        }

    } catch (error) {
        job.status = 'error';
        job.errorMessage = error.message;
        renderJobQueue();
        showErrorPopup(`작업 #${job.id} 실패`, error, {
            jobId: job.id,
            filename: job.filename,
            lat: job.formData.get('lat'),
            lon: job.formData.get('lon')
        });
    }
}

function showAllCompleted() {
    dashboard.classList.remove('hidden');
    if (resultCount) {
        const doneCount = jobQueue.filter(j => j.status === 'done').length;
        resultCount.textContent = `${doneCount}개 작업 완료`;
    }

    // Set download for the last completed job
    const lastDone = [...jobQueue].reverse().find(j => j.status === 'done');
    if (lastDone && lastDone.downloadUrl) {
        downloadLink.href = lastDone.downloadUrl;
        downloadLink.download = lastDone.filename.replace('.zip', '_normalized.zip');
    }
}

function clearJobQueue() {
    jobQueue = [];
    jobCounter = 0;
    if (queuePanel) queuePanel.classList.add('hidden');
}

function updateQueueItem(idx, status, total) {
    const statusEl = document.getElementById(`queue-status-${idx}`);
    const itemEl = document.getElementById(`queue-item-${idx}`);

    if (statusEl) {
        if (status === 'processing') {
            statusEl.textContent = '⚡ 작동중';
            statusEl.className = 'text-brand-500 text-[10px] font-bold animate-pulse';
            if (itemEl) itemEl.className = 'flex items-center gap-2 p-2 rounded bg-brand-500/10 border border-brand-500/30';
        } else if (status === 'done') {
            statusEl.textContent = '✅ 완료';
            statusEl.className = 'text-green-400 text-[10px]';
            if (itemEl) itemEl.className = 'flex items-center gap-2 p-2 rounded bg-green-500/10 border border-green-500/30';
        }
    }

    if (queueProgress) {
        const done = document.querySelectorAll('[id^="queue-status-"]');
        const doneCount = Array.from(done).filter(el => el.textContent.includes('완료')).length;
        queueProgress.textContent = `${doneCount}/${total}`;
    }
}

function hideQueue() {
    if (queuePanel) queuePanel.classList.add('hidden');
}

// Check Map URL
let urlTimeout = null;
mapUrlInput.addEventListener('input', (e) => {
    const url = e.target.value.trim();
    if (!url) return;

    if (urlTimeout) clearTimeout(urlTimeout);
    urlTimeout = setTimeout(() => {
        fetchLocationFromUrl(url);
    }, 500);
});

async function fetchLocationFromUrl(url) {
    urlSpinner.classList.remove('hidden');
    try {
        const response = await fetch('/extract-location', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.lat && data.lon) {
                latInput.value = data.lat;
                lonInput.value = data.lon;

                latInput.classList.add('border-brand-500', 'ring-1', 'ring-brand-500');
                lonInput.classList.add('border-brand-500', 'ring-1', 'ring-brand-500');
                setTimeout(() => {
                    latInput.classList.remove('border-brand-500', 'ring-1', 'ring-brand-500');
                    lonInput.classList.remove('border-brand-500', 'ring-1', 'ring-brand-500');
                }, 1000);
            }
        }
    } catch (error) {
        showErrorPopup('위치 추출 실패', error, { url: url });
    } finally {
        urlSpinner.classList.add('hidden');
    }
}

// Process - Non-blocking with job queue
processBtn.addEventListener('click', () => {
    if (!selectedFile) {
        alert('먼저 이미지나 ZIP 파일을 업로드해주세요.');
        return;
    }

    if (!latInput.value || !lonInput.value) {
        alert('좌표를 입력해주세요.');
        return;
    }

    // Create FormData for this job
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('lat', latInput.value);
    formData.append('lon', lonInput.value);
    formData.append('address_text', addressInput ? addressInput.value : '');

    // Add job to queue (runs in background, doesn't block UI)
    addJob(selectedFile.name, formData);

    // Brief button feedback
    const btnText = processBtn.querySelector('span');
    if (btnText) {
        const originalText = btnText.textContent;
        btnText.textContent = '✓ 대기열 추가됨';
        setTimeout(() => {
            btnText.textContent = originalText;
        }, 500);
    }
});

// Copy Handler
copyBtn.addEventListener('click', () => {
    const text = locationText.textContent;
    if (!text || text === 'Calculating...') return;

    navigator.clipboard.writeText(text).then(() => {
        // Show success state
        copyIcon.classList.add('hidden');
        checkIcon.classList.remove('hidden');

        setTimeout(() => {
            copyIcon.classList.remove('hidden');
            checkIcon.classList.add('hidden');
        }, 2000);
    }).catch(err => {
        showErrorPopup('클립보드 복사 실패', err, { text: text });
    });
});

// Reset
resetBtn.addEventListener('click', () => {
    // Clear file selection
    selectedFile = null;
    fileInput.value = '';
    window.currentReport = null;

    // Reset drop zone
    const dropZoneH3 = dropZone.querySelector('h3');
    const dropZoneP = dropZone.querySelector('p');
    if (dropZoneH3) dropZoneH3.textContent = '파일 놓기';
    if (dropZoneP) dropZoneP.textContent = '또는 클릭하여 선택';
    dropZone.classList.remove('border-brand-500');

    // Clear coordinate inputs (restore defaults)
    mapUrlInput.value = '';
    latInput.value = '37.5665';
    lonInput.value = '126.9780';

    // Clear address input
    if (addressInput) addressInput.value = '';

    // Clear Job Queue
    clearJobQueue();

    // Hide result panels
    dashboard.classList.add('hidden');
    if (queuePanel) queuePanel.classList.add('hidden');

    // Reset inspector
    fileCount.textContent = '대기 중';
    fileCount.className = 'text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700';
    inspectorBody.innerHTML = `
        <tr>
            <td colspan="16" class="p-12 text-center text-slate-500">
                <div class="flex flex-col items-center justify-center gap-3">
                    <svg class="w-10 h-10 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <p>파일을 업로드하면 메타데이터가 여기에 표시됩니다.</p>
                </div>
            </td>
        </tr>
    `;

    // Reset button state
    const btnText = processBtn.querySelector('span');
    if (btnText) btnText.textContent = '데이터 정규화 시작';
    processBtn.disabled = false;

    console.log('[초기화] 모든 입력값이 초기화되었습니다.');
});

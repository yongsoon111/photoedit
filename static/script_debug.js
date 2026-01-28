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
        alert('Please upload an image or ZIP file.');
        return;
    }
    selectedFile = file;

    // Update Drop Zone UI
    const h3 = dropZone.querySelector('h3');
    const p = dropZone.querySelector('p');
    if (h3) h3.textContent = file.name;
    if (p) p.textContent = 'Analyzing Metadata...';

    // Reset Views
    dashboard.classList.add('hidden');
    inspectorDashboard.classList.add('hidden');
    inspectorBody.innerHTML = '';

    // 1. Analyze Metadata
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/analyze', { method: 'POST', body: formData });
        if (response.ok) {
            const report = await response.json();
            populateInspector(report);
            inspectorDashboard.classList.remove('hidden');
            if (p) p.textContent = 'Analysis Complete. Ready to Normalize.';
        }
    } catch (e) {
        console.error(e);
        if (p) p.textContent = 'Analysis failed.';
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
    fileCount.textContent = `${report.length} files found`;
    inspectorBody.innerHTML = report.map(item => `
        <tr class="hover:bg-slate-700/30 transition-colors group">
            <td class="py-2 pl-2 font-mono text-xs text-slate-300 truncate max-w-[150px]" title="${item.filename}">${item.filename}</td>
            <td class="py-2 text-xs text-slate-400 truncate max-w-[100px]" title="${item.make} ${item.model}">${item.make} ${item.model}</td>
            <td class="py-2 text-xs text-slate-400">${item.datetime}</td>
            <td class="py-2 text-xs font-mono ${item.has_gps ? 'text-red-400 font-bold' : 'text-slate-500'}">
                ${item.has_gps ? 'DETECTED' : 'NONE'}
            </td>
            <td class="py-2 pr-2 text-right">
                <span class="px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${item.is_risky ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'bg-green-500/10 border-green-500/30 text-green-400'}">
                    ${item.is_risky ? 'RISK' : 'SAFE'}
                </span>
            </td>
        </tr>
    `).join('');
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
        console.error('Error fetching location:', error);
    } finally {
        urlSpinner.classList.add('hidden');
    }
}

// Process
processBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('Please upload an image or ZIP first.');
        return;
    }

    const btnText = processBtn.querySelector('span');
    const originalText = btnText ? btnText.textContent : 'Normalize Data';
    if (btnText) btnText.textContent = 'Processing...';
    processBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('lat', latInput.value);
    formData.append('lon', lonInput.value);

    try {
        // Minimum scanning animation time
        const startTime = Date.now();

        const response = await fetch('/normalize', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Processing failed');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        // Handle Metadata (Only for single image headers)
        const metadataHeader = response.headers.get('X-Metadata-Info');
        if (metadataHeader) {
            try {
                const metadata = JSON.parse(metadataHeader);
                console.log("Metadata Injected:", metadata);

                // Populate Location Text
                if (metadata.formatted_coords) {
                    locationText.textContent = metadata.formatted_coords;
                }
                // In a real app we would bind this data to the UI report cards
            } catch (e) {
                console.error("Error parsing metadata header:", e);
            }
        }

        // Wait for animation if needed
        const elapsed = Date.now() - startTime;
        if (elapsed < 1500) {
            await new Promise(r => setTimeout(r, 1500 - elapsed));
        }

        dashboard.classList.remove('hidden');

        // Check if ZIP result
        if (selectedFile.name.endsWith('.zip')) {
            // Replace the previewNormalized element with a custom message for ZIP
            const previewNormalizedParent = previewNormalized.parentElement;
            if (previewNormalizedParent) {
                previewNormalizedParent.innerHTML = `
                    <div class="h-64 flex items-center justify-center bg-slate-800 rounded-lg border border-slate-700">
                        <div class="text-center">
                            <svg class="w-16 h-16 text-brand-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                            <p class="text-brand-300 font-bold">Batch Processing Complete</p>
                            <p class="text-sm text-slate-400">ZIP file ready for download</p>
                        </div>
                    </div>
                `;
            }
            downloadLink.download = `normalized_batch.zip`;
            downloadLink.href = url;
        } else {
            previewNormalized.src = url;
            downloadLink.href = url;
            downloadLink.download = `normalized_${selectedFile.name}`;
        }

        dashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (error) {
        console.error(error);
        alert('An error occurred during processing.');
    } finally {
        if (btnText) btnText.textContent = originalText;
        processBtn.disabled = false;
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
        console.error('Failed to copy: ', err);
    });
});

// Reset
resetBtn.addEventListener('click', () => {
    location.reload(); // Simplest reset for complex state
});

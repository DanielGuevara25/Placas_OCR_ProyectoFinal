const $ = id => document.getElementById(id);
let selectedFile = null, originalURL = null, payload = null, busy = false;
const percent = value => value == null ? '—' : `${(value * 100).toFixed(1)} %`;
function showError(text) { $('error-message').textContent = text; $('error-message').hidden = !text; }
function resetResults() { payload = null; $('results-section').hidden = true; $('preview-toggle').hidden = true; $('plate-list').replaceChildren(); $('dimensions').textContent = ''; }
function setBusy(value) {
  busy = value;
  $('analyze-button').disabled = value || !selectedFile;
  $('declared-plate').disabled = value;
  document.querySelectorAll('.select-plate').forEach(button => { button.disabled = value; });
  $('json-download').disabled = value; $('zip-download').disabled = value;
  document.querySelectorAll('.example-button').forEach(button => {button.disabled = value;});
  $('image-input').disabled = value; $('clear-button').disabled = value; $('confidence').disabled = value;
  $('busy-overlay').hidden = !value;
  $('button-label').textContent = value ? 'Analizando…' : 'Validar placa';
}
function selectFile(file) {
  if (busy || !file) return;
  if (file.size > 12 * 1024 * 1024) { showError('La foto supera 12 MB. Selecciona una más pequeña.'); return; }
  if (file.type && !['image/jpeg', 'image/png', 'image/webp', 'image/bmp', 'image/x-ms-bmp'].includes(file.type)) { showError('Usa una foto JPG, PNG, WEBP o BMP.'); return; }
  if (originalURL) URL.revokeObjectURL(originalURL);
  selectedFile = file; originalURL = URL.createObjectURL(file); showError(''); resetResults();
  $('preview-image').src = originalURL; $('preview-image').hidden = false; $('empty-preview').hidden = true;
  $('preview-image').alt = 'Fotografía seleccionada';
  $('file-info').hidden = false; $('file-name').textContent = file.name; $('file-size').textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB`;
  $('drop-title').textContent = 'Foto seleccionada'; $('drop-subtitle').textContent = 'Haz clic para cambiarla';
  $('preview-caption').textContent = 'Foto lista. Pulsa Validar placa.'; $('analyze-button').disabled = false;
}
$('image-input').addEventListener('change', e => selectFile(e.target.files[0]));
$('drop-zone').addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); if (!busy) $('image-input').click(); } });
for (const event of ['dragenter', 'dragover']) $('drop-zone').addEventListener(event, e => { e.preventDefault(); if (!busy) $('drop-zone').classList.add('drag'); });
for (const event of ['dragleave', 'drop']) $('drop-zone').addEventListener(event, e => { e.preventDefault(); $('drop-zone').classList.remove('drag'); });
$('drop-zone').addEventListener('drop', e => selectFile(e.dataTransfer.files[0]));
$('confidence').addEventListener('input', e => { $('confidence-value').textContent = `${e.target.value} %`; });
$('clear-button').addEventListener('click', () => {
  if (busy) return;
  if (originalURL) URL.revokeObjectURL(originalURL);
  selectedFile = null; originalURL = null; $('image-input').value = ''; $('preview-image').removeAttribute('src');
  $('preview-image').hidden = true; $('empty-preview').hidden = false; $('file-info').hidden = true;
  $('drop-title').textContent = 'Arrastra una foto aquí'; $('drop-subtitle').textContent = 'o haz clic para seleccionarla';
  $('preview-caption').textContent = 'Las placas detectadas se marcarán sobre la fotografía.'; resetResults(); setBusy(false); showError('');
});
function preview(mode) {
  const detected = mode === 'detected';
  $('preview-image').src = detected && payload ? payload.annotated_image : originalURL;
  $('original-button').classList.toggle('active', !detected); $('detected-button').classList.toggle('active', detected);
  $('original-button').setAttribute('aria-pressed', String(!detected)); $('detected-button').setAttribute('aria-pressed', String(detected));
  $('preview-image').alt = detected ? 'Fotografía con placas detectadas y lecturas OCR' : 'Fotografía original';
}
$('original-button').addEventListener('click', () => preview('original'));
$('detected-button').addEventListener('click', () => preview('detected'));
function renderResults(data) {
  payload = data;
  const result = data.result, plates = result.plates;
  const validation = result.validation;
  const titles = {coincide:'Coincidencia de placa', inconsistencia:'Inconsistencia · revisión manual', revision_manual:'Lectura dudosa · revisión manual', sin_placa:'Sin placa · solicita otra foto', seleccion_pendiente:'Selecciona el vehículo inspeccionado'};
  $('validation-title').textContent = titles[validation.status];
  $('validation-message').textContent = validation.message;
  $('validation-detail').textContent = `Placa declarada: ${validation.declared_plate}${validation.selected_plate_id ? ` · Placa seleccionada: ${validation.selected_plate_id}` : ''}`;
  $('validation-summary').dataset.status = validation.status;
  $('results-section').hidden = false; $('preview-toggle').hidden = false; preview('detected');
  $('results-title').textContent = `${plates.length} ${plates.length === 1 ? 'placa detectada' : 'placas detectadas'}`;
  const read = plates.filter(p => p.plate_text).length;
  $('results-subtitle').textContent = `${read} ${read === 1 ? 'lectura obtenida' : 'lecturas obtenidas'} · ${(result.processing_ms / 1000).toFixed(2)} s de procesamiento${result.model_load_ms ? ` · ${(result.model_load_ms / 1000).toFixed(1)} s de carga inicial` : ''}`;
  $('dimensions').textContent = `${result.image_size.width} × ${result.image_size.height} px`;
  $('preview-caption').textContent = 'Los números de cada caja corresponden a los recortes de abajo.';
  $('no-plates').hidden = plates.length !== 0; $('plate-list').replaceChildren();
  plates.forEach((plate, index) => {
    const fragment = $('plate-template').content.cloneNode(true);
    const find = cls => fragment.querySelector(`.${cls}`);
    const choose = find('select-plate');
    choose.hidden = plates.length < 2;
    choose.textContent = validation.selected_plate_id === plate.id ? 'Vehículo seleccionado' : 'Seleccionar este vehículo';
    choose.setAttribute('aria-pressed', String(validation.selected_plate_id === plate.id));
    choose.addEventListener('click', async () => {
      if (busy) return;
      showError(''); setBusy(true);
      try {
        const response = await fetch('/api/select', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({job_id:payload.job_id,selected_plate_id:plate.id})});
        const updated = await response.json();
        if (!response.ok) throw new Error(updated.error || 'No se pudo seleccionar la placa.');
        renderResults(updated);
      } catch(error) {showError(error.message);}
      finally {setBusy(false);}
    });
    find('comparison-text').textContent = plate.validation.message;
    find('plate-index').textContent = `PLACA ${String(plate.id).padStart(2, '0')}`;
    find('reading-status').textContent = plate.ocr_status === 'error' ? 'Error OCR' : (plate.plate_text ? 'Texto reconocido' : 'Sin lectura');
    find('reading-status').classList.toggle('warning', !plate.plate_text);
    find('crop-image').src = data.crops[index]; find('crop-image').alt = `Recorte de placa ${plate.id}`;
    find('plate-text').textContent = plate.plate_text || 'Sin lectura';
    find('detection-confidence').textContent = percent(plate.detection_confidence);
    find('ocr-confidence').textContent = percent(plate.ocr_mean_confidence);
    const button = find('copy-button'); button.disabled = !plate.plate_text;
    button.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(plate.plate_text); button.textContent = 'Copiado'; setTimeout(() => { button.textContent = 'Copiar'; }, 1800); }
      catch { button.textContent = 'Selecciona el texto'; }
    });
    const chars = Array.from(plate.plate_text), list = find('character-list');
    chars.forEach((char, i) => { const item = document.createElement('span'); item.textContent = char; const score = document.createElement('small'); score.textContent = percent(plate.character_confidences[i]); item.append(score); list.append(item); });
    find('characters').hidden = !chars.length;
    if (plate.ocr_error) { find('plate-warning').textContent = plate.ocr_error; find('plate-warning').hidden = false; }
    find('crop-download').href = data.crops[index]; find('crop-download').download = plate.crop_file;
    $('plate-list').append(fragment);
  });
}
$('upload-form').addEventListener('submit', async e => {
  e.preventDefault(); if (!selectedFile || busy) return;
  const declared = $('declared-plate').value.trim();
  if (!/^[A-Z0-9]{2,12}$/.test(declared.toUpperCase().replace(/[\s-]+/g,''))) {showError('Ingresa una placa declarada de 2 a 12 letras o números.'); return;}
  showError(''); resetResults(); $('preview-image').src = originalURL; setBusy(true);
  const form = new FormData(); form.append('image', selectedFile); form.append('declared_plate', declared); form.append('confidence', Number($('confidence').value) / 100);
  try {
    const response = await fetch('/api/detect', { method: 'POST', body: form });
    let data;
    try { data = await response.json(); } catch { throw new Error('El servidor no devolvió una respuesta válida. Revisa la consola.'); }
    if (!response.ok) throw new Error(data.error || 'No se pudo analizar la foto.');
    renderResults(data); $('system-status').textContent = 'Modelos cargados · listos para otra fotografía.';
  } catch (error) { showError(error.message || 'No se pudo conectar con el servidor.'); }
  finally { setBusy(false); }
});
function saveBlob(blob, name) { const url = URL.createObjectURL(blob); const link = document.createElement('a'); link.href = url; link.download = name; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000); }
$('json-download').addEventListener('click', () => { if (payload) saveBlob(new Blob([JSON.stringify(payload.result, null, 2)], { type: 'application/json;charset=utf-8' }), 'resultados.json'); });
$('zip-download').addEventListener('click', () => { if (!payload) return; const bytes = Uint8Array.from(atob(payload.download_zip), c => c.charCodeAt(0)); saveBlob(new Blob([bytes], { type: 'application/zip' }), 'resultados_placas.zip'); });
fetch('/api/status').then(r => r.json()).then(data => {
  if (!data.weights_found) { $('system-status').textContent = 'Falta el modelo entrenado. Revisa su ubicación antes de analizar.'; }
  else { $('system-status').textContent = 'Detector disponible · los modelos se cargarán al analizar.'; }
}).catch(() => { $('system-status').textContent = 'No se pudo comprobar el servidor.'; });

$('declared-plate').addEventListener('input', () => { if (!busy && payload) {resetResults(); $('preview-image').src = originalURL; $('preview-caption').textContent = 'La placa declarada cambió. Vuelve a validar la fotografía.';} });

// Los ejemplos pasan por la misma selección y la misma inferencia que las fotos subidas.
document.querySelectorAll('.example-button').forEach(button => {
  button.addEventListener('click', async () => {
    if (busy) return;
    showError(''); setBusy(true); $('example-status').textContent = 'Cargando fotografía de ejemplo…';
    try {
      const response = await fetch(button.dataset.image);
      if (!response.ok) throw new Error('No se encontró la foto de ejemplo. Copia también static/examples.');
      const blob = await response.blob();
      const file = new File([blob], button.dataset.image.split('/').pop(), {type:blob.type || 'image/png'});
      setBusy(false);
      $('declared-plate').value = button.dataset.plate;
      $('image-input').value = '';
      selectFile(file);
      $('example-status').textContent = 'Ejemplo cargado. Pulsa Validar placa para ejecutar el análisis real.';
      $('upload-form').scrollIntoView({behavior:'smooth',block:'start'});
      $('analyze-button').focus({preventScroll:true});
    } catch(error) {showError(error.message); $('example-status').textContent = 'No se pudo cargar el ejemplo.';}
    finally {setBusy(false);}
  });
});

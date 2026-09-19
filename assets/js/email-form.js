

document.querySelectorAll('[data-email-form]').forEach(form => {
  const status = form.querySelector('[data-form-status]');
  const copy = form.querySelector('[data-copy-message]');
  const preview = form.querySelector('[data-email-preview]');
  function draft() {
    const data = new FormData(form);
    const subject = (data.get('Assunto') || 'Parceria com a GAIA — ' + data.get('Cota')).trim();
    const body = ['Olá, equipe GAIA!', '', 'Nome / organização: ' + data.get('Nome').trim(), 'E-mail para resposta: ' + data.get('Email').trim(), data.has('Cota') ? 'Modalidade de interesse: ' + data.get('Cota') : '', '', data.get('Mensagem').trim()].filter((line, index, lines) => line || index === 1 || lines[index - 1]).join('\n');
    preview.value = 'Para: gaia.robotica.uftm@gmail.com\nAssunto: ' + subject + '\n\n' + body;
    return { subject, body };
  }
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const { subject, body } = draft();
    status.hidden = false;
    status.textContent = 'Seu rascunho está pronto. Se o aplicativo de e-mail abrir, confira a mensagem e confirme o envio por lá. Se ele não abrir, use “Copiar mensagem” e envie para gaia.robotica.uftm@gmail.com.';
    window.location.href = 'mailto:gaia.robotica.uftm@gmail.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  });
  copy.addEventListener('click', async () => {
    if (!form.reportValidity()) return;
    draft();
    status.hidden = false;
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error('clipboard unavailable');
      await navigator.clipboard.writeText(preview.value);
      status.textContent = 'Mensagem copiada. Cole no seu e-mail e envie para gaia.robotica.uftm@gmail.com.';
    } catch {
      preview.hidden = false;
      preview.focus();
      preview.select();
      status.textContent = 'Selecione e copie o texto abaixo. Depois, cole no seu e-mail e envie para gaia.robotica.uftm@gmail.com.';
    }
  });
});

document.querySelectorAll('[data-interest]').forEach(link => link.addEventListener('click', () => {
  const select = document.getElementById('interest');
  select.value = link.dataset.interest;
}));

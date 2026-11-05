(() => {
    // Delegation also handles the new forms returned by the Django view.
    if (window.fitnessChatLoading) return;
    window.fitnessChatLoading = true;
    let activeRequest = null;

    const announce = (message) => {
        let status = document.getElementById('coach-request-status');
        if (!status) {
            status = document.createElement('p');
            status.id = 'coach-request-status';
            status.className = 'fine wrap';
            status.setAttribute('role', 'status');
            document.querySelector('.composer').append(status);
        }
        status.textContent = message;
    };

    document.addEventListener('submit', async (event) => {
        const form = event.target;
        if (!form.matches('.chat form') || form.querySelector('[name="workout_action"]')) return;
        event.preventDefault();
        if (activeRequest) return;

        const payload = new FormData(form);
        if (event.submitter?.name) payload.append(event.submitter.name, event.submitter.value);
        const controller = new AbortController();
        activeRequest = controller;
        const previousFocus = document.activeElement;
        const dialog = document.createElement('dialog');
        dialog.className = 'coach-loading';
        dialog.setAttribute('aria-labelledby', 'coach-loading-title');
        dialog.setAttribute('aria-describedby', 'coach-loading-description');
        dialog.innerHTML = `
            <div class="coach-pulse" aria-hidden="true"><span></span><span></span><span></span></div>
            <h2 id="coach-loading-title">Coach is thinking</h2>
            <p id="coach-loading-description">Putting together an answer for your fitness goals…</p>
            <button type="button" class="btn btn-primary" autofocus>Cancel request</button>`;
        document.body.append(dialog);
        const cancel = () => {
            controller.abort();
            finish();
            announce('Request cancelled. You can edit your question and try again.');
        };
        const finish = () => {
            if (activeRequest !== controller) return;
            activeRequest = null;
            dialog.close();
            dialog.remove();
            if (previousFocus?.isConnected) previousFocus.focus();
        };
        dialog.querySelector('button').addEventListener('click', cancel);
        dialog.addEventListener('cancel', (cancelEvent) => {
            cancelEvent.preventDefault();
            cancel();
        });
        // A modal dialog makes the rest of the document inert, including navigation.
        dialog.showModal();
        try {
            const response = await fetch(form.action || location.href, {
                method: 'POST', body: payload, signal: controller.signal,
                credentials: 'same-origin',
            });
            const html = await response.text();
            if (controller.signal.aborted || activeRequest !== controller) return;
            const page = new DOMParser().parseFromString(html, 'text/html');
            if (!response.ok) {
                throw new Error(page.querySelector('.msg')?.textContent.trim() ||
                    'The coach could not respond. Please try again.');
            }
            if (response.redirected) {
                location.assign(response.url);
                return;
            }
            const nextMain = page.querySelector('main');
            if (!nextMain?.querySelector('.chat')) throw new Error('Unexpected response. Please try again.');
            document.querySelector('main').replaceWith(document.importNode(nextMain, true));
            const thread = document.querySelector('.thread');
            thread.scrollTop = thread.scrollHeight;
            finish();
            document.querySelector('.composer textarea')?.focus();
            announce('Your coach’s response is ready.');
        } catch (error) {
            if (controller.signal.aborted || activeRequest !== controller) return;
            announce(error instanceof TypeError ? 'Connection lost. Please try again.' : error.message);
        } finally {
            finish();
        }
    });
})();

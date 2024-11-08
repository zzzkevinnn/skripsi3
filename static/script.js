function submitForm(event) {
    event.preventDefault();
    startProgress();

    const formData = new FormData(document.getElementById('stock-form'));

    fetch('/process', {
        method: 'POST',
        body: formData
    });
}

function startProgress() {
    var progress = document.getElementById('progress');
    var progressBar = document.getElementById('progress-bar');
    progress.style.width = '0%';
    progress.textContent = '0%';

    var eventSource = new EventSource('/process');

    eventSource.onmessage = function(event) {
        var progress = event.data;
        progressBar.style.width = progress + '%';
        progressBar.textContent = Math.round(progress) + '%';

        if (progress >= 100) {
            eventSource.close();
            window.location.href = "/results";
        }
    };
}

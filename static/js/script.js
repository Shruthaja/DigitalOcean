function startLoadTest() {
    // Show the loader
    document.getElementById('message').innerHTML = '<div class="loader"></div>';

    fetch('/trigger-load')
    .then(response => response.json())
    .then(data => {
        document.getElementById('message').innerText = data.message;
        document.getElementById('message').classList.add('success');
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('message').innerText = 'An error occurred while starting the load test.';
        document.getElementById('message').classList.add('error');
    });
}

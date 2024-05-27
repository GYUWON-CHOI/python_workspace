let abortController = null;

document.querySelectorAll('.read-button').forEach(function(button) {
    button.addEventListener('click', function() {
        if (abortController) {
            abortController.abort(); // 이전 요청 취소
        }
        abortController = new AbortController(); // 새로운 AbortController 생성
        var signal = abortController.signal;
        var summary = this.getAttribute('data-summary');

        fetch('/read-summary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ summary: summary }),
            signal: signal
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            // 여기에 음성을 재생하는 코드 추가
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });
    });
});

document.querySelectorAll('.stop-button').forEach(function(button) {
    button.addEventListener('click', function() {
        if (abortController) {
            abortController.abort(); // 현재 요청 취소
            abortController = null; // AbortController 초기화
        }
    });
});

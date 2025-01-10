document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('stockChart').getContext('2d');

    const stockChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // X축 레이블 (시간)
            datasets: [{
                label: 'Stock Price',
                data: [], // 주식 가격 데이터
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute'
                    }
                }
            }
        }
    });

    // 카프카로부터 실시간 데이터 수신
    const eventSource = new EventSource('/stream');
    eventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);
        stockChart.data.labels.push(data.time);
        stockChart.data.datasets[0].data.push(data.price);
        stockChart.update();
    };

    // 매도, 매수 버튼 클릭 이벤트 처리
    document.getElementById('buyButton').addEventListener('click', () => {
        // 매수 로직 추가
        alert('Buy button clicked');
    });

    document.getElementById('sellButton').addEventListener('click', () => {
        // 매도 로직 추가
        alert('Sell button clicked');
    });
});

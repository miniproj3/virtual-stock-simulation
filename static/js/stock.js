document.addEventListener('DOMContentLoaded', function () {
    fetchStockData();
    setInterval(fetchStockData, 5000);  // 5초마다 데이터 업데이트
});

function fetchStockData() {
    fetch('/stock_kr/get_stock_data')
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                console.log('Stock Data:', data);
                renderStockData(data);
            } else {
                console.error('No valid stock data available');
                alert('주식 데이터를 불러오는 데 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error fetching stock data:', error);
            alert('서버에서 데이터를 가져오는 중 문제가 발생했습니다.');
        });
}

function renderStockData(stockData) {
    const stockListContainer = document.querySelector('tbody');

    if (!stockListContainer) {
        console.error('Stock list container not found');
        return;
    }

    stockListContainer.innerHTML = ''; // 기존 데이터 초기화

    stockData.forEach(stock => {
        const stockRow = document.createElement('tr');

        // 변동률에 따른 클래스 적용
        let changeClass = 'change-percent-0'; // 기본은 0으로 설정
        if (stock.regularMarketChange > 0) {
            changeClass = 'change-percent-positive'; // 상승
        } else if (stock.regularMarketChange < 0) {
            changeClass = 'change-percent-negative'; // 하락
        }

        stockRow.innerHTML = `
            <td>${stock.shortName}</td>
            <td>${stock.regularMarketPrice.toLocaleString()} KRW</td>
            <td class="change ${changeClass}">
                ${stock.regularMarketChange > 0 ? '+' : ''}${stock.regularMarketChange.toLocaleString()} KRW
            </td>
            <td class="change ${changeClass}">
                ${stock.regularMarketChangePercent}
            </td>
        `;

        stockListContainer.appendChild(stockRow);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    socket.on('connected', (data) => {
        console.log(data);
    });

    socket.on('stock_data_update', (stock_data) => {
        const tbody = document.querySelector('tbody');
        tbody.innerHTML = '';
        stock_data.forEach(stock => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${stock.shortName}</td>
                <td>${stock.regularMarketPrice} KRW</td>
                <td class="${stock.regularMarketChange == 0 ? 'change-percent-0' : stock.regularMarketChange > 0 ? 'change-percent-positive' : 'change-percent-negative'}">
                    ${stock.regularMarketChange} KRW
                </td>
                <td class="${stock.regularMarketChangePercent == '0.00' ? 'change-percent-0' : stock.regularMarketChangePercent > 0 ? 'change-percent-positive' : 'change-percent-negative'}">
                    ${stock.regularMarketChangePercent}%
                </td>
            `;
            tbody.appendChild(tr);
        });
    });

    // 데이터를 주기적으로 요청하는 함수
    function requestStockData() {
        socket.emit('request_stock_data');
    }

    // 페이지가 로드된 후 10초마다 데이터를 요청
    setInterval(requestStockData, 10000);

    // 페이지가 처음 로드될 때 데이터를 요청
    requestStockData();
});

document.addEventListener('DOMContentLoaded', function () {
    const symbol = new URLSearchParams(window.location.search).get('symbol');
    if (symbol) {
        fetchStockDetail(symbol);
        setInterval(() => fetchStockDetail(symbol), 5000);  // 5초마다 업데이트
    }
});

function fetchStockDetail(symbol) {
    fetch('/stock_kr/get_stock_data')
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data)) {
                throw new Error('Invalid stock data format: Expected an array');
            }

            const stock = data.find(item => item.symbol === symbol);
            if (stock && stock.history) {
                document.getElementById("stock-name").innerText = stock.shortName;
                document.getElementById("stock-info").innerHTML = `
                    현재 가격: <strong>${stock.regularMarketPrice.toLocaleString()} 원</strong>,
                    변동: <span class="${stock.regularMarketChange > 0 ? 'change-percent-positive' : (stock.regularMarketChange < 0 ? 'change-percent-negative' : 'change-percent-0')}">
                        ${stock.regularMarketChange > 0 ? '+' : ''}${stock.regularMarketChange.toLocaleString()} 원
                    </span>,
                    변동률: <span class="${stock.regularMarketChangePercent > 0 ? 'change-percent-positive' : (stock.regularMarketChangePercent < 0 ? 'change-percent-negative' : 'change-percent-0')}">
                        ${parseFloat(stock.regularMarketChangePercent).toFixed(2)}%
                    </span>
                `;
                initializeChart(stock.history);
            } else {
                console.error('Stock data or history missing for symbol:', symbol);
                alert('Stock data or history missing. Please check');
            }
        })
        .catch(error => {
            console.error('Error fetching stock detail:', error);
        });
}

function initializeChart(history) {
    if (!history || !history.timestamps || !history.prices || !history.volumes) {
        console.error('Invalid chart data');
        return;
    }

    const timestamps = history.timestamps || [];
    const prices = history.prices || [];
    const volumes = history.volumes || [];

    const trace1 = {
        x: timestamps,
        y: prices,
        mode: 'lines+markers',
        name: 'Price',
        line: { color: 'rgb(75, 192, 192)' }
    };

    const trace2 = {
        x: timestamps,
        y: volumes,
        mode: 'lines',
        name: 'Volume',
        yaxis: 'y2',
        line: { color: 'rgb(192, 75, 75)' }
    };

    const layout = {
        title: '주식 가격 및 거래량',
        xaxis: {
            type: 'date',
            title: '시간'
        },
        yaxis: {
            title: '가격'
        },
        yaxis2: {
            title: '거래량',
            overlaying: 'y',
            side: 'right'
        }
    };

    const data = [trace1, trace2];
    Plotly.newPlot('chart', data, layout);
}

setInterval(function () {
    const symbol = new URLSearchParams(window.location.search).get('symbol');
    if (symbol) {
        updateChart(symbol);
    }
}, 10000);  // 10초마다 데이터 업데이트

function updateChart(symbol) {
    fetch('/stock_kr/get_stock_data')
        .then(response => response.json())
        .then(data => {
            const stock = data.find(item => item.symbol === symbol);
            if (stock && stock.history) {
                const timestamps = stock.history.timestamps || [];
                const prices = stock.history.prices || [];
                const volumes = stock.history.volumes || [];

                Plotly.react('chart', [
                    {
                        x: timestamps,
                        y: prices,
                        mode: 'lines+markers',
                        name: 'Price',
                        line: { color: 'rgb(75, 192, 192)' }
                    },
                    {
                        x: timestamps,
                        y: volumes,
                        mode: 'lines',
                        name: 'Volume',
                        yaxis: 'y2',
                        line: { color: 'rgb(192, 75, 75)' }
                    }
                ]);
            } else {
                console.error('Stock data or history missing for symbol:', symbol);
                alert('Stock data or history missing. Please check');
            }
        })
        .catch(error => console.error('Error updating chart data:', error));
}
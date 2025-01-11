document.addEventListener('DOMContentLoaded', function () {
    const symbol = new URLSearchParams(window.location.search).get('symbol');
    console.log("[DEBUG] Stock symbol from URL:", symbol);

    if (!symbol) {
        console.error("[DEBUG] Symbol is missing from the URL.");
        alert("주식 심볼이 URL에 없습니다.");
        return;
    }

    fetchStockDetail(symbol);
    setInterval(() => fetchStockDetail(symbol), 5000); // 5초마다 데이터 갱신
});

async function fetchStockDetail(symbol) {
    console.log("[DEBUG] Fetching stock detail for symbol:", symbol);

    try {
        const response = await fetch(`/stock_kr_detail/api/get_stock_detail?symbol=${symbol}`);
        const data = await response.json();

        if (data.success) {
            console.log("[DEBUG] Stock data received:", data);
            document.getElementById("stock-name").innerText = data.stock.name || "알 수 없음";
            document.getElementById("stock-info").innerHTML = `
                현재 가격: <strong>${data.stock.current_price.toLocaleString()} 원</strong>
            `;
            initializeChart(data.chartData);
        } else {
            console.error("[DEBUG] Error fetching stock data:", data.message);
            alert(data.message || "주식 데이터를 찾을 수 없습니다.");
        }
    } catch (error) {
        console.error("[DEBUG] Error fetching stock detail:", error);
        alert("주식 데이터를 불러오는 중 오류가 발생했습니다.");
    }
}

function initializeChart(chartData) {
    if (!chartData) {
        console.error('[DEBUG] 차트 데이터가 없습니다.');
        return;
    }

    const trace1 = {
        x: chartData.timestamps,
        y: chartData.prices,
        mode: 'lines+markers',
        name: 'Price',
        line: { color: 'rgb(75, 192, 192)' }
    };

    const trace2 = {
        x: chartData.timestamps,
        y: chartData.volumes,
        mode: 'lines',
        name: 'Volume',
        yaxis: 'y2',
        line: { color: 'rgb(192, 75, 75)' }
    };

    const layout = {
        title: '주식 가격 및 거래량',
        xaxis: { type: 'date', title: '시간' },
        yaxis: { title: '가격' },
        yaxis2: { title: '거래량', overlaying: 'y', side: 'right' }
    };

    Plotly.newPlot('chart', [trace1, trace2], layout);
}

async function submitOrder(event, orderType) {
    event.preventDefault();

    if (!userId) {
        alert("로그인이 필요합니다.");
        console.error("[DEBUG] User ID is missing.");
        return;
    }

    const symbol = new URLSearchParams(window.location.search).get('symbol');
    const amount = document.getElementById(orderType === 'BUY' ? 'buy-amount' : 'sell-amount').value;
    const price = document.getElementById(orderType === 'BUY' ? 'buy-price' : 'sell-price').value;

    const data = {
        user_id: userId, // 사용자 ID를 전달
        stock_symbol: symbol,
        order_type: orderType,
        target_price: parseFloat(price),
        quantity: parseInt(amount),
    };

    console.log("[DEBUG] Sending order data:", data);

    try {
        const response = await fetch('/api/order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        if (response.ok) {
            console.log("[DEBUG] Order placed successfully:", result);
            alert(result.message || '주문이 성공적으로 생성되었습니다.');
        } else {
            console.error("[DEBUG] Order submission error:", result.error);
            alert(result.error || '주문 생성 중 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('[DEBUG] Error placing order:', error);
        alert('주문 생성 중 문제가 발생했습니다.');
    }
}

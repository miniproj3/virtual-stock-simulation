// 세션 설정 함수 추가
function sessionSetup() {
    const userId = sessionStorage.getItem('user-id');
    if (!userId) {
        console.error('[DEBUG] 사용자가 로그인되지 않았습니다.');
        alert('로그인이 필요합니다.');
        return false; // 세션이 없으면 false 반환
    }
    console.log('[DEBUG] 세션 설정 완료:', userId);
    return true; // 세션이 유효하면 true 반환
}

// 로그인 성공 시
function onLoginSuccess(user_id) {
    sessionStorage.setItem('user-id', user_id);
    console.log("[DEBUG] 사용자 ID가 세션에 저장됨:", user_id);
}

// DOMContentLoaded 이벤트 리스너
document.addEventListener('DOMContentLoaded', function() {
    const symbol = new URLSearchParams(window.location.search).get('symbol');
    if (symbol) {
        fetchStockDetail(symbol);
        setInterval(() => fetchStockDetail(symbol), 5000);  // 5초마다 데이터 업데이트
    }
});

// 주식 상세 정보를 가져오는 함수
async function fetchStockDetail(symbol) {
    console.log("[DEBUG] Fetching stock detail for symbol:", symbol);

    try {
        const response = await fetch(`/stock_kr/get_stock_data?symbol=${symbol}`);
        const data = await response.json();

        if (!Array.isArray(data)) {
            throw new Error('잘못된 주식 데이터 형식: 배열이 아니네요.');
        }

        const stock = data.find(item => item.symbol === symbol);
        if (stock && stock.history) {
            document.getElementById("stock-name").innerText = stock.shortName;
            document.getElementById("stock-info").innerHTML = `
                현재 가격: <strong>${stock.regularMarketPrice.toLocaleString()} 원</strong> ,
                변동: <span class="${stock.regularMarketChange > 0 ? 'change-percent-positive' : (stock.regularMarketChange < 0 ? 'change-percent-negative' : 'change-percent-0')}">
                    ${stock.regularMarketChange > 0 ? '+' : ''}${stock.regularMarketChange.toLocaleString()} 원
                </span> ,
                변동률: <span class="${stock.regularMarketChangePercent > 0 ? 'change-percent-positive' : (stock.regularMarketChangePercent < 0 ? 'change-percent-negative' : 'change-percent-0')}">
                    ${parseFloat(stock.regularMarketChangePercent).toFixed(2)}%
                </span>
            `;
            initializeChart(stock.history);
        } else {
            console.error('주식 데이터나 역사 기록이 없습니다:', symbol);
            alert('주식 데이터가 없거나 기록이 잘못되었습니다. 다시 확인해주세요.');
        }
    } catch (error) {
        console.error('주식 상세 정보를 가져오는 중 오류 발생:', error);
        alert('주식 상세 정보를 가져오는 데 오류가 발생했습니다. 다시 시도해주세요.');
    }
}

// 차트 초기화 함수
function initializeChart(history) {
    if (!history || !history.timestamps || !history.prices || !history.volumes) {
        console.error('잘못된 차트 데이터');
        return;
    }

    const trace1 = {
        x: history.timestamps,
        y: history.prices,
        mode: 'lines+markers',
        name: 'Price',
        line: { color: 'rgb(75, 192, 192)' }
    };

    const trace2 = {
        x: history.timestamps,
        y: history.volumes,
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

// 주식 데이터 10초마다 업데이트
setInterval(function () {
    const symbol = new URLSearchParams(window.location.search).get('symbol');
    if (symbol) {
        updateChart(symbol);
    }
}, 10000); // 이 문장도 원래 setInterval()의 마지막 부분에 추가해야 합니다.

// 차트 업데이트 함수
function updateChart(symbol) {
    fetch(`/stock_kr/get_stock_data?symbol=${symbol}`)
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
                console.error('주식 데이터나 역사 기록이 없습니다:', symbol);
                alert('주식 데이터가 없거나 기록이 잘못되었습니다. 다시 확인해주세요.');
            }
        })
        .catch(error => console.error('차트 데이터 업데이트 오류:', error));
}

// 주문 처리 함수
async function submitOrder(event, orderType) {
    event.preventDefault();

    if (!sessionSetup()) return;

    const userId = sessionStorage.getItem('user-id');
    const symbol = new URLSearchParams(window.location.search).get('symbol');

    // Price and quantity
    const amountElement = document.getElementById(orderType === 'BUY' ? 'buy-amount' : 'sell-amount');
    const priceElement = document.getElementById(orderType === 'BUY' ? 'buy-price' : 'sell-price');

    const amount = parseInt(amountElement ? amountElement.value : 0);
    const price = parseFloat(priceElement ? priceElement.value : stock.regularMarketPrice);

    console.log("Amount:", amount);
    console.log("Price:", price);

    // Validate data
    if (isNaN(amount) || amount <= 0) {
        alert('유효한 수량을 입력하세요.');
        console.error("[DEBUG] 잘못된 수량 입력:", amount);
        return;
    }

    if (isNaN(price) || price <= 0) {
        alert('유효한 가격을 입력하세요.');
        console.error("[DEBUG] 잘못된 가격 입력:", price);
        return;
    }
    const data = {
        user_id: userId,
        stock_symbol: symbol,
        order_type: orderType,
        target_price: price,
        quantity: amount,
    };
    
    console.log("[DEBUG] 주문 데이터 전송:", data);

    try {
        const response = await fetch('/stock_kr_detail/buy_sell_stock', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        

        if (response.ok) {
            const result = await response.json();
            console.log("[DEBUG] 주문 성공:", result);
            alert(result.message || '주문이 성공적으로 생성되었습니다.');
        } else {
            const result = await response.json();
            console.error("[DEBUG] 주문 생성 오류:", result.error);
            alert(result.error || '주문 생성 중 오류가 발생했습니다.');
        }
    } catch (error) {
        console.error('[DEBUG] 주문 생성 중 오류 발생:', error);
        alert('주문 생성 중 문제가 발생했습니다.');
    }
}

// 차트 초기화 함수의 중복된 정의 삭제
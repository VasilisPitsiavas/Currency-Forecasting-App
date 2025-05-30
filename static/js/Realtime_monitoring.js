document.addEventListener('DOMContentLoaded', () => {
    // List of cryptocurrencies to monitor
    const symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'AVAX', 'MATIC', 'LINK'];
    const currency = 'USD';
    const summaryCardsRow = document.getElementById('summary-cards-row');
    const liveDataTable = document.getElementById('live-data-table');
    let summaryPrices = {};
    let sources = new Map();
    let lastTimestamps = {};

    // Render summary cards
    function renderSummaryCards() {
        summaryCardsRow.innerHTML = '';
        symbols.forEach(symbol => {
            const price = summaryPrices[symbol] || 0;
            summaryCardsRow.innerHTML += `
                <div class="col-md-3 mb-2">
                    <div class="card text-center shadow-sm crypto-card">
                        <div class="card-body">
                            <div class="crypto-symbol">${symbol}</div>
                            <div class="crypto-price" id="summary-${symbol}">${price ? price.toFixed(2) : 'Loading...'}</div>
                            <span class="badge bg-secondary">${currency}</span>
                        </div>
                    </div>
                </div>
            `;
        });
    }

    // Fetch current prices for summary cards
    function fetchSummaryPrices() {
        fetch(`/api/prices?symbols=${symbols.join(',')}&currency=${currency}`)
            .then(response => response.json())
            .then(data => {
                symbols.forEach(symbol => {
                    summaryPrices[symbol] = data[symbol] || 0;
                });
                renderSummaryCards();
            });
    }

    // Update summary card for a symbol
    function updateSummaryCard(symbol, price) {
        summaryPrices[symbol] = price;
        const el = document.getElementById(`summary-${symbol}`);
        if (el) el.textContent = price.toFixed(2);
    }

    // Start monitoring for each symbol
    function startMonitoring() {
        // Clean up previous EventSources
        sources.forEach(source => source.close());
        sources.clear();
        liveDataTable.innerHTML = '';
        lastTimestamps = {};

        symbols.forEach(symbol => {
            const source = new EventSource(`/stream_realtime?symbol=${symbol}&currency=${currency}`);
            sources.set(symbol, source);

            source.onmessage = function (event) {
                const data = JSON.parse(event.data);
                if (data.error) {
                    updateSummaryCard(symbol, 0);
                    return;
                }
                const price = data[currency];
                const time = data.time;
                const prediction = data.prediction !== undefined ? data.prediction.toFixed(2) : 'N/A';
                updateSummaryCard(symbol, price);

                // Only add new row if timestamp is new
                if (lastTimestamps[symbol] !== time) {
                    lastTimestamps[symbol] = time;
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${time}</td>
                        <td>${symbol}</td>
                        <td>${price.toFixed(2)}</td>
                        <td>${prediction}</td>
                    `;
                    liveDataTable.prepend(row);
                    // Limit the table to 40 rows
                    if (liveDataTable.rows.length > 40) {
                        liveDataTable.deleteRow(liveDataTable.rows.length - 1);
                    }
                }
            };

            source.onerror = function () {
                updateSummaryCard(symbol, 0);
            };
        });
    }

    // Initial load
    fetchSummaryPrices();
    renderSummaryCards();
    startMonitoring();
    // Refresh summary prices every 30 seconds
    setInterval(fetchSummaryPrices, 30000);
});

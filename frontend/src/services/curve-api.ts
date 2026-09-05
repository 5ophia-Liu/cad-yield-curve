
async function fetchCurveData(start_date: string, end_date: string) {
    const url = import.meta.env.VITE_API_BASE_URL + '/curve?start_date=' + encodeURIComponent(start_date) + 
    '&end_date=' + encodeURIComponent(end_date);

    const response = await fetch(url)
    // error
    if (!response.ok) {
        throw new Error(`Failed to fetch curve: ${response.status}`);
    }
    
    const data = await response.json();
    // empty
    if (!data || data.dates.length === 0 || data.maturities.length === 0 || data.curves.length === 0) {
        return { dates: [], maturities: [], curves: []};
    }

    return {maturities: data.maturities, curves: data.curves, dates: data.dates};
}

export { fetchCurveData };
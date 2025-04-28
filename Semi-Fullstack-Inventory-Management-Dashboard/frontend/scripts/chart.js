// fetch from internal API
async function fetchChartData() {
  try {
    const response = await fetch('/api/dashboard-chart-data');
    const data = await response.json();
    processChartData(data);
  } catch (error) {
    console.error('Error fetching chart data:', error);
  }
}

// process data
function processChartData(data) {
  const months = getLast12Months(data.charts);

  data.charts.forEach((chartData, index) => {
    const chartContainer = document.getElementById('charts-section');
    
    // create div for each chart
    const chartWrapper = document.createElement('div');
    chartWrapper.style.marginTop = '10px';
    chartWrapper.style.marginBottom = '100px';
    chartWrapper.style.marginLeft = '30px';
    chartWrapper.style.marginRight = '30px';

    // title the chart
    const title = document.createElement('h3');
    title.innerText = chartData.category;
    title.style.color = '#222';  // Optionally, style the title
    chartWrapper.appendChild(title);  // Append the title to the wrapper

    // create new canvas for each chart
    const canvas = document.createElement('canvas');
    canvas.id = `chart${index + 1}`;
    canvas.height = 250;  // set height to 250px
    chartWrapper.appendChild(canvas);  // add canvas to wrapper

    chartContainer.appendChild(chartWrapper);  // add wrapper to container

    const ctx = canvas.getContext('2d');
    const formattedData = formatDataForChart(chartData.data, months);
    createChart(ctx, formattedData, 'Purchase Frequency', 'Usage Frequency', '#afcd6d', '#4289cf', months);
  });
}

// get last 12 months
function getLast12Months(charts) {
  // determine latest month
  const latestMonth = charts.reduce((latest, chart) => {
    const chartMonths = chart.data.map(item => item.month);
    const maxMonth = Math.max(...chartMonths.map(month => {
      const [year, monthStr] = month.split('-');
      const monthNum = parseInt(monthStr, 10) - 1; // 0-based months
      return new Date(year, monthNum).getTime(); // get timestamp
    }));
    return maxMonth > latest ? maxMonth : latest;
  }, 0); // default to 0

  // 12 months from latest month
  const last12Months = [];
  let currentMonth = new Date(latestMonth);

  for (let i = 0; i < 12; i++) {
    last12Months.unshift(currentMonth.toISOString().slice(0, 7)); // yyyy-mm
    currentMonth.setMonth(currentMonth.getMonth() - 1);
  }

  return last12Months;
}


// format data for chart
function formatDataForChart(chartData, months) {
  // get months data
  return months.map(month => {
    const dataForMonth = chartData.find(item => item.month === month);
    return {
      purchased: dataForMonth ? dataForMonth.orders : 0,
      used: dataForMonth ? dataForMonth.usages : 0
    };
  });
}



// make charts
function createChart(ctx, data, label1, label2, color1, color2, months) {
  const formattedMonths = months.map(month => {
    const [year, monthStr] = month.split('-');
    const formattedMonth = new Date(year, parseInt(monthStr, 10) - 1);  // convert to date object
    return `${formattedMonth.toLocaleString('default', { month: 'short' })}-${year.slice(2)}`; // mon-yy
  });


  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: formattedMonths, // months on x-axis
      datasets: [
        {
          label: label1,
          data: data.map(d => d.purchased),
          backgroundColor: color1,
          borderColor: '#222',
          borderWidth: 1,
          fill: false
        },
        {
          label: label2,
          data: data.map(d => d.used),
          backgroundColor: color2,
          borderColor: '#222',
          borderWidth: 1,
          fill: false
        }
      ]
    },
    options: {
      scales: {
        x: {
          ticks: {
            autoSkip: false, // show every month
            maxRotation: 45,
            minRotation: 45,
            color: '#222'  // label color #222 black
          },
          grid: {
            display: true
          }
        },
        y: {
          ticks: {
            stepSize: 1,
            beginAtZero: true,
            color: '#222'
          },
          grid: {
            display: false
          }
        }
      },
      plugins: {
        legend: {
          display: true,
          labels: {
            color: '#222'
          }
        }
      }
    }
  });
}


// main entry
fetchChartData();

import React from 'react';
import { Chart, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'react-chartjs-2';

Chart.register(ArcElement, Tooltip, Legend);

const ChartModule = ({ data }) => {
    const chartData = {
        labels: Object.keys(data),
        datasets: [
            {
                data: Object.values(data),
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40',
                ],
            },
        ],
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    generateLabels: function (chart) {
                        const data = chart.data;
                        if (data.labels.length && data.datasets.length) {
                            return data.labels.map((label, i) => {
                                const value = data.datasets[0].data[i];
                                const backgroundColor = data.datasets[0].backgroundColor[i];
                                return {
                                    text: `${label}: ${new Intl.NumberFormat('en-US').format(value)}`,
                                    fillStyle: backgroundColor,
                                    strokeStyle: backgroundColor,
                                    hidden: false,
                                    index: i,
                                };
                            });
                        }
                        return [];
                    }
                }
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        let label = context.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.raw !== null) {
                            label += new Intl.NumberFormat('en-US', { notation: "compact" }).format(context.raw);
                        }
                        return label;
                    }
                }
            }
        }
    };

    return (
        <div style={{
            position: 'relative',
            height: '25vh',
            width: 'auto',
            margin: '10px auto',
        }}>
            <Pie data={chartData} options={options} />
            <style jsx>{`
              @media (max-width: 845px) {
                div {
                  width: 100%;
                  height: auto;
                }
              }
              .chart-legend-text {
                font-size: 2rem; /* Большой текст на больших экранах */
              }

              @media (max-width: 845px) {
                .chart-legend-text {
                  font-size: 1rem; /* Меньший текст на мобильных устройствах */
                }
              }
            `}</style>
        </div>
    );
};

export default ChartModule;

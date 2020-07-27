"use strict";
var chartDefOpt = Chart.defaults.global;
if ('matchMedia' in window && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    chartDefOpt.defaultFontColor = "#ccc";
    chartDefOpt.elements.arc.borderColor = "#141010";
    Chart.defaults.line.scales.xAxes[0].gridLines = { color: '#fff2' };
    Chart.defaults.line.scales.yAxes[0].gridLines = { color: '#fff2' };
}
var cpu_count = logs[0].cpus_load.split(",").length;
var charts = {};
var yAxisOptions = {};

charts.loadavg = [{
    label: '5 minute load average',
    borderColor: "#f003",
    backgroundColor: "#f003",
    data: []
}];

charts.cpu_load = []
yAxisOptions.cpu_load = []
function cpu_color(i) {
    return "hsla(" + (i * 40) + ",100%,50%,0.5)"
}
for (let i = 0; i < cpu_count; i++)
    charts['cpu_load'].push({
        label: "CPU"+i+"%",
        borderColor: cpu_color(i),
        data: []
    });
    yAxisOptions.cpu_load.push({
        ticks: {
            beginAtZero: true,
            max: 100
        }
    });

charts['memory_usage'] = [{
    label: 'MiB',
    borderColor: "#f0f3",
    backgroundColor: "#f0f3",
    data: []
}];
yAxisOptions.memory_usage = [{
    ticks: {
        beginAtZero: true,
        max: sessionInfo.total_virt_mem
    }
}];

charts.disk_usage = [{
    label: 'MiB',
    borderColor: "#0f03",
    backgroundColor: "#0f03",
    data: []
}];
yAxisOptions.disk_usage = [{
    ticks: {
        beginAtZero: true,
        max: sessionInfo.total_disk_space
    }
}];

charts.network_usage = [{
    label: 'Sent MiB',
    fill: false,
    borderColor: "#00f3",
    backgroundColor: "#00f3",
    borderDash: [5, 5],
    data: []
}, {
    label: 'Receive MiB',
    fill: false,
    borderColor: "#00f3",
    backgroundColor: "#00f3",
    data: []
}];

if (sessionInfo.total_gpu_mem != null) {
    charts.gpu_load = [{
        label: 'Load %',
        borderColor: "#0ff3",
        backgroundColor: "#0ff3",
        data: []
    }];
    yAxisOptions.gpu_load = [{
        ticks: {
            beginAtZero: true,
            max: 100
        }
    }];

    charts.gpu_memory = [{
        label: 'MiB',
        borderColor: "#0ff3",
        backgroundColor: "#0ff3",
        data: []
    }];
    yAxisOptions.gpu_memory = [{
        ticks: {
            beginAtZero: true,
            max: sessionInfo.total_gpu_mem
        }
    }];
}

if (sessionInfo.tpu_type != null) {
    charts.tpu_mxu = [{
        label: 'Matrix Unit Utilization %',
        borderColor: "#0093",
        backgroundColor: "#0093",
        data: []
    }];
    yAxisOptions.tpu_mxu = [{
        ticks: {
            beginAtZero: true,
            max: 100
        }
    }];

    charts.tpu_idle = [{
        label: 'Idle Time %',
        borderColor: "#0093",
        backgroundColor: "#0093",
        data: []
    }];
    yAxisOptions.tpu_idle = [{
        ticks: {
            beginAtZero: true,
            max: 100
        }
    }];
}

var timestamps = [];
function line_chart_config(data, yAxesConfig = {}) {
    return {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: data
        },
        options: {
            scales: {
                xAxes: [{
                    display: false
                }],
                yAxes: yAxesConfig
            }
        }
    };
}
logs.reverse();
logs.forEach(function(log) {
    timestamps.push(log.time);
    charts.loadavg[0].data.push(log["5m_loadavg"]);
    log.cpus_load.split(",").forEach(function(cpu_load, index) {
        charts.cpu_load[index].data.push(cpu_load);
    });
    charts.memory_usage[0].data.push((log.virt_mem * sessionInfo.total_virt_mem).toFixed(2));
    charts.disk_usage[0].data.push((log.disk_usage * sessionInfo.total_disk_space).toFixed(2));
    charts.network_usage[0].data.push(log.net_sent);
    charts.network_usage[1].data.push(log.net_recv);
    if (sessionInfo.total_gpu_mem != null) {
        charts.gpu_load[0].data.push(log.gpu_load);
        charts.gpu_memory[0].data.push((log.gpu_mem * sessionInfo.total_gpu_mem).toFixed(2));
    }
    if (sessionInfo.tpu_type != null) {
        charts.tpu_mxu[0].data.push(log.tpu_mxu);
        charts.tpu_idle[0].data.push(log.tpu_idle);
    }
});
document.querySelectorAll("canvas").forEach(function(el) {
    charts[el.id]['chart'] = new Chart(el, line_chart_config(charts[el.id], yAxisOptions[el.id]));
});

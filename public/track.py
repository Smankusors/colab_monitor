import os
import requests
import subprocess
import sys
from threading import Thread
from time import sleep
subprocess.check_call([sys.executable, "-m", "pip", "install", "gputil", "psutil", "--upgrade"])
import GPUtil
import psutil

class ColabMonitor():
    def update(self):
        try:
            gpu = GPUtil.getGPUs()[0]
        except:
            gpu = None
        loadavg = psutil.getloadavg()[1]
        #disk_counter = psutil.disk_io_counters()
        net_counter = psutil.net_io_counters()
        payload = {
            '5m_loadavg': loadavg,
            'cpus_load[]': psutil.cpu_percent(percpu=True),
            'virt_mem': psutil.virtual_memory().percent / 100,
            'disk_usage': psutil.disk_usage(self.cwd).percent / 100,
            #'disk-counter': [disk_counter.read_bytes, disk_counter.write_bytes],
            'net_sent': (net_counter.bytes_sent - self._last_bytes_sent) / 1048576,
            'net_recv': (net_counter.bytes_recv - self._last_bytes_recv) / 1048576
        }
        self._last_bytes_sent = net_counter.bytes_sent
        self._last_bytes_recv = net_counter.bytes_recv
        if gpu is not None:
            payload['gpu_load'] = gpu.load * 100
            payload['gpu_mem'] = gpu.memoryUtil
        if self.tpu is not None:
            payload['tpu_idle'] = self.tpu.idle
            payload['tpu_mxu'] = self.tpu.mxu
        payload['_token'] = self.token
        self._response = requests.post(
            self.post_url,
            headers={'Host':'colab-monitor.smankusors.com'},
            data=payload
        )
        if self._response.status_code != 200:
            raise Exception("Something wrong happened. Status code: {}".format(self._response.status_code))

    def __init__(self, tpu=None):
        self.cwd = os.getcwd()
        payload = {}
        payload['total_virt_mem'] = psutil.virtual_memory().total / 1048576
        try:
            gpu = GPUtil.getGPUs()[0]
            payload['total_gpu_mem'] = gpu.memoryTotal
            payload['gpu_name'] = gpu.name
        except:
            pass
        if tpu is None:
            self.tpu = None
        else:
            self.tpu = self.Tensorflow_TPUMonitor(tpu, self)
            payload['tpu_type'] = self.tpu.type_n_cores
        payload['total_disk_space'] = psutil.disk_usage(self.cwd).total / 1048576
        net_counter = psutil.net_io_counters()
        self._last_bytes_sent = net_counter.bytes_sent
        self._last_bytes_recv = net_counter.bytes_recv
        self._response = requests.post(
            'http://185.224.137.80',
            headers={'Host':'colab-monitor.smankusors.com'},
            data=payload
        )
        if self._response.status_code != 200:
            raise Exception('Failed to add new session! Status code: {}'.format(self._response.status_code))
        self.id, self.token = self._response.text.split(",")
        self.post_url = "http://185.224.137.80/" + self.id
        self._interval = 60

    def loop(self):
        while self._isLooping:
            self.update()
            sleep(self._interval)

    def start(self):
        thread = Thread(target=self.loop)
        self._isLooping = True
        thread.start()
        if self.tpu is not None:
            thread = Thread(target=self.tpu.loop)
            thread.start()
        print("Now live at : http://colab-monitor.smankusors.com/" + self.id)
        return self

    def setInterval(self, interval_s):
        self._interval = interval_s
        return self

    def stop(self):
        self._isLooping = False
        return self

    class Tensorflow_TPUMonitor():
        def __init__(self, tpu, colabMonitor):
            service_addr = tpu.get_master()
            self.service_addr = service_addr.replace('grpc://', '').replace(':8470', ':8466')
            from tensorflow.python.profiler.internal import _pywrap_profiler
            self.monitor = _pywrap_profiler.monitor
            self.colabMonitor = colabMonitor
            self.mxu = 0
            self.idle = 100
            ret = self.monitor(self.service_addr, 1, 2, False)
            for line in ret.strip().split("\n"):
                if line.startswith("TPU type:"):
                    self.type_n_cores = line[10:] + "-" + str(tpu.num_accelerators()['TPU'])
                    break

        def loop(self):
            while self.colabMonitor._isLooping:
                self.update()

        def update(self):
            ret = self.monitor(self.service_addr, self.colabMonitor._interval, 2, False)
            self.idle = 100
            for line in ret.split("\n"):
                line = line.strip()
                if line.startswith("TPU idle time"):
                    self.idle = line[33:-1]
                elif line.startswith("Utilization of"):
                    self.mxu = line[52:-1]

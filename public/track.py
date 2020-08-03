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
    _interval = 60
    _isLooping = False
    tpu = None
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
            payload['tpu_idle'] = self.tpu.idle.value
            payload['tpu_mxu'] = self.tpu.mxu.value
        payload['_token'] = self.token
        self._response = requests.post(
            self.post_url,
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
        if tpu is not None:
            self.tpu = self.Tensorflow_TPUMonitor(tpu, self)
            payload['tpu_type'] = self.tpu.type_n_cores
        payload['total_disk_space'] = psutil.disk_usage(self.cwd).total / 1048576
        net_counter = psutil.net_io_counters()
        self._last_bytes_sent = net_counter.bytes_sent
        self._last_bytes_recv = net_counter.bytes_recv
        self._response = requests.post(
            'http://colab-monitor.smankusors.com',
            data=payload
        )
        if self._response.status_code != 200:
            raise Exception('Failed to add new session! Status code: {}'.format(self._response.status_code))
        self.id, self.token = self._response.text.split(",")
        self.post_url = "http://colab-monitor.smankusors.com/" + self.id
        print("Now live at : " + self.post_url)

    def loop(self):
        while self._isLooping:
            self.update()
            sleep(self._interval)

    def start(self):
        if (self._isLooping):
            raise Exception("Monitoring already started!")
        thread = Thread(target=self.loop)
        self._isLooping = True
        thread.start()
        if self.tpu is not None:
            self.tpu.start()
        return self

    def setInterval(self, interval_s):
        self._interval = interval_s
        return self

    def stop(self):
        self._isLooping = False
        if self.tpu is not None:
            self.tpu.stop()
        return self

    class Tensorflow_TPUMonitor():
        def __init__(self, tpu, colabMonitor):
            from tensorflow.python.profiler.internal import _pywrap_profiler
            from multiprocessing import Value
            service_addr = tpu.get_master()
            self.service_addr = service_addr.replace('grpc://', '').replace(':8470', ':8466')
            self.monitor = _pywrap_profiler.monitor
            self.colabMonitor = colabMonitor
            self.mxu = Value('d', 0)
            self.idle = Value('d', 100)
            ret = self.monitor(self.service_addr, 1, 2, False)
            for line in ret.strip().split("\n"):
                if line.startswith("TPU type:"):
                    self.type_n_cores = line[10:] + "-" + str(tpu.num_accelerators()['TPU'])
                    break
            self.exit_loop = None

        def start(self):
            if self.exit_loop is not None and not self.exit_loop.is_set():
                raise Exception("TPU monitoring already started")
            from multiprocessing import Event, Process
            self.exit_loop = Event()
            self.process_loop = Process(target=self.loop)
            self.process_loop.start()

        def loop(self):
            while not self.exit_loop.is_set():
                self.update(self.colabMonitor._interval - 1)
                sleep(1)

        def update(self, interval_s):
            ret = self.monitor(self.service_addr, interval_s * 1000, 2, False)
            self.idle.value = 100
            for line in ret.split("\n"):
                line = line.strip()
                if line.startswith("TPU idle time"):
                    self.idle.value = float(line[33:-1])
                elif line.startswith("Utilization of"):
                    self.mxu.value = float(line[52:-1])

        def stop(self):
            self.exit_loop.set()
            self.process_loop.join()

import os
import psutil
import requests
import subprocess
import sys
from threading import Thread
from time import sleep
subprocess.check_call([sys.executable, "-m", "pip", "install", "gputil", "psutil", "--upgrade"])
import GPUtil

class ColabMonitor():
  def update(self):
    try:
      gpu = GPUtil.getGPUs()[0]
    except:
      gpu = None
    loadavg = os.getloadavg()[1]
    #disk_counter = psutil.disk_io_counters()
    net_counter = psutil.net_io_counters()
    payload = {
      '5m_loadavg': loadavg,
      'cpus_load[]': psutil.cpu_percent(percpu=True),
      'virt_mem': psutil.virtual_memory().percent / 100,
      'disk_usage': psutil.disk_usage('/').percent / 100,
      #'disk-counter': [disk_counter.read_bytes, disk_counter.write_bytes],
      'net_sent': net_counter.bytes_sent / 1024,
      'net_recv': net_counter.bytes_recv / 1024
    }
    if gpu is not None:
      payload['gpu_load'] = gpu.load * 100
      payload['gpu_mem'] = gpu.memoryUtil
    payload['_token'] = self.token
    self._response = requests.post(self.post_url,
                  headers={'Host':'colab-monitor.smankusors.com'},
                  data=payload)
    if self._response.status_code != 200:
      raise Exception("Something wrong happened. Status code: {}".format(self._response.status_code))

  def __init__(self):
    payload = {}
    payload['total_virt_mem'] = psutil.virtual_memory().total / 1048576
    try:
      gpu = GPUtil.getGPUs()[0]
      payload['total_gpu_mem'] = gpu.memoryTotal
      payload['gpu_name'] = gpu.name
    except:
      pass
    payload['total_disk_space'] = psutil.disk_usage('/').total / 1048576
    self._response = requests.post('http://185.224.137.80',
                  headers={'Host':'colab-monitor.smankusors.com'},
                  data=payload)
    if self._response.status_code != 200:
      raise Exception('Failed to add new session! Status code: {}'.format(self._response.status_code))
    self.id, self.token = self._response.text.split(",")
    self.post_url = "http://185.224.137.80/" + self.id
    print("Now live at : " + self.post_url)

  def loop(self):
    while True:
      self.update()
      sleep(3)

  def start(self):
    thread = Thread(target=self.loop)
    thread.start()
    return self

_colabMonitor = ColabMonitor().start()

import psutil
import threading
import time
import collections

# Needs adjustement!!!
class PerformanceMonitor:
    def __init__(self, sample_interval=1.0):  
        self.sample_interval = sample_interval
        self.cpu_usage = 0.0
        self.running = True

        # eep track of last **5 readings** for better stabilization
        self.cpu_history = collections.deque(maxlen=5)

        self.thread = threading.Thread(target=self._update_cpu_usage, daemon=True)
        self.thread.start()

    def _update_cpu_usage(self):
        while self.running:
            try:
                raw_cpu = psutil.cpu_percent(interval=0.3)  # faster updates
                self.cpu_history.append(raw_cpu)

                # compute a weighted moving average
                self.cpu_usage = sum(self.cpu_history) / len(self.cpu_history)

                print(f"DEBUG: Raw CPU: {raw_cpu:.2f}%, Smoothed: {self.cpu_usage:.2f}%")

            except Exception as e:
                print(f"Error measuring CPU usage: {e}")

            time.sleep(self.sample_interval)

    def get_cpu_usage(self):
        return round(self.cpu_usage, 2)

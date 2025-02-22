import numpy as np
from collections import deque
from datetime import datetime

class CorrelationMonitor:
    def __init__(self, window_size=10, correlation_threshold=0.5):
        """
        Initialize the correlation-based monitor
        window_size: minutes of data to consider
        correlation_threshold: minimum correlation required between heart rate and steps
        """
        self.window_size = window_size
        self.correlation_threshold = correlation_threshold
        self.heart_rates = deque(maxlen=window_size)
        self.step_counts = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
        
    def normalize_deltas(self, data):
        """Normalize deltas to range [0,1]"""
        deltas = np.diff(data)
        if len(deltas) == 0 or np.all(deltas == 0):
            return np.zeros(len(data) - 1)
            
        return (deltas - np.min(deltas)) / (np.max(deltas) - np.min(deltas) + 1e-10)
        
    def add_reading(self, heart_rate, step_count):
        """Add a new reading to the monitoring window"""
        self.heart_rates.append(heart_rate)
        self.step_counts.append(step_count)
        self.timestamps.append(datetime.now())
        
    def detect_anomaly(self):
        """
        Detect anomalies based on correlation between normalized deltas
        Returns: bool indicating if current state is anomalous, correlation value
        """
        if len(self.heart_rates) < 3:  # Need at least 3 points to establish a pattern
            return False, 0
            
        # Calculate normalized deltas
        norm_hr_deltas = self.normalize_deltas(list(self.heart_rates))
        norm_step_deltas = self.normalize_deltas(list(self.step_counts))
        
        # Calculate correlation between recent changes
        correlation = np.corrcoef(norm_hr_deltas, norm_step_deltas)[0,1]
        
        # Check if correlation is too low (indicating heart rate changes not explained by activity)
        is_anomalous = abs(correlation) < self.correlation_threshold
        
        return is_anomalous, correlation
        
    def get_alert_details(self):
        """Get detailed information about the current state"""
        is_anomalous, correlation = self.detect_anomaly()
        
        return {
            'current_heart_rate': self.heart_rates[-1],
            'heart_rate_change': self.heart_rates[-1] - self.heart_rates[-2],
            'current_steps': self.step_counts[-1],
            'step_change': self.step_counts[-1] - self.step_counts[-2],
            'correlation': correlation,
            'timestamp': self.timestamps[-1]
        }

# Example usage
def simulate_monitoring():
    monitor = CorrelationMonitor(window_size=10, correlation_threshold=0.5)
    
    # Simulate correlated activity (normal exercise)
    normal_hr = [70, 75, 85, 90, 95]  # Gradually increasing heart rate
    normal_steps = [0, 20, 50, 80, 100]  # Corresponding increase in steps
    
    # Simulate uncorrelated activity (potential health issue)
    anomaly_hr = [70, 90, 140, 150,100]  # Sudden heart rate spike
    anomaly_steps = [0, 5, 10, 12, 15]  # Minimal activity
    
    print("Testing normal exercise pattern:")
    for hr, steps in zip(normal_hr, normal_steps):
        monitor = CorrelationMonitor(window_size=10)
        for i in range(len(normal_hr)):
            monitor.add_reading(normal_hr[i], normal_steps[i])
        is_anomalous, correlation = monitor.detect_anomaly()
        if is_anomalous:
            print("Alert! Anomaly detected:")
            print(monitor.get_alert_details())
        else:
            print(f"Normal activity detected. Correlation: {correlation:.2f}")
            
    print("\nTesting anomalous pattern:")
    for hr, steps in zip(anomaly_hr, anomaly_steps):
        monitor = CorrelationMonitor(window_size=10)
        for i in range(len(anomaly_hr)):
            monitor.add_reading(anomaly_hr[i], anomaly_steps[i])
        is_anomalous, correlation = monitor.detect_anomaly()
        if is_anomalous:
            print("Alert! Anomaly detected:")
            print(monitor.get_alert_details())
        else:
            print(f"Normal activity detected. Correlation: {correlation:.2f}")

if __name__ == "__main__":
    simulate_monitoring()
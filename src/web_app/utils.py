import psutil

def adjust_resources():
    for proc in psutil.process_iter(['pid','cpu_percent']):
        try:
            if proc.info['cpu_percent'] > 20:
                proc.nice(-5)
            else:
                proc.nice(5)
        except:
            pass
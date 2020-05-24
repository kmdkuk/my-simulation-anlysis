import matplotlib.pyplot as plt
import numpy as np
import math


def get_service_name(lines):
    s_l = [s.strip() for s in lines]
    service_names = []
    for l in s_l:
        line = l.split(' ')
        service_names.append(line[5])
    return [x for x in set(service_names) if service_names.count(x) > 1]


def get_join_client(lines, service_name):
    ips = []

    return ips


file_name = 'log-100_latency.log'

# log[lines][count]


def get_max_time(time):
    return max(time)


def summarize_time(time, latency):
    count = int(math.floor(get_max_time(time) / 1_000_000))
    print("count:", count)
    summarized_time = np.arange(count)
    summarized_latency = np.empty(count)
    for i in summarized_time:
        time_seconds = i * 1_000_000
        print(i)
        applicable_latency = latency[(
            (time >= time_seconds) & (time < (time_seconds + 1_000_000)))]
        print(applicable_latency)
        if (len(applicable_latency) == 0):
            summarized_latency[i] = 0
            continue
        print("here")
        summarized_latency[i] = sum(
            applicable_latency) / len(applicable_latency)
    return (summarized_time, summarized_latency)

# 指定したサービスのログを抜き出す


def get_log(log, service_name):
    time = []
    latency = []
    for l in log:
        if l[5] == service_name:
            time.append(float(l[8]))
            latency.append(float(l[10]))
    return (np.array(time), np.array(latency))


# log[servicename][count][0] = time
# log[servicename][count][1] = latency
log_time = {}
log_latency = {}
service_names = []
with open(file_name) as f:
    lines = f.readlines()
    service_names = get_service_name(lines)
    log = [s.strip().split(' ') for s in lines]
    for s in service_names:
        log_time[s], log_latency[s] = get_log(log, s)

for service_name in service_names:
    x, y = summarize_time(log_time[service_name], log_latency[service_name])
    # プロット
    plt.plot(x, y, label=service_name)


# 凡例の表示
plt.legend()

# ラベル名
plt.ylabel('Service RTT (ms)')
plt.xlabel('elapsed time (s)')

# プロット表示(設定の反映)
plt.show()

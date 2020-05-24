import matplotlib.pyplot as plt
import numpy as np
import math
import os
from enum import IntEnum


class LogColum(IntEnum):
    ELAPSED = 0
    NODE_NUM = 1
    FUNCTION = 2
    INFO = 3
    INFO_ = 4
    SERVICE_NAME = 5
    SERVER_IP = 6
    CLIENT_IP = 7
    NOW_TIME = 8
    SENT_TIME = 9
    LATENCY = 10


def get_service_name(lines):
    s_l = [s.strip() for s in lines]
    service_names = []
    for l in s_l:
        line = l.split(' ')
        service_names.append(line[LogColum.SERVICE_NAME])
    return [x for x in set(service_names) if service_names.count(x) > 1]


def get_join_ips(lines, service_name):
    s_l = [s.strip() for s in lines]
    ips = []
    for l in s_l:
        line = l.split(' ')
        if (service_name == line[LogColum.SERVICE_NAME]):
            ips.append(line[LogColum.CLIENT_IP])
    return [ip for ip in set(ips) if ips.count(ip) > 1]

# log[lines][count]


def get_max_time(time):
    return max(time)


def latency(time, latency):
    order = 1_000_000
    count = int(math.floor(get_max_time(time) / order))
    summarized_time = np.arange(count)
    summarized_latency = np.empty(count)
    for i in summarized_time:
        time_seconds = i * order
        applicable_latency = latency[(
            (time >= time_seconds) & (time < (time_seconds + order)))]
        if (len(applicable_latency) == 0):
            summarized_latency[i] = 0
            continue
        summarized_latency[i] = sum(
            applicable_latency) / len(applicable_latency)
    return (summarized_time, summarized_latency)


def variance(time, latency):
    order = 1_000_000
    count = int(math.floor(get_max_time(time) / order))
    summarized_time = np.arange(count)
    summarized_variance = np.empty(count)
    for i in summarized_time:
        time_seconds = i * order
        applicable_latency = latency[(
            (time >= time_seconds) & (time < (time_seconds + order)))]
        if (len(applicable_latency) == 0):
            summarized_variance[i] = 0
            continue
        ave = sum(
            applicable_latency) / len(applicable_latency)
        squared_diff = [(i - ave) ** 2 for i in applicable_latency]
        summarized_variance[i] = sum(squared_diff) / len(squared_diff)
    return (summarized_time, summarized_variance)

# 指定したサービスのログを抜き出す


def get_log(log, service_name):
    time = []
    latency = []
    for l in log:
        if l[LogColum.SERVICE_NAME] == service_name:
            time.append(float(l[LogColum.NOW_TIME]))
            latency.append(float(l[LogColum.LATENCY]))
    # latencyがμ秒なのでm秒に治す．
    order = 1_000
    return (np.array(time), np.array(latency)/order)


def get_log_with_ip(log, service_name, ip):
    # return log_time["service_name"]["ip"]
    # return log_latency["service_name"]["ip"]
    time = []
    latency = []
    for l in log:
        if l[LogColum.SERVICE_NAME] == service_name and l[LogColum.CLIENT_IP] == ip:
            time.append(float(l[LogColum.NOW_TIME]))
            latency.append(float(l[LogColum.LATENCY]))
    # latencyがμ秒なのでm秒に治す．
    order = 1_000
    return (np.array(time), np.array(latency)/order)


def load_file(file_name):
    path = file_name + '.log'
    log_time = {}
    log_latency = {}
    service_names = []
    with open(path) as f:
        lines = f.readlines()
        service_names = get_service_name(lines)
        log = [s.strip().split(' ') for s in lines]
        for s in service_names:
            log_time[s], log_latency[s] = get_log(log, s)
    return service_names, log_time, log_latency


def load_file_with_ip(file_name):
    path = file_name + '.log'
    # log_time["service_name"]["ip"]
    # log_latency["service_name"]["ip"]
    log_time = {}
    log_latency = {}
    service_names = []
    # join_ips[service_name] = []
    join_ips = {}
    with open(path) as f:
        lines = f.readlines()
        service_names = get_service_name(lines)
        log = [s.strip().split(' ') for s in lines]
        for s in service_names:
            log_time[s] = {}
            log_latency[s] = {}
            join_ips[s] = get_join_ips(lines, s)
            for ip in join_ips[s]:
                log_time[s][ip], log_latency[s][ip] = get_log_with_ip(
                    log, s, ip)
    return service_names, join_ips, log_time, log_latency


def plot_std(file_name):
    # log[servicename][count][0] = time
    # log[servicename][count][1] = latency
    service_names, log_time, log_latency = load_file(file_name)
    for service_name in service_names:
        x, y = variance(log_time[service_name], log_latency[service_name])
        y = y**0.5
        # プロット
        plt.plot(x, y, label=service_name)

    # 凡例の表示
    plt.legend()

    # ラベル名
    plt.ylabel('Latency standard deviation (ms)')
    plt.xlabel('elapsed time (s)')

    makedir(file_name)
    # プロット表示(設定の反映)
    plt.savefig('figure/'+file_name + '/std.png')
    plt.clf()
    return


def plot_latency(file_name):
    # log[servicename][count][0] = time
    # log[servicename][count][1] = latency
    service_names, log_time, log_latency = load_file(file_name)
    for service_name in service_names:
        x, y = latency(log_time[service_name], log_latency[service_name])
        # プロット
        plt.plot(x, y, label=service_name)

    # 凡例の表示
    plt.legend()

    # ラベル名
    plt.ylabel('Service RTT (ms)')
    plt.xlabel('elapsed time (s)')

    makedir(file_name)
    # プロット表示(設定の反映)
    plt.savefig('figure/'+file_name + '/latency.png')
    plt.clf()
    return


def plot_ip_latency(file_name):
    # log_time[service_name][ip]
    # log_latency[service_name][ip]
    service_names, join_ips, log_time, log_latency = load_file_with_ip(
        file_name)
    for service_name in service_names:
        for join_ip in join_ips[service_name]:
            x, y = latency(log_time[service_name][join_ip],
                           log_latency[service_name][join_ip])
            plt.plot(x, y, label=join_ip)
        # 凡例の表示
        plt.legend()

        plt.title(service_name+'s latency')

        # ラベル名
        plt.ylabel('Service RTT (ms)')
        plt.xlabel('elapsed time (s)')

        makedir(file_name)
        # プロット表示(設定の反映)
        plt.savefig('figure/'+file_name + '/'+service_name+'_latency.png')
        plt.clf()
    return


def makedir(file_name):
    os.makedirs('figure/'+file_name, exist_ok=True)
    return


file_name = 'log-100_latency'
plot_latency(file_name)
plot_ip_latency(file_name)
plot_std(file_name)

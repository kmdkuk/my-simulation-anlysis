file_name = 'log-100'
path = file_name+'.log'

latency_log = file_name + '_latency.log'
other_log = file_name + '_others.log'

latency_file = open(latency_log, mode='w')
other_file = open(other_log, mode='w')

with open(path) as f:
    lines = [s.strip() for s in f.readlines()]
    print(lines)
    for l in lines:
        s_l = l.split(' ')
        if s_l[2] == "KmdEchoClientApplication:HandleRead():":
            latency_file.write(l+'\n')
        else:
            other_file.write(l+'\n')


latency_file.close()
other_file.close()

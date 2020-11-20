# 20.11.2020 initial version
#
# read winscp logfile (debug mode), create summary and "readable" log

# variables
winscp_file = r'c:\anywhere'
winscp_result = r'c:\anywhere'
winscp_find = ['Command-line', 'Script: Failed']
winscp_raw = []
winscp_detail = {}

# read calls and steps to list
with open(winscp_file, 'r') as rawfile:
    for line in rawfile:
        line = line.replace('\n','')
        for item in winscp_find:
            if line.find(item) is not -1:
                winscp_raw.append(line)
        if line.startswith(('!','>','<')):
            winscp_raw.append(line)
        else:
            continue

# create dict of calls and collect indices for further handling
# structure of dict: key=number, value=list of values
#                    list: timestamp, partner, job, idx command, idx stop

counter = 1
for line in winscp_raw:
    date = line.split(' ', 3)[1]
    time = line.split(' ', 3)[2]
    timestamp = date + ' ' + time
    if 'Command-line' in line:
        winscp_detail[counter] = []
        winscp_detail[counter].append(timestamp)
        partner = line.split(' ')[5].split('\\')[-1].replace('.ppk','')
        winscp_detail[counter].append(partner)
        job = line.split(' ')[17:]
        job = ' '.join(job)
        job = job.split('\"')[1].replace('call ','').lstrip()
        winscp_detail[counter].append(job)
        idx_command = str(winscp_raw.index(line))
        winscp_detail[counter].append(idx_command)
        counter += 1

# get next index from next entry in winscp_detail and enhance value in winscp_detail
stop_flag = len(winscp_detail)
for k,v in winscp_detail.items():
    if k < stop_flag:
        idx_counter = k
        idx_counter += 1
        idx_stop = winscp_detail.get(idx_counter)
        idx_stop = idx_stop[3]
        winscp_detail[k].append(idx_stop)
    else:
        winscp_detail[k].append(':')

# append list of steps for a job
for k,v in winscp_detail.items():
    idx_start = int(v[3]) + 1
    if not v[4] == ':':
        idx_stop = int(v[4])
        steps = winscp_raw[idx_start:idx_stop]
    else:
        steps = winscp_raw[idx_start:]
    winscp_detail[k].append(steps)

# get number of filetransfers per partner
partner_jobs = {}
for v in winscp_detail.values():
    partner = v[1]
    job = v[2]
    steps = v[5]
    if partner not in partner_jobs.keys():
        partner_jobs[partner] = []
        partner_jobs[partner].append(job)
        for item in steps:
            if 'Failed' in item:
                partner_jobs[partner].append('FAILED')
    else:
        partner_jobs[partner].append(job)
        for item in steps:
            if 'Failed' in item:
                partner_jobs[partner].append('FAILED')

sorted_partner_jobs = sorted(partner_jobs.items())

# write summary and all log entries to result file
with open(winscp_result, 'w+') as result:
    result.write('Summary:' + '\n')
    result.write('partner name' + ';' + 'number of jobs' ';' + 'failed jobs' + '\n')
    for line in sorted_partner_jobs:
        failed = line[1].count('FAILED')
        success = len(line[1]) - failed
        result.write(line[0] + ';' + str(success) + ';' + str(failed) + '\n')
    result.write('\n' + 'Log for all jobs:' + '\n')
    for key, value in winscp_detail.items():
        for step in value[5]:
            if 'Script: ' in step:
                result.write(str(key) + ';' + value[0] + ';' + value[1] + ';' + value[2] + ';' + step + '\n')
            elif 'failed' in step:
                result.write(str(key) + ';' + value[0] + ';' + value[1] + ';' + value[2] + ';' + step + '\n')        

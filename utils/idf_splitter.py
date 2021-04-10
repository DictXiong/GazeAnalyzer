import csv,os

# 实验常量
label_sentence = "sentence"
label_starttime = "text.started"
label_duration = "key_resp.rt"
start_message = "eb7fb6ea27e5c57b63452296ade184aa_1680x1050.jpg"

# 传入眼动文件的一行, 输出其时间戳 (us)
def get_timestamp_of_eye_line(s):
    return int(s.split('\t')[0])

# 传入一个[时间字符串], 输出其时间戳 (us)
def get_time_stamp_of_psy(s):
    return int(float(s.replace('[','').replace(']','')) * 1e6)

def split_idf(idf_path:str, psy_path:str, dst_dir:str, delta_t:float):
    # 读取psychopy有效数据的有效列
    psy_data = []
    with open(psy_path, 'r', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i in reader:
            if not i[label_starttime]:
                continue
            psy_data.append({
                label_sentence: i[label_sentence], 
                label_starttime: i[label_starttime],
                label_duration: i[label_duration]
            })

    #读取眼动文件的所有行
    eye_data = []
    with open(idf_path, 'r', encoding='UTF-8') as f:
        eye_data = f.readlines()
    # 初始化参数
    table_header = ""
        # 闭区间 [start_line, end_line]
    start_line = 0
    end_line = -1
    delta_time = 0 # 时间差 eye - psy = delta, 单位微秒
    # 开始遍历找到表头
    while('##' in eye_data[start_line]):
        start_line += 1
    # 存储表头
    table_header = eye_data[start_line]
    # 开始寻找start_message. 完成时, start_line应当指向含有message的这一行
    while(start_message not in eye_data[start_line]):
        start_line += 1
    delta_time = get_timestamp_of_eye_line(eye_data[start_line+1]) - int(float(psy_data[0][label_starttime]) * 1e6)
    # 处理额外的时间偏移
    delta_time += int(0.5e6) # between 'ITI1.started' and 'text.started'
    delta_time += int(delta_t*1e6)
    print(f'delta time = {delta_time} us')
    end_line = start_line

    # 开始遍历psychopy数据里面的每一节
    for i in psy_data:
        start_line = end_line + 1
        start_time = get_time_stamp_of_psy(i[label_starttime])
        # 遍历直到眼动数据的时间戳进入了 i 的时间起点
        while (get_timestamp_of_eye_line(eye_data[start_line]) < start_time + delta_time):
            start_line += 1
        end_line = start_line + 1
        end_time = start_time + get_time_stamp_of_psy(i[label_duration])
        while (get_timestamp_of_eye_line(eye_data[end_line]) <= end_time + delta_time):
            end_line += 1
        end_line -= 1
        # 好 现在我们把 [start_time, end_time] 之间的数据写入文件
        with open(os.path.join(dst_dir, i[label_sentence] + ".txt"), 'w') as f:
            f.write(table_header)
            #f.write(f"{start_time + delta_time}\tMSG\t1\t# Message: okk\n")
            for j in range(start_line, end_line+1):
                f.write(eye_data[j])

if __name__ == "__main__":
    source_eye = r"D:\OneDrive - DictTech Co. Ltd\Workspace\2021-03-20-心双毕设实验\source\wyl-idf\熊典-eye_data Samples.txt"
    source_psy = r"D:\OneDrive - DictTech Co. Ltd\Workspace\2021-03-20-心双毕设实验\source\test\熊典_spr_text1_2021_Mar_18_2213.csv"
    dst_folder = r"D:\OneDrive - DictTech Co. Ltd\Workspace\2021-03-20-心双毕设实验\source\idf_split" + '\\'

    split_idf(source_eye, source_psy, dst_folder)
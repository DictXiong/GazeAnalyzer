# analyze.py
# 目标: 输入同一个被试的所有句子情况 (眼动和图像), 处理信息

from utils.idf_reader import read_idf
from utils.idf_splitter import split_idf
import os,math,csv

file_path = os.path.split(os.path.realpath(__file__))[0]
source_img_dir = "../source/eye_images"
tmp_dir = os.path.join(file_path, "gaze_analyze_tmp")
sentence_conf_file = os.path.join(file_path, r"utils/sentence.csv")
value_f = 1
value_s = 2
DISPSIZE = (1680,1050)

def distance(a:tuple, b:tuple):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

class KPI:
    def __init__(self):
        self.sequence = -1
        self.entry_time = -1
        self.dwell_time = 0
        self.revisits = 0
        self.total_fixation_time = 0
        self.first_fixation_time = -1
        self.fixation_count = 0

        # not of AOI
        self.not_of_AOI = False
        self.total_fixation_time_image = -1
        self.aver_jump_dist = -1
        self.total_reverse_count = -1
        self.total_fixation_count = -1

    def to_dict(self):
        return {
            'sequence': self.sequence,
            'entry_time': self.entry_time,
            'dwell_time': self.dwell_time,
            'revisits': self.revisits,
            'total_fixation_time': self.total_fixation_time,
            'first_fixation_time': self.first_fixation_time,
            'fixation_count': self.fixation_count,
            'total_fixation_time_image': self.total_fixation_time_image,
            'aver_jump_dist': self.aver_jump_dist,
            'total_reverse_count': self.total_reverse_count,
            'total_fixation_count': self.total_fixation_count
        }

class AOI:
    def __init__(self, o:tuple, s:tuple):
        self.origin = o
        self.size = s
        self.KPI = KPI()
    def isInside(self, p:tuple):
        if p[0] - self.origin[0] < self.size[0] and p[0] - self.origin[0] >= 0 and p[1] - self.origin[1] < self.size[1] and p[1] - self.origin[1] >= 0:
            return True
        return False
    def clear_KPI(self):
        self.KPI = KPI()
def which_AOI(p:tuple, AOIs:list):
    for i in range(len(AOIs)):
        if (AOIs[i].isInside(p)):
            return i
    print("WTF???")
    return len(AOIs)-1

class Sentence:
    def __init__(self, s:str, t:str, a:str):
        self.text = s
        self.type = t 
        tmp = {'AOI':AOI}
        exec(f"b = {a}", tmp)
        self.AOIs = tmp['b']
        self.AOIs.append(AOI((0,0), DISPSIZE))
    def clear_KPI(self):
        for i in range(len(self.AOIs)):
            self.AOIs[i].clear_KPI()
sentences = []
with open(sentence_conf_file, 'r', encoding="gb2312") as f:
    reader = csv.DictReader(f)
    for i in reader:
        a = i['sentence']
        b = i['type']
        c = i['AOIs']
        sentences.append(Sentence(a,b,c))
def clear_sentences_KPI():
    for i in range(len(sentences)):
        sentences[i].clear_KPI()

# def draw_AOIs(output_dir:str):
#     linewidth = 2
#     color = [0.5,0.5,0.5]
#     for i in sentences:
#         source_img_i = os.path.join(source_img_dir, i.text + '.jpg')
#         dst_img_i = os.path.join(output_dir, i.text + '.jpg')
#         fig, ax = draw_display(DISPSIZE, imagefile=source_img_i)
#         image = matplotlib.image.imread(source_img_i)
#         image.imshow()
#         for j in i.AOIs:
#             if False:
#                 ax.add_line(Line2D(
#                     [j.origin[0], j.origin[1]],
#                     [j.origin[0], j.origin[1] + j.size[1]],
#                     linewidth=linewidth, color=color))
#                 ax.add_line(Line2D(
#                     [j.origin[0], j.origin[1]],
#                     [j.origin[0] + j.size[0], j.origin[1]],
#                     linewidth=linewidth, color=color))
#                 ax.add_line(Line2D(
#                     [j.origin[0] + j.size[0], j.origin[1] + j.size[1]],
#                     [j.origin[0], j.origin[1] + j.size[1]],
#                     linewidth=linewidth, color=color))
#             ax.add_line(Line2D(
#                 [j.origin[0] + j.size[0], j.origin[1] + j.size[1]],
#                 [j.origin[0] + j.size[0], j.origin[1]],
#                 linewidth=linewidth, color=color))
#         ax.invert_yaxis()
#         fig.savefig(dst_img_i)
#         break

# draw_AOIs(r"D:\OneDrive - DictTech Co. Ltd\Workspace\2021-03-20-心双毕设实验\source\eye_images_AOIs" + '\\')
# exit(0)

# 处理一个被试的一个刺激. 输入单个刺激的 idf 文件. 
def single_analyze(idf_path:str, img_path:str, sentence:Sentence):
    AOIs = sentence.AOIs
    idf_data = read_idf(idf_path)

    total_fixation_time_image = 0
    last_fixation = None
    total_jump_dist = 0
    total_fixation_count = 0
    total_reverse_count = 0
    # calc KPI
    AOIs_entered = 0
    AOI_now = -1

    last_saccade_time = 0
    for i in idf_data:
        if i["Value"] == value_f: # if it's a fixation
            if last_fixation == None:
                last_fixation = i
            total_fixation_count += 1
            total_fixation_time_image += i["Duration"]
            AOI_index = which_AOI((i["mean_x"], i["mean_y"]), AOIs)
            AOIs[AOI_index].KPI.total_fixation_time += i["Duration"]
            AOIs[AOI_index].KPI.dwell_time += i["Duration"]
            AOIs[AOI_index].KPI.fixation_count += 1
            if (AOI_now != AOI_index):  #entered a new AOI
                AOIs[AOI_now].KPI.dwell_time += last_saccade_time / 2
                AOIs[AOI_index].KPI.dwell_time += last_saccade_time / 2
                last_saccade_time = 0
                AOI_now = AOI_index
                if AOIs[AOI_index].KPI.sequence == -1: # if never entered before
                    AOIs_entered += 1
                    AOIs[AOI_index].KPI.sequence = AOIs_entered
                    AOIs[AOI_index].KPI.entry_time = i["Start"]
                    AOIs[AOI_index].KPI.first_fixation_time = i["Duration"]
                else: # if entered one that visited
                    AOIs[AOI_index].KPI.revisits += 1
            elif last_saccade_time != 0:
                AOIs[AOI_index].KPI.dwell_time += last_saccade_time
                last_saccade_time = 0
            # other KPI
            total_jump_dist += distance((i["mean_x"],i["mean_y"]), (last_fixation["mean_x"],last_fixation["mean_y"]))
            total_reverse_count += 1 if i["mean_x"] < last_fixation["mean_x"] else 0
            last_fixation = i
        elif i["Value"] == value_s:
            last_saccade_time += i["Duration"]
        else:
            print(f"Unknown Data Type: {i['Value']}")
            print("Press enter to continue or Ctrl+C to exit...")
            input()
    if last_saccade_time != 0:
        AOIs[AOI_now].KPI.dwell_time += last_saccade_time
        last_saccade_time = 0

    ans = []
    for i in range(len(AOIs)):
        tmp = AOIs[i].KPI.to_dict()
        tmp['AOI'] = i
        ans.append(tmp)
    tmp = KPI()
    tmp.total_fixation_time_image = total_fixation_time_image
    if total_fixation_count > 1:
        tmp.aver_jump_dist = total_jump_dist/(total_fixation_count-1)
    tmp.total_reverse_count = total_reverse_count
    tmp.total_fixation_count = total_fixation_count
    ans.append(tmp.to_dict())
    return ans
    # if False:
    #     for i in AOIs:
    #         print(i.KPI.to_dict())
    #     print(total_fixation_time_image)
    #     print(total_jump_dist/(total_fixation_count-1))
    #     print(total_reverse_count)
    #     print(total_fixation_count)

# 处理一个被试的所有数据. 输入: 该被试的 idf 文件和 psychopy 文件.
def man_analyze(idf_path:str, psy_path:str, delta_t:float):
    ans = []
    split_idf(idf_path, psy_path, tmp_dir, delta_t)
    for i in sentences:
        source_idf_i = os.path.join(tmp_dir, i.text + '.txt')
        source_img_i = os.path.join(source_img_dir, i.text + '.jpg')
        ret = single_analyze(source_idf_i, source_img_i, i)
        for j in ret:
            j['sentence'] = i.text
            j['type'] = i.type
            ans.append(j)
    return ans

def clear_tmp():
    for i in sentences:
        os.remove(os.path.join(tmp_dir, i.text + '.txt'))

def write_to_csv(data:dict, dst:str):
    with open(dst, 'w', newline='', encoding="gb2312") as f:
        field = ['type','sentence','AOI','sequence','entry_time','dwell_time','revisits','total_fixation_time','first_fixation_time','fixation_count','total_fixation_time_image','aver_jump_dist','total_reverse_count','total_fixation_count']
        writer = csv.DictWriter(fieldnames=field, f=f)
        writer.writeheader()
        writer.writerows(data)

# ret = man_analyze(
#     r"D:\OneDrive - DictTech Co. Ltd\Workspace\2021-03-20-心双毕设实验\source\wyl-idf\xyy-eye_data Samples.txt", 
#     r"D:\OneDrive - DictTech Co. Ltd\Workspace\2021-03-20-心双毕设实验\source\psychopy\xyy_spr_text1_2021_Mar_23_1456.csv"
# )

# 群组分析. 要求: idf 目录和 psy 目录下的文件均仅包含人名.
def group_analyze(config:str, dst_dir:str, save_for_everyone=True):
    idf_files = []
    psy_files = []
    delta_t = []
    with open(config, 'r', encoding='UTF-8') as f:
        reader = csv.DictReader(f)
        for i in reader:
            print(i)
            idf_files.append(i['idf_file'])
            psy_files.append(i['csv_file'])
            delta_t.append(float(i['delta_t']))

    names = []
    for i in idf_files:
        names.append(os.path.split(i)[1].split('.')[0])
    results = []
    for i in range(len(idf_files)):
        clear_sentences_KPI()
        try: 
            results.append(man_analyze(idf_files[i], psy_files[i], delta_t[i]))
            clear_tmp()
        except IOError as e:
            print(f"Error: maybe there's sth wrong in filenames: {str(e)}")
            print("Press enter to continue or Ctrl+C to exit...")
            input()
        print(" ", names[i], " OK")
        if save_for_everyone:
            write_to_csv(results[-1], os.path.join(dst_dir, names[i] + '.csv'))
    average = []
    len_of_man_analyze = len(results[0])
    keys = results[0][0].keys()
    # 遍历每一行, 逐行处理
    for i in range(len_of_man_analyze):
        average_line = {}
        # 遍历所有的标签
        for k in keys:
            if k not in results[0][i]:
                continue
            # 如果说这个标签的内容是字符串的话
            if type(results[0][i][k]) == str:
                average_line[k] = results[0][i][k]
            # 否则就是可加的数字
            else:
                average_line[k] = 0
                # 遍历每一个人, 加起来之后取平均
                for j in results:
                    average_line[k] += j[i][k]
                average_line[k] /= len(results)
        average.append(average_line)
    write_to_csv(average, os.path.join(dst_dir, 'group_analyze.csv'))

if __name__ == "__main__":
    #group_analyze(os.path.join(file_path, r"../config.csv"), os.path.join(file_path, r"../output"), True)
    group_analyze(os.path.join(file_path, r"../config_elderly.csv"), os.path.join(file_path, r"../output_elderly"), True)
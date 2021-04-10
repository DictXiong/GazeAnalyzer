import rpy2.robjects as robjects

# read idf by gazepath
def read_idf(idf_path:str):
    # 大致参数都写死在下方的 r 脚本中了. 
    r_script = [
        'options(warn=-1)',
        'library(gazepath)',
        f'eye_data = read.table("{idf_path}", header = TRUE, sep = "\\t")',
        'ret = gazepath(data = eye_data, x1 = "L.POR.X..px.", y1 = "L.POR.Y..px.", x2 = "R.POR.X..px.", y2 = "R.POR.Y..px.", d1 = "L.EPOS.Z", d2 = "R.EPOS.Z", trial = "Trial", height_px = 1050, height_mm = 296.100, width_px = 1680, width_mm = 473.760, res_x = 1680, res_y = 1050, samplerate = 250, method = "gazepath")',
        'summary(ret)',
    ]
    try:
        r_ret = robjects.r("\n".join(r_script))
        len_summary = len(list(r_ret.rx2("Value")))
        print("R", end="", flush=True)
    except Exception as e:
        print(f"Handling {idf_path}:")
        print(f"R Error: {str(e)}")
        return {}

    summary = [{} for i in range(len_summary)]
    # 需要哪些列的信息
    to_collect = ["Value", "Duration", "Start", "End", "mean_x", "mean_y", "Order"]
    for i in to_collect:
        tmp = r_ret.rx2(i)
        for j in range(len_summary):
            summary[j][i] = tmp[j]

    return summary


if __name__ == "__main__":
    ret = read_idf(r"/mnt/d/OneDrive - DictTech Co. Ltd/Workspace/2021-03-20-心双毕设实验/source/test/帮助赵丽的同学理论上的确得到了班主任的大力表扬。.txt")
    print(ret)
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os

warnings.filterwarnings("ignore")

def read_hyperspectrum(file_path):
    """
    读取高光谱图像数据，行数rows=512，列数cols=512，波段数bands=204，存储格式BIL
    :param file_path: 文件路径
    :return mean_spectrum: 平均光谱曲线
    """
    # 数据参数
    rows = 512  # 行数
    cols = 512  # 列数
    bands = 204  # 波段数
    dtype = np.float32  # 数据类型

    total_elements = rows * cols * bands  # 计算总元素数量

    # 1.读取二进制数据
    with open(file_path, 'rb') as f:
        data = np.fromfile(f, dtype=dtype, count=total_elements)

    # 重塑为三维数组 (BIL格式: [行, 波段, 列])
    data_bil = data.reshape((rows, bands, cols))

    # 转换为 [行, 列, 波段] 格式
    raw_data = np.transpose(data_bil, (0, 2, 1))

    # 3.波段算法
    # 波段索引 (波段号-1，因为索引从0开始)
    band2_idx = 140  # 第54波段
    band1_idx = 80  # 第36波段

    # 指数波段差运算：exp(20*(54波段-36波段))
    ratio_data = np.exp(2 * (raw_data[:, :, band2_idx] - raw_data[:, :, band1_idx]))

    # 归一化到[0,1]范围
    ratio_data_norm = (ratio_data - ratio_data.min()) / (ratio_data.max() - ratio_data.min())

    # 创建二值图像，二值图像(0=黑，1=白)
    threshold = 0.4
    binary_image = np.zeros((512, 512), dtype=np.uint8)  # 初始化全部元素为0，即黑色

    binary_image[ratio_data_norm >= threshold] = 1  # 高于阈值的的叶片区域设为255，即白色

    # 4.平均光谱曲线
    valid_pixel_num = np.sum(binary_image == 1)

    # 计算所有满足阈值条件的像素的平均光谱
    if valid_pixel_num > 0:
        # 获取所有满足条件的像素的光谱数据
        valid_spectra = raw_data[binary_image == 1, :]

        # 计算平均光谱
        mean_spectrum = np.mean(valid_spectra, axis=0)
    else:
        mean_spectrum = np.zeros(bands)
        print("警告：没有像素满足阈值条件！")

    return mean_spectrum


def curve_plot(mean_spectrum, sample_label):
    """绘制平均光谱曲线"""
    wavelength = np.arange(400, 1012, 3)

    plt.figure(figsize=(6, 6))

    plt.plot(wavelength, mean_spectrum, 'b-', linewidth=1.5)

    plt.title(f'average hyperspectral curve of {sample_label}')
    plt.xlabel('wavelength')
    plt.ylabel('average reflectance')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def read_data(file_path, sample_label):
    # sample_label = 1945

    if os.path.exists(file_path):

        # 1.提取平均光谱曲线
        mean_spectrum = read_hyperspectrum(file_path)

        # 2.显示原始曲线图
        # curve_plot(mean_spectrum, sample_label)

        # 2. 数据预处理：将反射率转为吸光度，取以10为底的对数，然后乘以-1
        absorbance = -np.log10(mean_spectrum)

        # 3. 转为一阶导数
        # 使用 np.gradient 可以保持输出长度与输入一致 (204,)
        derivative = np.gradient(absorbance)

        # 4.显示处理后的曲线
        # curve_plot(derivative, sample_label)
    else:
        print(f'==============={sample_label}文件不存在===============')

    return derivative

def main():
    import os
    file_name = str(9247)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, file_name, "results", f"REFLECTANCE_{file_name}.dat")
    
    print(f"\n开始读取{file_name}数据...")
    mean_spectrum = read_data(file_path, file_name)


if __name__ == "__main__":
    main()
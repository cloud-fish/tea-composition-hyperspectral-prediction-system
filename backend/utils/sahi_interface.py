import os
import glob
import cv2
import torch
from tqdm import tqdm
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

# ================= 配置区域 =================
# 1. 模型路径
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "detection_best.pt")

# 2. 待推理的新图片文件夹
INPUT_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images")

# 3. 生成的 txt 标签保存目录
OUTPUT_LABELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "labels")

# 4. 推理参数设置
CONF_THRESHOLD = 0.1  # 置信度阈值（打伪标签建议设高一点，宁缺毋滥，比如0.4或0.5）
SLICE_HEIGHT = 640  # 切片高度
SLICE_WIDTH = 640  # 切片宽度
OVERLAP_RATIO = 0.2  # 切片重叠率


# ============================================

def ensure_dir(path):
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)


def xyxy2yolo(box, img_w, img_h):
    """
    将绝对坐标 [xmin, ymin, xmax, ymax] 转换为 YOLO 归一化格式 [x_center, y_center, w, h]
    """
    xmin, ymin, xmax, ymax = box

    # 计算中心点和宽高
    x_center = (xmin + xmax) / 2.0
    y_center = (ymin + ymax) / 2.0
    box_w = xmax - xmin
    box_h = ymax - ymin

    # 归一化
    x_center /= img_w
    y_center /= img_h
    box_w /= img_w
    box_h /= img_h

    # 限制在 0-1 之间，防止越界
    x_center = max(0.0, min(1.0, x_center))
    y_center = max(0.0, min(1.0, y_center))
    box_w = max(0.0, min(1.0, box_w))
    box_h = max(0.0, min(1.0, box_h))

    return x_center, y_center, box_w, box_h


def main():
    ensure_dir(OUTPUT_LABELS_DIR)

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"⚙️ 正在加载 SAHI 模型 (设备: {device}) ...")

    # 加载 SAHI 模型
    detection_model = AutoDetectionModel.from_pretrained(
        model_type='yolo11',
        model_path=MODEL_PATH,
        confidence_threshold=CONF_THRESHOLD,
        device=device
    )

    # 获取所有图片路径 (支持多种格式)
    image_paths = []
    for ext in ["*.jpg", "*.png", "*.jpeg", "*.bmp"]:
        image_paths.extend(glob.glob(os.path.join(INPUT_IMAGES_DIR, ext)))
        # 支持大写后缀
        image_paths.extend(glob.glob(os.path.join(INPUT_IMAGES_DIR, ext.upper())))

    if not image_paths:
        print(f"⚠️ 在 {INPUT_IMAGES_DIR} 中未找到任何图片，请检查路径！")
        return

    print(f"🚀 开始为 {len(image_paths)} 张图片生成 YOLO 标签...")

    for img_path in tqdm(image_paths):
        # 1. 读取图片获取宽高
        img = cv2.imread(img_path)
        if img is None:
            print(f"⚠️ 无法读取图片: {img_path}，已跳过。")
            continue
        img_h, img_w = img.shape[:2]

        # 2. 执行 SAHI 切片推理
        result = get_sliced_prediction(
            img_path,
            detection_model=detection_model,
            slice_height=SLICE_HEIGHT,
            slice_width=SLICE_WIDTH,
            overlap_height_ratio=OVERLAP_RATIO,
            overlap_width_ratio=OVERLAP_RATIO,
            perform_standard_pred=False,
            postprocess_type="GREEDYNMM",
            postprocess_match_metric="IOS",
            verbose=0
        )

        # 3. 解析预测结果并转换为 YOLO 格式
        yolo_lines = []
        for obj in result.object_prediction_list:
            cls_id = obj.category.id
            box_xyxy = obj.bbox.to_xyxy()  # [xmin, ymin, xmax, ymax]

            # 坐标转换
            x_c, y_c, w, h = xyxy2yolo(box_xyxy, img_w, img_h)

            # 拼接成 YOLO 格式字符串: class x_center y_center width height
            line = f"{cls_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n"
            yolo_lines.append(line)

        # 4. 写入 txt 文件
        # 提取原文件名（不含后缀）
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        txt_path = os.path.join(OUTPUT_LABELS_DIR, f"{base_name}.txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.writelines(yolo_lines)

        # 注意：如果一张图中没有检测到任何目标，上述代码会生成一个空的 txt 文件。
        # 这在 YOLO 训练中是标准做法（代表背景图），请予以保留。

    print(f"\n🎉 全部完成！YOLO 标签文件已成功保存至: {OUTPUT_LABELS_DIR}")


if __name__ == "__main__":
    main()
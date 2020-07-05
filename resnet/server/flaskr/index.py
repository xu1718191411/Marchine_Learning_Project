import os
import sys
sys.path.append("/home/xuzhongwei/Source/Machine_Learning_Project")


from resnet.collate_fn import collater
from resnet.image_transform import ImageTransform
from resnet.make_data_path import make_data_path
from torch.utils.data import DataLoader
from torchvision.models import resnet50
import torch
from resnet.dataset import WeaponDataset

def index_router():
    return run_process_result()

def run_process_result():
    trainDataPath = "/home/xuzhongwei/Source/Machine_Learning_Project/resnet/dataset/train"
    valDataPath = "/home/xuzhongwei/Source/Machine_Learning_Project/resnet/dataset/val"
    categories = ["f15", "f16", "f18"]

    _, valDataPath = make_data_path(trainDataPath, valDataPath, categories)

    trainTransform = ImageTransform(224, (0.485, 0.456, 0.406), (0.229, 0.224, 0.225))

    valDataSet = WeaponDataset(valDataPath, trainTransform, "val")
    valDataLoader = DataLoader(valDataSet, shuffle=True, batch_size=1, collate_fn=collater)

    model = resnet50(pretrained=True)
    model = model.train()
    model.fc = torch.nn.Linear(in_features=2048, out_features=3, bias=True)
    model = model.cuda()

    print("valdataset {}".format(valDataLoader.dataset.__len__()))

    print("start evaluating")
    PATH = "/home/xuzhongwei/Source/Machine_Learning_Project/resnet/trainning_result/train_by_offical_model_final.pth"
    model.load_state_dict(torch.load(PATH))
    model = model.eval()

    total = 0
    for batchIndex, data in enumerate(valDataLoader):
        input = data["images"].cuda()
        categories = data["categories"].cuda()
        output = model(input)
        pred = torch.argmax(output, dim=1)
        s = torch.sum(pred == categories)
        total += s

    return "accuracy: {}".format(int(total) / len(valDataLoader.dataset))
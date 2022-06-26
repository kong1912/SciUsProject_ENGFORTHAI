"""Copy of Thai speech command recognition with torchaudio

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ensKfWzt6WEvmAZTrtMtyUrX1i5JBkMk
"""
import math
import os
import pathlib

# import IPython.display as ipd
from typing import NamedTuple

import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchaudio
from torch.utils.data import Dataset
from tqdm import tqdm

__all__ = [
    "EndToEndSetting",
    "EndToEndDataset",
    "EndToEndASR",
    "M5"
]


class EndToEndSetting(NamedTuple):
    annotations_file_train: pathlib.Path
    annotations_file_test: pathlib.Path
    model_file: pathlib.Path
    audio_dir: pathlib.Path


class EndToEndDataset(Dataset):
    """Importing the Dataset
    ---------------------
    original code from Gowajee V0.9.2 (downloaded 27/Jul/2021)
    https://github.com/ekapolc/gowajee_corpus
    """

    def __init__(self, annotations_file, audio_dir):
        self.annotations = pd.read_csv(annotations_file)
        self.audio_dir = audio_dir

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, index):
        audio_sample_path = self._get_audio_sample_path(index)
        label = self._get_audio_sample_label(index)
        waveform, sr = torchaudio.load(audio_sample_path)
        return waveform, sr, label

    def _get_audio_sample_path(self, index):
        path = os.path.join(self.audio_dir, self.annotations.iloc[
            index, 0])
        return path

    def _get_audio_sample_label(self, index):
        return self.annotations.iloc[index, 1]


class M5(nn.Module):
    """Define the Network
    ------------------

    For this tutorial we will use a convolutional neural network to process
    the raw audio data. Usually more advanced transforms are applied to the
    audio data, however CNNs can be used to accurately process the raw data.
    The specific architecture is modeled after the M5 network architecture
    described in `this paper <https://arxiv.org/pdf/1610.00087.pdf>`__. An
    important aspect of models processing raw audio data is the receptive
    field of their first layer’s filters. Our model’s first filter is length
    80 so when processing audio sampled at 8kHz the receptive field is
    around 10ms (and at 4kHz, around 20 ms). This size is similar to speech
    processing applications that often use receptive fields ranging from
    20ms to 40ms.
    """

    def __init__(self, n_input=1, n_output=24, stride=16, n_channel=32):
        super().__init__()
        self.conv1 = nn.Conv1d(n_input, n_channel, kernel_size=80, stride=stride)
        self.bn1 = nn.BatchNorm1d(n_channel)
        self.pool1 = nn.MaxPool1d(4)
        self.conv2 = nn.Conv1d(n_channel, n_channel, kernel_size=3)
        self.bn2 = nn.BatchNorm1d(n_channel)
        self.pool2 = nn.MaxPool1d(4)
        self.conv3 = nn.Conv1d(n_channel, 2 * n_channel, kernel_size=3)
        self.bn3 = nn.BatchNorm1d(2 * n_channel)
        self.pool3 = nn.MaxPool1d(4)
        self.conv4 = nn.Conv1d(2 * n_channel, 2 * n_channel, kernel_size=3)
        self.bn4 = nn.BatchNorm1d(2 * n_channel)
        self.pool4 = nn.MaxPool1d(4)
        self.fc1 = nn.Linear(2 * n_channel, n_output)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(self.bn1(x))
        x = self.pool1(x)
        x = self.conv2(x)
        x = F.relu(self.bn2(x))
        x = self.pool2(x)
        x = self.conv3(x)
        x = F.relu(self.bn3(x))
        x = self.pool3(x)
        x = self.conv4(x)
        x = F.relu(self.bn4(x))
        x = self.pool4(x)
        x = F.avg_pool1d(x, x.shape[-1])
        x = x.permute(0, 2, 1)
        x = self.fc1(x)
        return F.log_softmax(x, dim=2)


class EndToEndASR:
    setting: EndToEndSetting

    dataset_train: any
    dataset_test: any
    waveform: any
    sample_rate: any
    label: any

    pretrain_model: any
    labels: any

    def __init__(self, setting: EndToEndSetting):
        self.setting = setting

        self.dataset_train = EndToEndDataset(setting.annotations_file_train, setting.audio_dir)
        self.dataset_test = EndToEndDataset(setting.annotations_file_test, setting.audio_dir)
        print(f"There are {len(self.dataset_train)} samples in the dataset.")
        self.waveform, self.sample_rate, self.label = self.dataset_train[0]
        """A data point in the SPEECHCOMMANDS dataset is a tuple made of a waveform
        (the audio signal), the sample rate, the utterance (label), the ID of
        the speaker, the number of the utterance.
        """

        self.pretrain_model = torch.load(setting.model_file)
        self.labels = sorted(list(set(datapoint[2] for datapoint in self.dataset_train)))

    def get_likely_index(self, tensor):
        # find most likely label index for each element in the batch
        return tensor.argmax(dim=-1)

    def label_to_index(self, word):
        # Return the position of the word in labels
        return torch.tensor(self.labels.index(word))

    def index_to_label(self, index):
        # Return the word corresponding to the index in labels
        # This is the inverse of label_to_index
        return self.labels[index]

    def predict(self, tensor):
        # Use the model to predict the label of the waveform
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        tensor = tensor.to(device)

        new_sample_rate = 8000
        transform = torchaudio.transforms.Resample(orig_freq=self.sample_rate, new_freq=new_sample_rate)

        tensor = transform(tensor)
        tensor = self.pretrain_model(tensor.unsqueeze(0))
        # tensor = model(tensor.unsqueeze(1))
        tensor_index = self.get_likely_index(tensor)
        predict_index = tensor_index.squeeze()

        tensor_list = tensor[0][0].tolist()
        predict_log_score = tensor_list[tensor_index[0].item()]
        predict_score = math.exp(predict_log_score)
        # print(predict_score)

        tensor = self.index_to_label(predict_index)
        # tensor = index_to_label(tensor.squeeze())
        return (tensor, predict_score)

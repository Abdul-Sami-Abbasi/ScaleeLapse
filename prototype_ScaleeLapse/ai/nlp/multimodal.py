"""Proposal experiment: ResNet-50 + transformer pooled features, multilabel head.

Training requires a consented manifest linking each image to caption and labels.
No relationship is inferred between the unpaired supplied image and caption datasets.
"""

import torch
from torch import nn
from torchvision.models import resnet50, ResNet50_Weights
from transformers import AutoModel


class MultimodalHashtags(nn.Module):
    def __init__(
        self,
        num_labels,
        text_model="distilbert/distilbert-base-uncased",
        pretrained_visual=True,
    ):
        super().__init__()
        self.visual = resnet50(
            weights=ResNet50_Weights.DEFAULT if pretrained_visual else None
        )
        self.visual.fc = nn.Identity()
        self.text = AutoModel.from_pretrained(text_model)
        self.classifier = nn.Sequential(
            nn.Linear(2048 + self.text.config.hidden_size, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, num_labels),
        )

    def forward(self, images, input_ids, attention_mask):
        hidden = self.text(
            input_ids=input_ids, attention_mask=attention_mask
        ).last_hidden_state
        mask = attention_mask.unsqueeze(-1)
        text = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1)
        return self.classifier(torch.cat([self.visual(images), text], dim=1))

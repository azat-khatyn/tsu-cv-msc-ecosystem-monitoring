import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image




# Загрузка модели
def load_model():
    # Определяем количество классов
    num_classes = 2  # wildfire / no wildfire

    # Создаём модель
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, num_classes)  # Заменяем последний слой

    # Загружаем веса
    model.load_state_dict(torch.load("model/resnet50_wildfire.pth", map_location=device))
    model.to(device)
    model.eval()  # Переключаем в режим оценки

    return model


# Подготовка изображения
def prepare_image(image_path, img_size=(256, 256)):
    image = Image.open(image_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize(img_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image = transform(image).unsqueeze(0)  # Добавляем batch dimension
    return image


# Функция предсказания
def predict(image_path):
    # Загрузка модели
    model = load_model()

    # Подготовка изображения
    input_tensor = prepare_image(image_path)

    # Предсказание
    with torch.no_grad():
        output = model(input_tensor)
        output = torch.sigmoid(output)  # Применяем сигмоиду для получения вероятностей
        prediction = (output[0][0] > 0.5).float()  # Бинаризация (порог 0.5)

    # Возвращаем класс (1 или 0)
    return prediction


# Пример использования
# image_path = 'img2.jpg'
# prediction = predict(image_path)
# print(f"Предсказанный класс: {prediction}")
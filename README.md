# Мониторинг Экосистемы Леса




---


## О команде


| Участник      | Фокус работы                                                                                           |
|---------------|--------------------------------------------------------------------------------------------------------|
|Большова Елизавета | Обучение ResNet50 на EuroSat Dataset (Kaggle), генерация рекоммендаций                                 |
|Родина Екатерина   | Обучение ResNet 50 на Wildfire Dataset (Kaggle), оценка качества модели                                |
|Токаревский Святослав | Разработка модуля аугментации данных, интеграция аугментации в Dataloader,                             |
|Халитова Яна   | Тимлид, Обучение ResNet50 на Smoke&Fire Dataset (Huggingface), YOLO11 на Fire&Smoke Dataset (Roboflow) |
| Храмков Николай   | Исследование использования спутниковых данных через Google Earth Engine, применение SAM фреймворка     |
| Шайдуров Даниил     | Дизайн и имплементация телеграм бота для развертывания модели, обучение ResNet50                       |


---


## О проекте
**Мониторинг экосистемы леса** — это комплексное решение на основе моделей компьютерного зрения (Computer Vision), позволяющее осуществлять мониторинг состояний лесных покровов на предмет деградации состояния, в частности, распозновать и оповещать об убывании лесного покрова, вырубки леса, пожары и пр.  



## Функциональность решения
Доступно в настоящий момент: 
- Детекция возгорания и задымления на предоставленных изображениях 
- Детекция поражения лесных покровов на предоставленных спутниковых снимках (вырубка, заболевания)

Также доступно чтение изображений с помощью веб камеры локального устройства, на котором запущено приложение.

В дальнейшем: 
- Мониторинг состояний экосистемы леса через видеопоток определенных участков леса.
- И при возникновении признаков деградации - оповещение соответсвующих слуб и организаций через бот.
---

## Поддерживаемые алгоритмы распознования
- ResNet50

В дальнейшем: 
- YOLO11
- SAM

## Оценки качества дообученных моделей

| Модель             | Precision | Recall | F1 score |
|--------------------|-----------|--------|----------|
| ResNet50 (EuroSat) | 98%       | 97.9%  | 98.7%     |
| ResNet50 (Wildfire) | 98%       | 98%    | 98%      |
| YOLO11 (Fire&Smoke) | 99.4%     | 99.6%  | 99.5%    |


---

## Установка и запуск приложения мониторинга


### Шаг 1: Клонирование репозитория
```bash
git clone https://github.com/azat-khatyn/tsu-cv-msc-ecosystem-monitoring
cd tsu-cv-msc-ecosystem-monitoring
```


### Шаг 2: Установка зависимостей


Создайте и активируйте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```


Установите зависимости:
```bash
pip install -r requirements.txt
```


### Шаг 3: Запуск приложения
```bash
cd app
python main.py
```



---

## Структура проекта


```plaintext
tsu-cv-msc-ecosystem-monitoring
│
└── app                             # Бот для инференса
│    ├──  model
│    │      ├── new_model.py
│    │      ├── resnet50_wildfire.pth
│    ├──  user_photos
│    ├──  main.py
│    ├──  repository_models.py                
│    ├── utils.py
├── augmentation                    # Модули для аугментации данных
├── notebooks                       # Ноутбуки с обучением и исследованием моделей
└── README.md                       # Документация

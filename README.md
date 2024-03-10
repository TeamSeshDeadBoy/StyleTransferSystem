# StyleTransfer - Photomaker bot
**StyleTransfer - Генерация изображений с помощью Telegram Bot и AI-модели Photomaker**
   
<hr></hr>
![Без имени-1](https://github.com/TeamSeshDeadBoy/StyleTransferSystem/assets/57834332/a2c7055e-4e8d-4359-a8c6-02162f180561)
<hr></hr>

Проект состоит из **трех** модулей, обернутых в docker-container:           

 - Telegram bot (PytelegramBotApi)     
 - Backend (FastAPI + Torch + CUDA)     
 - Redis (Redis Queue)     

Все модули собраны в одну композицию через **docker-compose** [^1]    

Использование модели происходит через встроенный интерфейс Telegram через создаваемого Телеграм бота.  Пользователь настраивает свой
конфигурационный файл, затем присутпает к генерации. Фотографии пользователя, промпт и настройки передаются на FastAPI бэкэнд, где задача генерации
добавляется в очередь через RedisQueue. Очередь задач запускает 'воркеров' на выполнение задач, на А10 генерация картинки занимает 17 секунд,
занимает до 22гб видеопамяти на оптимизированной (с VAE slicing) и до 35гб на неоптимизированной (out-of-the-box) модели.   
Для использования необходима NVidia GPU c 20+ гигабайтами видеопамяти и установленные CUDA драйвера. Вывод картинки происходит через telegram bot. 


## Требования:

- **CUDA** NVIDIA GPU drivers (v 11.6)
- **21gb** + GPU MEM


## Установка:

### Установка через самостоятельную сборку контейнеров:

0. **Запулить основной python image для сборки контейнеров: <code>docker pull ayyyoshii/base_python:style</code>
1. Переименовать python image: <code>docker tag ayyyoshii/base_python:style base_python/1</code>
2. Клонировать репозиторий
3. Создать **.env** файл по примеру **.template_env** [^2]
4. Занести необходимую информацию в .env (токен Бота, настройки при необходимости)
5. Собрать проект через    <code>docker compose build</code> 
6. Запустить проект через    <code>docker compose up</code>


### Установка через docker-hub:

0. **Запулить основной python image для сборки контейнеров: <code>docker pull ayyyoshii/base_python:style</code>
1. Переименовать python image: <code>docker tag ayyyoshii/base_python:style base_python/1</code>
2. Создать **.env** файл по примеру **.template_env** [^2]
3. Скопировать **compose.yaml** [^1] файл 
4. Изменить файл **compose.yaml**:
    ```yaml
        services:
            consumer-fastapi:
                ...
                image:
                    - ayyyoshii/style-transfer-server:v1.1_optimized
                ...
            tg-bot:
                ...
                image:
                    - ayyyoshii/style-transfer-bot:v1.1
                ...
            ...
        ...
    ```
5. Запустить контейнеры через <code>docker compose up</code>

# Photomaker модель:

![image](https://camo.githubusercontent.com/c004ae7f537e0fc3a13da99577b79a4f3e354412d1af5c07ee54d51961f9e572/68747470733a2f2f63646e2d75706c6f6164732e68756767696e67666163652e636f2f70726f64756374696f6e2f75706c6f6164732f3632383561393133336162363634323137393135383934342f4259425a4e79666d4e346a424b427878743475787a2e6a706567)

Модель является One-shot генеративной моделью, выпущена 15.01.2024 командой TencentARC, в моей имплементации требует 20 гб видеопамяти.  
Модель имеет возможности стилизации и реалистичной генерации, я имплементировал реалистичную генерацию.  

---
id: "[@li2023photomaker]"
- authors:
  - Li Zhen
  - Cao Mingdeng
  - Wang Xintao
  - Qi Zhongang
  - Cheng Ming-Ming
  - Shan Ying
- issued: 2024
- title: "PhotoMaker: Customizing realistic human photos via stacked ID embedding"
---




[^1]:compose.yaml
[^2]:.template_env

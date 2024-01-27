Запуск сервера fastapi -> <code>python main.py</code>   
   
Запуск воркера (через Ubuntu или среду WSL в папке проекта) -> <code>cd src   rq worker</code>    

Запуск redis (через Ubuntu или среду WSL в папке проекта) -> <code>sudo service redis-server start</code>, <code>redis-cli</code>  

<code>kill_workers.py</code> нужен для очистки запущеных воркеров (не путать воркера с файлом worker.py)

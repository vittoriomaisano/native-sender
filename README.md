### Native-sender ###

Скрипт для отправки нативных монет в сетях: "Ethereum"; "Arbitrum"; "Optimism"; "Avalanche"; "Polygon"; "BSC".

Три режима:
1. "direct" - отравляет определенное количество нативки, которое задается в (native_from, native_to)
2. "remain" - отправляет разницу между балансом кошелька и суммы, которую хотим оставить(remain_native_from, remain_native_to)
3. "full_balance" - отправляет весь баланс

Запуск:
1. Вся настройка описана в 'config.py'
2. Устанавливаем библиотеки 'pip3 install -r requirements.txt'
3. Запускаем 'main.py'
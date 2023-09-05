###config###

network = "Ethereum"                #выбираем сеть("Ethereum"; "Arbitrum"; "Optimism"; "Avalanche"; "Polygon"; "BSC")
mode = "direct"                     #("full_balance" - отправит весь баланс; "remain" - выбираем сколько оставить, остальное отправит; "direct" - указываем сколько отправить)
shuffle = False                     #перемешивать ли кошельки(True-да, False-нет)

#(только для "Ethereum") 
max_gwei = 20                       #если газ gwei выше этого числа будет спать и проверять раз в 10 секунд.
max_gas_check_attempts = 1000       #сколько раз будет оценивать газ

min_delay = 100                     #минимальная задержка между кошельками
max_delay = 120                     #максимальная задержка между кошельками

decimals = 5                        #количество знаков после запятой

#mode = "direct"
native_from = 0.0001                #от скольки отправляем 
native_to = 0.0002                  #до скольки отправляем

#mode = "remain"
native_remain_from = 0.01           #от какого количества ETH оставляем на кошельке
native_remain_to   = 0.02           #до какого количества ETH оставляем на кошельке

#(только для "remain" и "full_balance")
min_amount_to_send = 0.00005        #если количество монет, которое отправляем меньше этого числа отправлять не будет
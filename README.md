# Silver Spring
**A Python BTC Trading Bot/Infrastructure**

![logo](SilverSpring.jpg)

# Overview
Silver Spring is a trading bot and infrastructure for BTC and altcoin exchanges with Python3. This project was created to allow users -

* Automatically exchanges within 7x24 hours
* Rapidly expending new altcoins and exchanges
* Easily creating customer strategies

# Disclaimer

* Please make sure 100% understand the code before any live transactions
* You have fully responsibility for each dollar in your wallet
* Don't test with real money in your account

# Features
* Exchanges websites
	- www.okcoin.cn, REST APIs
* Strategies
	- 50/50 balanced

# To Be Implemented
* [ ] Quotation database
* [ ] GUI
* [ ] Multiple Index

# Release Plan
## 2.0 (Target at WW28'16)
- [Feature] Grid trade
- [Feature] Multi-level logs

>	Type     | Description 
>	-------- | -------------
	Critical | That’s bad, you may lose money when you see this
	Error    | Trade bot is stopped by unavoidable errors
	Warning  | Messages needs attention, unexpected behavior happened
	Info     | For user's information
	Debug    | Use this for developing this project

## 1.1 (Released at WW27'16)
- [Fix #1] Python crash with HTTP request error when network is unstable
- [Fix #2] Exit with buy_market
- [Feature] Multi-level logs
- [Enhance] 50/50 balanced strategy


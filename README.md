# Gillian Ramirez

Overview:
A stock paper trading simulator that engages the user to dip their feet in the world of stock trading. 
The user starts with $100k as their starting balance before buying shares of their preferred stocks. Stocks
that are available to the user for now are Google, Microsoft, and Apple. 

Usage:
- The user can view the history of stock price for Apple, Microsoft, and Google, displayed as a graph.
- The user is given an initial balance of $100000 which updates with every sale and purchase of stocks. This balance saves in localstorage with each completed transaction. Which is also tracked by a history graph inside the portfolio page as well.
- The user can see how many stocks they own from each company. These values update and save in localstorage with each completed transaction.

Technologies used: 
- HTML
- CSS
- Django
- Python
- Plotly
- Yfinance
- Google Fonts

Ideas for future improvement:
- Can view any stock company instead of the three companies I have listed above.
- The user can successfully add as many stocks as they want each time, instead of being only able to purchase one share at a time.
- Less negative space for my pages

How to use:
- Download zip file and use terminal to cd to the website directory
- Use pip to install plotly and yfinance
- Use python manage.py runserver


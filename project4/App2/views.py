from django.shortcuts import  render, redirect, HttpResponse
from django.core.mail import EmailMessage
from django.contrib.auth.forms import UserCreationForm
import pandas as pd
from App2.forms import ContactForm
from django.contrib.auth.decorators import login_required
from .models import Post, StockPortfolio
from .forms import PortfolioForm, ShareForm
from django.contrib import messages
import yfinance as yahooFinance
import yfinance as yf
import plotly.express as px


# Create your views here.
@login_required
def home(request):
    data = Post.objects.all()
    context = getShareGraphContext(1)
    context['data'] = data
    return render(request, "index.html", context)


# Contact Page.
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

        EmailMessage(
            'Contact Form Submission from {}'.format(name),
            message,
            'form-response@example.com',  # Send from (your website)
            [''],  # Send to (your admin email)
            [],
            reply_to=[email]  # Email from the form to get back to
        ).send()

        return redirect('success')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def success(request):
    return render(request, 'success.html')


# Registration
def signup(request):
    return render(request, "signup.html")


def login(request):
    return render(request, "login.html")


def authView(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def navbar(request):
    return render(request, "navbar.html")


# Trade
def ShareCommerce(request):
    print("This is sharecommerce.")
    form = ShareForm(request.POST or None)
    addToPortfolioForm = PortfolioForm(request.POST or None)
    share_company = 'AAPL'  # Default value
    share_price = None  # Default value
    if request.method == "POST" and form.is_valid(): 
        share_company = form.cleaned_data['company']
        print("share_company", share_company)
        # Fetch share price
        share_price = get_share_price(share_company)  # Assuming you have a function to get share price
    context = {'form': form, 'addToPortfolioForm': addToPortfolioForm, 'share_company': share_company, **getShareGraphContext(share_company)}
    if share_price is not None:
        context['share_price'] = share_price
    return render(request, 'assets/base.html', context)


def getShareGraphContext(share_company):
    if share_company:
        try:
            # Fetch data for the selected company
            company_data = yahooFinance.download(share_company, period="1y", actions=True)
            
            # Extract necessary data for plotting
            close_price = company_data['Close']
            last_quote = round(close_price.iloc[-1], 2)
            date = close_price.index
            x_data = date
            y_data = close_price

            # Generate the plot
            fig = px.line(
                x=x_data,
                y=y_data,
            ).update_layout(
                title_text=share_company,
                title_x=0.5,
                xaxis_title="Date",
                yaxis_title="Close Pricing",
                width=600,
                height=400,
                plot_bgcolor='#f9f8f9',
                font=dict(family="Special Elite", color="#000000")
            ).update_traces(line_color='black')
            
            # Convert the plot to HTML
            chart_html = fig.to_html()

            return {
                'chart_html': chart_html,
                'last_quote': last_quote
            }
        except Exception as e:
            # Handle errors gracefully
            print("Error fetching data:", str(e))
            return {}
    else:
        return {}



def shareGraph(request):
    share_company = 1
    context = getShareGraphContext(share_company)
    return render(request, 'assets/sharegraph.html', context)

def add_stock(request):
    user_id = request.user.id
    
    # Retrieve or initialize balance from session
    balance = request.session.get('balance', 100000)

    if request.method == 'POST':
        form = ShareForm(request.POST)
        if form.is_valid():
            share_company = form.cleaned_data['company']
            shares_to_add = int(request.POST.get('shares', 1))  # Get the number of shares to add, defaulting to 1
            try:
                share_price = get_share_price(share_company)
                if share_price:
                    total_price = share_price * shares_to_add  # Calculate the total price
                    if balance >= total_price:
                        # Deduct the total price from balance
                        balance -= total_price

                        # Check if the stock is already in the portfolio
                        portfolio = StockPortfolio.objects.filter(user_id=user_id, stock_id=share_company).first()
                        if portfolio:
                            # Update existing portfolio entry
                            portfolio.shares += shares_to_add
                            portfolio.total_value = portfolio.shares * share_price
                        else:
                            # Create a new portfolio entry
                            portfolio = StockPortfolio(
                                user_id=user_id,
                                stock_id=share_company,
                                shares=shares_to_add,  # Add the specified number of shares
                                share_price=share_price,
                                total_value=total_price  # Set the total value based on the number of shares and price
                            )
                        portfolio.save()

                        # Update session with new balance
                        request.session['balance'] = balance
                        update_balance_history(request, balance)  # Update balance history

                        messages.success(request, f"Successfully bought {shares_to_add} shares of {share_company}.")

                        # Redirect to the portfolio page or render it with updated data
                        return redirect('App2:portfolio')
                    else:
                        messages.error(request, "Insufficient balance to buy these shares.")
                else:
                    messages.error(request, "Failed to fetch share price.")
            except Exception as e:
                messages.error(request, f"Error adding stock: {str(e)}")
        else:
            messages.error(request, "Form is not valid. Please correct the errors.")
    else:
        form = ShareForm()

    # Retrieve updated stock portfolios for the user
    stock_portfolios = StockPortfolio.objects.filter(user_id=user_id)

    # Generate balance history chart
    balance_history_chart = get_balance_history_chart(request.session.get('balance_history', []))

    return render(request, 'assets/portfolio.html', {
        'form': form,
        'balance': balance,
        'stock_portfolios': stock_portfolios,
        'balance_history_chart': balance_history_chart['chart_html'] if balance_history_chart else None,
    })




def sell_stock(request):
    user_id = request.user.id
    
    # Retrieve or initialize balance from session
    balance = request.session.get('balance', 100000)

    if request.method == 'POST':
        stock_id = request.POST.get('stock_id')
        sell_shares_str = request.POST.get('sell_shares', '')

        # Check if sell_shares_str is not empty and is numeric
        if sell_shares_str.isdigit():
            sell_shares = int(sell_shares_str)
            
            # Retrieve the portfolio for the stock_id and user_id
            portfolio = StockPortfolio.objects.filter(stock_id=stock_id, user_id=user_id).first()
            
            if portfolio:  # Check if portfolio exists
                if sell_shares > 0 and sell_shares <= portfolio.shares:
                    try:
                        share_price = get_share_price(stock_id)
                        if share_price:
                            sell_value = share_price * sell_shares
                            
                            # Update the portfolio entry
                            portfolio.shares -= sell_shares
                            if portfolio.shares > 0:
                                portfolio.total_value = portfolio.shares * share_price
                                portfolio.save()
                            else:
                                portfolio.delete()  # Remove the entry if all shares are sold

                            # Update session with new balance
                            balance += sell_value
                            request.session['balance'] = balance
                            update_balance_history(request, balance)  # Update balance history

                            # Refresh stock_portfolios after selling
                            stock_portfolios = StockPortfolio.objects.filter(user_id=user_id)

                            # Generate balance history chart
                            balance_history_chart = get_balance_history_chart(request.session.get('balance_history', []))

                            return render(request, 'assets/portfolio.html', {
                                'stock_portfolios': stock_portfolios,
                                'balance': balance,
                                'balance_history_chart': balance_history_chart['chart_html'] if balance_history_chart else None,
                            })
                        else:
                            messages.error(request, "Failed to fetch share price for selling.")
                    except Exception as e:
                        messages.error(request, f"Error selling stock: {str(e)}")
                else:
                    messages.error(request, "Invalid number of shares to sell.")
            else:
                messages.error(request, "No portfolio found matching the criteria.")
        else:
            messages.error(request, "Invalid input for sell_shares. Please enter a valid number.")
    else:
        messages.error(request, "POST method required for selling stocks.")

    # Retrieve updated stock portfolios after potential changes
    stock_portfolios = StockPortfolio.objects.filter(user_id=user_id)

    # Generate balance history chart
    balance_history_chart = get_balance_history_chart(request.session.get('balance_history', []))

    return render(request, 'assets/portfolio.html', {
        'stock_portfolios': stock_portfolios,
        'balance': balance,
        'balance_history_chart': balance_history_chart['chart_html'] if balance_history_chart else None,
    })


def get_share_price(share_company):
    try:
        stock = yf.Ticker(share_company)
        share_data = stock.history(period="1d")
        return share_data['Close'].iloc[-1]
    except Exception as e:
        print("Error fetching share price:", str(e))
        return None
    

def reset_portfolio(request):
    # Reset portfolio (delete all portfolio entries for the current user)
    StockPortfolio.objects.filter(user_id=request.user.id).delete()
    
    # Reset starting_balance in session
    request.session['balance'] = 100000

     # Clear balance history in session
    request.session['balance_history'] = []

    
    # Redirect back to the same page or another appropriate page
    return redirect('App2:add_stock')  

#transaction history chart
def update_balance_history(request, new_balance):
    balance_history = request.session.get('balance_history', [])
    balance_history.append(new_balance)
    request.session['balance_history'] = balance_history
    request.session.modified = True  # Ensure session is saved

def get_balance_history_chart(balance_history):
      if balance_history:
        try:
            fig = px.line(
                x=range(len(balance_history)),
                y=balance_history,
                labels={'x': 'Transaction', 'y': 'Balance'},
                title='Balance History'
            ).update_layout(
                title_x=0.5,
                width=600,
                height=400,
                plot_bgcolor='#f9f8f9',
                font=dict(family="Special Elite", color="#000000")
            )
            fig.update_traces(line_color='black')
            transactionChart_html = fig.to_html()

            return {
                'chart_html': transactionChart_html,
            }
        except Exception as e:
            print("Error generating chart:", str(e))
            return {}
        else:
            return {}
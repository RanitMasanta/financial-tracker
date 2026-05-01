from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Account, Transaction, Category
from .forms import AccountForm, TransactionForm, CategoryForm

@login_required
def dashboard(request):
    accounts = Account.objects.filter(user=request.user)
    total_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0
    
    # Get last 10 transactions
    recent_transactions = Transaction.objects.filter(user=request.user)[:10]
    
    # Get monthly summary
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0)
    
    monthly_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_expense = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'recent_transactions': recent_transactions,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'net_balance': monthly_income - monthly_expense,
    }
    return render(request, 'finance/dashboard.html', context)

@login_required
def accounts_management(request):
    accounts = Account.objects.filter(user=request.user)
    return render(request, 'finance/accounts.html', {'accounts': accounts})

@login_required
def add_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            messages.success(request, 'Account added successfully!')
            return redirect('accounts')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AccountForm()
    
    return render(request, 'finance/add_account.html', {'form': form})

@login_required
def edit_account(request, account_id):
    account = get_object_or_404(Account, id=account_id, user=request.user)
    
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account updated successfully!')
            return redirect('accounts')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AccountForm(instance=account)
    
    return render(request, 'finance/edit_account.html', {'form': form, 'account': account})

@login_required
def delete_account(request, account_id):
    account = get_object_or_404(Account, id=account_id, user=request.user)
    if request.method == 'POST':
        account.delete()
        messages.success(request, 'Account deleted successfully!')
        return redirect('accounts')
    return render(request, 'finance/delete_account.html', {'account': account})

@login_required
def add_transaction(request):
    categories = Category.objects.filter(user=request.user)
    categories_json = {
        category.id: category.category_type 
        for category in categories
    }
    
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TransactionForm(request.user)
    
    return render(request, 'finance/add_transaction.html', {
        'form': form,
        'categories_json': categories_json,
    })

@login_required
def analytics(request):
    # Get data for charts
    transactions = Transaction.objects.filter(user=request.user)
    
    # Total income and expense
    total_income = transactions.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    net_balance = total_income - total_expense
    
    # Monthly summary
    monthly_data = {}
    current_year = timezone.now().year
    
    for month in range(1, 13):
        monthly_income = transactions.filter(
            transaction_type='income',
            date__year=current_year,
            date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_expense = transactions.filter(
            transaction_type='expense',
            date__year=current_year,
            date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data[month] = {'income': float(monthly_income), 'expense': float(monthly_expense)}
    
    # Expense by category
    category_expenses = {}
    expense_categories = Category.objects.filter(user=request.user, category_type='expense')
    
    for category in expense_categories:
        total = transactions.filter(
            transaction_type='expense',
            category=category
        ).aggregate(total=Sum('amount'))['total'] or 0
        if total > 0:
            category_expenses[category.name] = float(total)
    
    # Spending over time (last 30 days)
    spending_trend = []
    for i in range(30, -1, -1):
        date = timezone.now().date() - timedelta(days=i)
        daily_expense = transactions.filter(
            transaction_type='expense',
            date=date
        ).aggregate(total=Sum('amount'))['total'] or 0
        spending_trend.append({'date': date.strftime('%Y-%m-%d'), 'amount': float(daily_expense)})
    
    context = {
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'net_balance': float(net_balance),
        'monthly_data': monthly_data,
        'category_expenses': category_expenses,
        'spending_trend': spending_trend,
        'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    }
    
    return render(request, 'finance/analytics.html', context)

@login_required
def reports(request):
    accounts = Account.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category_id = request.GET.get('category')
    account_id = request.GET.get('account')
    report_type = request.GET.get('report_type', 'all')
    
    # Base queryset
    transactions = Transaction.objects.filter(user=request.user)
    
    # Apply filters
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if account_id:
        transactions = transactions.filter(account_id=account_id)
    if report_type == 'income':
        transactions = transactions.filter(transaction_type='income')
    elif report_type == 'expense':
        transactions = transactions.filter(transaction_type='expense')
    
    # Calculate totals
    total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'transactions': transactions,
        'accounts': accounts,
        'categories': categories,
        'total_amount': total_amount,
        'start_date': start_date,
        'end_date': end_date,
        'selected_category': category_id,
        'selected_account': account_id,
        'report_type': report_type,
    }
    
    return render(request, 'finance/reports.html', context)

@login_required
def export_csv(request):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Category', 'Account', 'Amount', 'Description'])
    
    transactions = Transaction.objects.filter(user=request.user)
    
    for transaction in transactions:
        writer.writerow([
            transaction.date,
            transaction.transaction_type,
            transaction.category.name if transaction.category else 'Uncategorized',
            transaction.account.name,
            transaction.amount,
            transaction.description
        ])
    
    return response

@login_required
def manage_categories(request):
    categories = Category.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('manage_categories')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    
    return render(request, 'finance/categories.html', {
        'categories': categories,
        'form': form
    })
from flask import Flask, render_template, abort, redirect, render_template, url_for, request
from jinja2 import TemplateNotFound
import requests
import bank_service as bank


# SETUP FLASK

app = Flask(__name__)


# ROUTES ----------------------------------------------------------------------

@app.route("/", methods=('GET','POST'))
def home():
    return redirect(url_for('customers_page'))

@app.route("/customers/<customer_id>/payments", methods=['GET'])
def customer_payments(customer_id):
    payments = bank.get_customer_payments(customer_id = customer_id)
    customer = bank.get_customer_by_id(customer_id)
    return render_template("payments.html", payments=payments, customer=customer)

@app.route("/customers", methods=["GET"])
def customers_page():
    customers = bank.get_customers()
    return render_template('customers.html', customers=customers)

@app.route("/payments/<payment_id>", methods=["GET", "POST"])
def payment_page(payment_id : str):
    if request.method == 'POST':
        amount = request.form.get('amount')
        status = request.form.get('status')
        bank.update_payment(payment_id = payment_id, new_status = status, new_amount = amount)
    customer_id = bank.get_customer_from_payment(int(payment_id))
    return redirect(f'/customers/{customer_id}/payments')


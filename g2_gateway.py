import requests
import json
from client_urls import *
from http_params import *
from urllib.parse import urlencode
from urllib.request import urlretrieve
from utils import *

########################################################################################

def get_uline_token():
    headers = {
        CONTENT_TYPE: APPLICATION_JSON,
        AUTHORIZATION: BASIC
    }

    response = requests.request(POST, SECURITY_AUTH_URL, headers=headers, data=EMPTY)

    obj = create_object(response.text)

    if isHttpError(obj): 
        raise ConnectionError("Error getting bearer token")
    else: return obj.token
    

########################################################################################

STANDARD_HEADERS = {
        CONTENT_TYPE: APPLICATION_JSON,
        AUTHORIZATION: BEARER + " " + get_uline_token()
    }

########################################################################################

def get_order_number():
    response = requests.request(POST, ORDER_NUMBER_URL, headers=STANDARD_HEADERS, data="{}")
    obj = create_object(response.text)

    if isHttpError(obj):
        raise ConnectionError("Error getting new order number from order service")
    else: return obj.orderNumber + FIVE_BILLION

########################################################################################

def create_checkout_request(order_number, shipToCustomer, contact):
    payload = json.dumps({
        COMPANY_CODE: shipToCustomer.companyCode,
        CATALOG_CODE: FV_CC,
        SOURCE_APPLICATION: JOE_PHONE,
        ORDER_TYPE: WRITTEN_ORDER,
        BILL_TO_CUSTOMER_ID: shipToCustomer.billToId,
        SHIP_TO_CUSTOMER_ID: shipToCustomer.customerId,
        CONTACT_NAME: contact.contactName,
        ORDER_NUMBER: order_number,
        CUSTOMER_PURCHASE_ORDER_NUMBER: G2HOLD,
        KEEP_LOCKED: False,
        MEXICO_USAGE_CODE: POI,
        PAYMENT_TYPE: NET_30,
        AUTO_ASSIGN_NUM: False
    })

    response = requests.request(POST, OES_CHECKOUT_REQ_URL, headers=STANDARD_HEADERS, data=payload)
    obj = create_object(response.text)

    if isHttpError(obj):
        raise ConnectionError("Error creating checkout request for order number: " + str(order_number) + " and customer ID: " + str(shipToCustomer.customerId))
    else: return obj

########################################################################################    

def search_customer(address):
    url = CUSTOMER_SEARCH_URL
    url += generate_param(ADDRESS_LINE, address.get(ADDRESS_LINE1))
    url += generate_param(CITY, address.get(CITY))
    url += generate_param(POSTAL_CODE, address.get(ZIP))
    url += generate_param(STATE_PROV_CODE, address.get(STATE))
    url += generate_param(MARKED_DEL, False)

    response = requests.request(GET, url, headers=STANDARD_HEADERS)
    obj = create_object(response.text)

    if isHttpError(obj):
        raise ConnectionError("Error in customer search")
    else: return obj

######################################################################################## 
    
def search_contact(name, email):
    url = CONTACT_SEARCH_URL
    url += generate_param(NAME, name)
    url += generate_param(EMAIL, email)
    url += generate_param(CUST_MARKED_DEL, False)

    response = requests.request(GET, url, headers=STANDARD_HEADERS)
    obj = create_object(response.text)

    if isHttpError(obj):
        raise ConnectionError("Error in contact search")    
    else: return match_contact(name, email, obj)
    
########################################################################################

def add_line(cr_id, item_id, qty, ext_price):
    payload = json.dumps({
        LINES: [
            {
            ITEM_ID: item_id,
            PRODUCT_ID: None,
            SELLABLE_ORDERED_QTY: qty,
            EXT_PRICE: ext_price,
            RA_CODE: EMPTY
            }
        ]
        })

    response = requests.request(POST, OES_LINES_URL.format(cr_id), headers=STANDARD_HEADERS, data=payload)
    obj = create_object(response.text)

    if isHttpError(obj):
        raise ConnectionError("Error adding order line to checkout request: " + str(cr_id))
    else: return obj

########################################################################################    

def compute_order_summary(cr_id):
    response = requests.request(POST, OES_SUMMARY_URL.format(cr_id), headers=STANDARD_HEADERS, data="{}")
    obj = create_object(response.text)

    if isHttpError(obj): 
        raise ConnectionError("Error computing order summary for checkout request: " + str(cr_id))
    else: return obj

########################################################################################

def line_preperation(model_number, quantity):
    payload = json.dumps({
        COMPANY_CODE : US_COMP_CODE,
        MODEL_NUM : model_number,
        QTY : quantity,
        RA_CODE : EMPTY
    })
    response = requests.request(POST, OES_LINE_PREP_URL, headers=STANDARD_HEADERS, data=payload)
    obj = create_object(response.text)

    if isHttpError(obj):
        raise ConnectionError("Error preparing line information for model number: " + str(model_number))
    else: return obj

########################################################################################

def submit_checkout_request(order_number, cr_id, shipToCustomer, contact):
    payload = json.dumps({
        BILL_TO_CUSTOMER_ID: shipToCustomer.billToId,
        CONTACT_ID: contact.contactId,
        CONTACT_NAME: contact.contactName,
        CONTACT_EMAIL: contact.emailAddress,
        CONTACT_MOBILE: EMPTY,
        SHIP_TO_CUSTOMER_ID: shipToCustomer.customerId,
        SHIP_TO_NAME: shipToCustomer.customerName,
        SHIP_TO_ADD1: shipToCustomer.address.addressLine1,
        SHIP_TO_ADD2: shipToCustomer.address.addressLine2,
        SHIP_TO_CITY: shipToCustomer.address.city,
        SHIP_TO_STATE: shipToCustomer.address.state,
        SHIP_TO_POSTAL: shipToCustomer.address.zipCode,
        SHIP_TO_EXT: int(shipToCustomer.address.zipPlusFourCode),
        SHIP_TO_COUNTRY: shipToCustomer.address.countryCode,
        PAYMENT_TYPE: NET_30,
        TAX_OVERRIDE: True,
        SOURCE_APPLICATION: JOE_PHONE,
        SOURCE_CODE: FTWEB,
        MEXICO_USAGE_CODE: EMPTY,
        SUBMISSION_MODE: PARALLEL,
        KEEP_LOCKED: False,
        'receivingHoursEnd': '12:00'
    })
    print(payload)
    response = requests.request(POST, OES_SUBMIT_URL.format(order_number, cr_id), headers=STANDARD_HEADERS, data=payload)
    obj = create_object(response.text)

    if isHttpError(obj):
        raise ConnectionError("Error submitting checkout request: " + str(cr_id) + " with order number: " + str(order_number))
    else: return obj

########################################################################################
   
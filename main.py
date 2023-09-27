import stripe
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import kafka

stripe.api_key = "sk_test_51NuYdUSFJMuMs1DNf3hHMmDBEDzBV5tbkvNH3p9EmbsoFwpiGSvENd6mL7rE6UnzT5dDXq0WVPZ0ugOrlpgTgMwr00iGLFYXhm"  # Replace with your actual Stripe API key

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = 'whsec_DdfpVCN5OJSpwAo4QOCDqhekHCeAmYDF'

app = FastAPI()

@app.get('/')
async def home():
    return "Server is working."

@app.post('/')
async def webhook(request: Request):
    event = None
    payload = await request.body()
    sig_header = request.headers['Stripe-Signature']
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'customer.created':
        customer = event['data']['object']
        kafka.send_to_kafka(
            "customer-events",
            {"event_type": "stripe_customer_created", "customer": customer},
        )

    elif event['type'] == 'customer.deleted':
        customer = event['data']['object']
        # This is not created yet.
        
    elif event['type'] == 'customer.updated':
        customer = event['data']['object']
        kafka.send_to_kafka(
            "customer-events",
            {"event_type": "stripe_customer_updated", "customer": customer},
        )
        
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event['type']))

    return JSONResponse(content={"success": True})

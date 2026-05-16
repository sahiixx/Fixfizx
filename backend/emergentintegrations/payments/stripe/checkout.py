"""Mock Stripe checkout module."""

class StripeCheckout:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "mock-key"

    async def create_session(self, **kwargs):
        return {"id": "mock_session", "url": "https://mock.stripe.com/checkout"}

    async def get_session(self, session_id: str):
        return {"id": session_id, "status": "complete"}

class StripeWebhook:
    def __init__(self, webhook_secret: str = None):
        self.webhook_secret = webhook_secret or "mock-secret"

    def construct_event(self, payload: bytes, sig_header: str):
        return {"type": "checkout.session.completed", "data": {"object": {"id": "mock"}}}

class CheckoutSessionResponse:
    id: str = "mock"
    url: str = "https://mock.stripe.com/checkout"
    status: str = "open"

class CheckoutStatusResponse:
    id: str = "mock"
    status: str = "complete"
    payment_status: str = "paid"

class CheckoutSessionRequest:
    price_id: str = "mock_price"
    quantity: int = 1
    success_url: str = "https://example.com/success"
    cancel_url: str = "https://example.com/cancel"

StripeCheckoutSession = StripeCheckout

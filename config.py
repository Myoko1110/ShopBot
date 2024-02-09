TOKEN = ""

# 管理系
LOG_CHANNEL_ID = 0
ADMIN_ROLE_ID = 0

# チケット系
TICKET_CATEGORY_ID = 0
TICKET_CHANNEL_NAME = "チケット-{username}"
TICKET_COMPLETED_ROLE_ID = 0
TICKET_REQUESTING_ROLE = 0

# 保存系
TICKET_DATA_PATH = "plugins/new/data/tickets.yml"
REQUEST_DATA_PATH = "plugins/new/data/requests.yml"
COMPLETE_BUTTON_DATA_PATH = "plugins/new/data/complete_button.yml"
GIVEAWAY_DATA_PATH = "plugins/giveaway/data/giveaway.yml"
SLOT_DATA_PATH = "plugins/slot/data/slots.yml"
VERIFY_DATA_PATH = "plugins/verify/data/verify_buttons.yml"

# スロット系
SLOT_CATEGORY_ID = 0
SLOT_CHANNEL_NAME = "🎰￤{username}{expiry}"
SLOT_MUTUAL_CATEGORY_ID = 0
SLOT_MUTUAL_CHANNEL_NAME = "相互-{username}"

# 自動販売機系
VENDING_PRODUCTS = [
    {
        "name": "あいうえお",
        "price": 1.0,
        "file_path": "main.py"
    }
]

MODAL_MODE = False

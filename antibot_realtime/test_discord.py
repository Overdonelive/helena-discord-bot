import requests

webhook = "https://discord.com/api/webhooks/1481387029127364669/W0dwWiKngktkIJv9jy7MSDIBQ5I80xUFUowDRFdfL16q2Y53dcOPnaIYY_OL2q8uNd5s"

role_id = "1407739499454271610"

data = {
    "content": f"<@&{role_id}> 🚨 TESTE DO SISTEMA ANTIBOT 🚨",
    "allowed_mentions": {
        "roles": [role_id]
    }
}

r = requests.post(webhook, json=data)

print("Status:", r.status_code)
print("Resposta:", r.text)
#!/usr/bin/env python3
"""
Vapi Phone Integration Setup — Ghost Agents.

Provides:
1. Vapi assistant configs for all 5 ghost systems
2. Webhook handlers for call events
3. Integration with existing ghost quote generators

Requires:
- Vapi account (dashboard.vapi.ai)
- Phone number purchase (~$1-3/mo per number)
- API key
"""
import json
import os
from typing import Dict, Any

VAPI_API_KEY = os.environ.get("VAPI_API_KEY", "YOUR_VAPI_KEY")


def create_locksmith_assistant() -> Dict[str, Any]:
    """Vapi assistant config for locksmith ghost."""
    return {
        "name": "Locksmith Ghost — Aria",
        "voice": {
            "provider": "11labs",
            "voiceId": "aria",
            "settings": {"stability": 0.5, "similarityBoost": 0.75}
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        },
        "firstMessage": "Thank you for calling [Business Name] Locksmith. I'm Aria, your virtual assistant. Are you calling for a lockout, key replacement, or security upgrade?",
        "endCallMessage": "Thank you for choosing [Business Name]. Help is on the way!",
        "functions": [
            {
                "name": "bookAppointment",
                "description": "Book a locksmith visit",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customerName": {"type": "string"},
                        "phone": {"type": "string"},
                        "address": {"type": "string"},
                        "serviceType": {"enum": ["lockout", "key_replacement", "security_upgrade", "repair"]},
                        "urgency": {"enum": ["emergency", "same_day", "scheduled"]},
                        "propertyType": {"enum": ["residential", "commercial", "automotive"]}
                    },
                    "required": ["customerName", "phone", "address", "serviceType", "urgency"]
                }
            },
            {
                "name": "sendTextSummary",
                "description": "Send job details to locksmith via SMS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "technicianPhone": {"type": "string"},
                        "customerName": {"type": "string"},
                        "address": {"type": "string"},
                        "issue": {"type": "string"},
                        "urgency": {"type": "string"},
                        "appointmentTime": {"type": "string"}
                    }
                }
            }
        ],
        "serverUrl": "https://your-server.com/vapi/webhook/locksmith",
        "analysisPlan": {
            "summaryPrompt": "Summarize the locksmith call. What service was needed? Was it booked?",
            "structuredDataPrompt": "Extract: customer_name, phone, address, service_type, urgency, property_type, booked (true/false)"
        }
    }


def create_electrical_assistant() -> Dict[str, Any]:
    """Vapi assistant config for electrical ghost."""
    return {
        "name": "Electrical Ghost — Aria",
        "voice": {
            "provider": "11labs",
            "voiceId": "aria",
            "settings": {"stability": 0.5, "similarityBoost": 0.75}
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        },
        "firstMessage": "Thank you for calling [Business Name] Electrical. I'm Aria, your virtual assistant. Are you experiencing a power outage, need new installations, or have an electrical emergency?",
        "endCallMessage": "Thank you for calling [Business Name]. Your electrical issue will be resolved promptly!",
        "functions": [
            {
                "name": "bookAppointment",
                "description": "Book electrical service visit",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customerName": {"type": "string"},
                        "phone": {"type": "string"},
                        "address": {"type": "string"},
                        "serviceType": {"enum": ["power_outage", "installation", "repair", "inspection", "emergency"]},
                        "urgency": {"enum": ["emergency", "same_day", "scheduled"]},
                        "propertyType": {"enum": ["residential", "commercial", "industrial"]}
                    },
                    "required": ["customerName", "phone", "address", "serviceType", "urgency"]
                }
            },
            {
                "name": "sendTextSummary",
                "description": "Send job details to electrician",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "technicianPhone": {"type": "string"},
                        "customerName": {"type": "string"},
                        "address": {"type": "string"},
                        "issue": {"type": "string"},
                        "urgency": {"type": "string"},
                        "appointmentTime": {"type": "string"}
                    }
                }
            }
        ],
        "serverUrl": "https://your-server.com/vapi/webhook/electrical",
        "analysisPlan": {
            "summaryPrompt": "Summarize the electrical call. What was the issue? Was it booked?",
            "structuredDataPrompt": "Extract: customer_name, phone, address, issue_type, urgency, property_type, booked"
        }
    }


def create_plumbing_assistant() -> Dict[str, Any]:
    """Vapi assistant config for plumbing ghost."""
    return {
        "name": "Plumbing Ghost — Aria",
        "voice": {
            "provider": "11labs",
            "voiceId": "aria",
            "settings": {"stability": 0.5, "similarityBoost": 0.75}
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        },
        "firstMessage": "Thank you for calling [Business Name] Plumbing. I'm Aria, your virtual assistant. Is this a burst pipe, leak, drainage issue, or routine service?",
        "endCallMessage": "Thank you for calling [Business Name]. A plumber will be with you shortly!",
        "functions": [
            {
                "name": "bookAppointment",
                "description": "Book plumbing service",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customerName": {"type": "string"},
                        "phone": {"type": "string"},
                        "address": {"type": "string"},
                        "serviceType": {"enum": ["burst_pipe", "leak", "drainage", "installation", "routine"]},
                        "urgency": {"enum": ["emergency", "same_day", "scheduled"]},
                        "propertyType": {"enum": ["residential", "commercial", "industrial"]}
                    },
                    "required": ["customerName", "phone", "address", "serviceType", "urgency"]
                }
            },
            {
                "name": "sendTextSummary",
                "description": "Send job details to plumber",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "technicianPhone": {"type": "string"},
                        "customerName": {"type": "string"},
                        "address": {"type": "string"},
                        "issue": {"type": "string"},
                        "urgency": {"type": "string"},
                        "appointmentTime": {"type": "string"}
                    }
                }
            }
        ],
        "serverUrl": "https://your-server.com/vapi/webhook/plumbing"
    }


def create_roofing_assistant() -> Dict[str, Any]:
    """Vapi assistant config for roofing ghost."""
    return {
        "name": "Roofing Ghost — Aria",
        "voice": {
            "provider": "11labs",
            "voiceId": "aria",
            "settings": {"stability": 0.5, "similarityBoost": 0.75}
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        },
        "firstMessage": "Thank you for calling [Business Name] Roofing. I'm Aria, your virtual assistant. Is this a leak, storm damage, inspection, or new installation?",
        "endCallMessage": "Thank you for calling [Business Name]. Your roof will be taken care of!",
        "functions": [
            {
                "name": "bookAppointment",
                "description": "Book roofing service",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customerName": {"type": "string"},
                        "phone": {"type": "string"},
                        "address": {"type": "string"},
                        "serviceType": {"enum": ["leak", "storm_damage", "inspection", "installation", "repair"]},
                        "urgency": {"enum": ["emergency", "same_day", "scheduled"]},
                        "propertyType": {"enum": ["residential", "commercial", "industrial"]}
                    },
                    "required": ["customerName", "phone", "address", "serviceType", "urgency"]
                }
            },
            {
                "name": "sendTextSummary",
                "description": "Send job details to roofer",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "technicianPhone": {"type": "string"},
                        "customerName": {"type": "string"},
                        "address": {"type": "string"},
                        "issue": {"type": "string"},
                        "urgency": {"type": "string"},
                        "appointmentTime": {"type": "string"}
                    }
                }
            }
        ],
        "serverUrl": "https://your-server.com/vapi/webhook/roofing"
    }


def create_towing_assistant() -> Dict[str, Any]:
    """Vapi assistant config for towing ghost."""
    return {
        "name": "Towing Ghost — Aria",
        "voice": {
            "provider": "11labs",
            "voiceId": "aria",
            "settings": {"stability": 0.5, "similarityBoost": 0.75}
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7
        },
        "firstMessage": "Thank you for calling [Business Name] Towing. I'm Aria, your virtual assistant. What's your location and vehicle type? Is this a breakdown or accident?",
        "endCallMessage": "Help is on the way! Stay safe and we'll be there soon.",
        "functions": [
            {
                "name": "dispatchTow",
                "description": "Dispatch tow truck",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customerName": {"type": "string"},
                        "phone": {"type": "string"},
                        "location": {"type": "string"},
                        "vehicleType": {"enum": ["car", "suv", "truck", "motorcycle", "van"]},
                        "issue": {"enum": ["breakdown", "accident", "flat_tire", "locked_out", "out_of_fuel"]},
                        "destination": {"type": "string"}
                    },
                    "required": ["customerName", "phone", "location", "vehicleType", "issue"]
                }
            },
            {
                "name": "sendTextSummary",
                "description": "Send dispatch details to driver",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "driverPhone": {"type": "string"},
                        "customerName": {"type": "string"},
                        "location": {"type": "string"},
                        "vehicleType": {"type": "string"},
                        "issue": {"type": "string"},
                        "destination": {"type": "string"}
                    }
                }
            }
        ],
        "serverUrl": "https://your-server.com/vapi/webhook/towing"
    }


def save_all_configs():
    """Save all Vapi assistant configs to JSON files."""
    configs = {
        "locksmith": create_locksmith_assistant(),
        "electrical": create_electrical_assistant(),
        "plumbing": create_plumbing_assistant(),
        "roofing": create_roofing_assistant(),
        "towing": create_towing_assistant(),
    }
    
    for name, config in configs.items():
        filename = f"/home/sahiix/Fixfizx/backend/vapi_{name}_assistant.json"
        with open(filename, "w") as f:
            json.dump(config, f, indent=2)
        print(f"✅ Saved: {filename}")
    
    return configs


if __name__ == "__main__":
    configs = save_all_configs()
    print(f"\n🎯 Created {len(configs)} Vapi assistant configs")
    print("\nNext steps:")
    print("1. Sign up at dashboard.vapi.ai")
    print("2. Get API key")
    print("3. Purchase phone numbers ($1-3/mo each)")
    print("4. Upload assistant JSON files")
    print("5. Set webhook URL to your server")

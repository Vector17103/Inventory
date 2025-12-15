# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 22:17:52 2025

@author: Achyut Niroula
"""

import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cosc-4206-default-rtdb.firebaseio.com/'
})

# Sample landscaping store inventory
items = [
    {"name": "Maple Tree", "quantity": 10, "price": 120, "category": "Plants & Trees"},
    {"name": "Oak Sapling", "quantity": 15, "price": 90, "category": "Plants & Trees"},
    {"name": "Cedar Hedge (3 ft)", "quantity": 25, "price": 45, "category": "Plants & Trees"},
    {"name": "Rose Bush", "quantity": 40, "price": 25, "category": "Plants & Trees"},
    {"name": "Hydrangea Shrub", "quantity": 30, "price": 35, "category": "Plants & Trees"},
    {"name": "Topsoil (40 lb bag)", "quantity": 80, "price": 6, "category": "Soil, Mulch & Fertilizer"},
    {"name": "Potting Mix (20 lb bag)", "quantity": 60, "price": 8, "category": "Soil, Mulch & Fertilizer"},
    {"name": "Mulch (Cedar)", "quantity": 100, "price": 7, "category": "Soil, Mulch & Fertilizer"},
    {"name": "Compost (Organic)", "quantity": 50, "price": 10, "category": "Soil, Mulch & Fertilizer"},
    {"name": "Grass Seed (Sun & Shade mix)", "quantity": 30, "price": 20, "category": "Soil, Mulch & Fertilizer"},
    {"name": "River Rock (per bag)", "quantity": 40, "price": 12, "category": "Stone, Gravel & Pavers"},
    {"name": "Patio Pavers (12x12 inch)", "quantity": 200, "price": 4, "category": "Stone, Gravel & Pavers"},
    {"name": "Retaining Wall Blocks", "quantity": 150, "price": 6, "category": "Stone, Gravel & Pavers"},
    {"name": "Shovel (Round Point)", "quantity": 20, "price": 25, "category": "Tools & Equipment"},
    {"name": "Rake (Garden)", "quantity": 30, "price": 18, "category": "Tools & Equipment"},
    {"name": "Wheelbarrow (6 cu ft)", "quantity": 10, "price": 120, "category": "Tools & Equipment"},
    {"name": "Garden Hose (50 ft)", "quantity": 25, "price": 30, "category": "Irrigation & Watering"},
    {"name": "Sprinkler (Oscillating)", "quantity": 15, "price": 35, "category": "Irrigation & Watering"},
    {"name": "Drip Irrigation Kit", "quantity": 10, "price": 60, "category": "Irrigation & Watering"},
    {"name": "Planters (Ceramic)", "quantity": 50, "price": 20, "category": "Outdoor Décor & Accessories"},
    {"name": "Garden Statues", "quantity": 15, "price": 45, "category": "Outdoor Décor & Accessories"},
    {"name": "Bird Bath", "quantity": 10, "price": 70, "category": "Outdoor Décor & Accessories"},
    {"name": "Snow Shovel", "quantity": 30, "price": 25, "category": "Seasonal Items"},
    {"name": "Ice Melt (20 lb bag)", "quantity": 40, "price": 12, "category": "Seasonal Items"},
    {"name": "Firewood Bundles", "quantity": 50, "price": 10, "category": "Seasonal Items"}
]

# Push items to Firebase
ref = db.reference('inventory')
for item in items:
    ref.push(item)

print("Database seeded successfully with landscaping inventory!")

# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 18:45:49 2025

@author: Achyut Niroula
"""

import firebase_admin
from firebase_admin import credentials, auth

# Initialize Admin SDK (same as in app.py)
cred = credentials.Certificate("cosc-4607-firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

# Replace with the UID of the user you want to promote
uid = "KB6rPYLaG8Mm5zgSfyVgiP0Hgqz2"

# Set custom claim
auth.set_custom_user_claims(uid, {"role": "admin"})

print(f"Role 'admin' set for UID: {uid}")

# Replace with the UID of the user you want to promote
uid1 = "BhWeFHt4YoSmlxYkJUtYOb9JOS93"

# Set custom claim
auth.set_custom_user_claims(uid, {"role": "editor"})

print(f"Role 'admin' set for UID: {uid1}")
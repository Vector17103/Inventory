package com.achyut.cloudchat.cloud_chat;

import com.google.firebase.FirebaseApp;
import com.google.firebase.FirebaseOptions;
import com.google.auth.oauth2.GoogleCredentials;
import java.io.FileInputStream;

public class FirebaseTest {
    public static void main(String[] args) throws Exception {
        // Load service account key
        FileInputStream serviceAccount = new FileInputStream("cosc-3657-firebase-adminsdk.json");

        // Configure Firebase
        FirebaseOptions options = new FirebaseOptions.Builder()
            .setCredentials(GoogleCredentials.fromStream(serviceAccount))
            .setDatabaseUrl("https://cosc-3657-default-rtdb.firebaseio.com/")
            .build();

        // Initialize Firebase
        FirebaseApp.initializeApp(options);

        System.out.println("Firebase initialized successfully!");
    }
}




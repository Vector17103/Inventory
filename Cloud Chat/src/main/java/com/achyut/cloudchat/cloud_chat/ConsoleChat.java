package com.achyut.cloudchat.cloud_chat;

import com.google.firebase.FirebaseApp;
import com.google.firebase.FirebaseOptions;
import com.google.firebase.database.*;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.api.core.ApiFuture;
import com.google.api.core.ApiFutureCallback;
import com.google.api.core.ApiFutures;
import com.google.common.util.concurrent.MoreExecutors;

import java.io.FileInputStream;
import java.util.Scanner;

public class ConsoleChat {
    public static void main(String[] args) throws Exception {
        // Initialization of Firebase with service account
        FileInputStream serviceAccount = new FileInputStream("cosc-3657-firebase-adminsdk.json");

        FirebaseOptions options = new FirebaseOptions.Builder()
                .setCredentials(GoogleCredentials.fromStream(serviceAccount))
                .setDatabaseUrl("https://cosc-3657-default-rtdb.firebaseio.com/")
                .build();

        FirebaseApp.initializeApp(options);

        // Reference to chatrooms/general
        DatabaseReference chatRef = FirebaseDatabase.getInstance()
                .getReference("chatrooms")
                .child("general");

        // Listening for new messages
        chatRef.addChildEventListener(new ChildEventListener() {
            @Override
            public void onChildAdded(DataSnapshot snapshot, String prevChildKey) {
                System.out.println(snapshot.getValue(String.class));
            }

            @Override
            public void onChildChanged(DataSnapshot snapshot, String prevChildKey) {
                // Optional: handle message edits
            }

            @Override
            public void onChildRemoved(DataSnapshot snapshot) {
                // Optional: handle message deletions
            }

            @Override
            public void onChildMoved(DataSnapshot snapshot, String prevChildKey) {
                // Optional: handle reordering
            }

            @Override
            public void onCancelled(DatabaseError error) {
                // Error handling for listener failures
                System.err.println("Listener cancelled: " + error.getMessage());
            }
        });

        // Console input loop
        Scanner scanner = new Scanner(System.in);
        System.out.println("Enter your name:");
        String username = scanner.nextLine();

        System.out.println("Start chatting! Type messages below:");
        while (true) {
            String msg = scanner.nextLine();

            // Pushing message asynchronously with error callbacks
            ApiFuture<Void> future = chatRef.push().setValueAsync(username + ": " + msg);

            ApiFutures.addCallback(future, new ApiFutureCallback<Void>() {
                @Override
                public void onSuccess(Void result) {
                    System.out.println("Message sent successfully!");
                }

                @Override
                public void onFailure(Throwable t) {
                    System.err.println("Failed to send message: " + t.getMessage());
                }
            }, MoreExecutors.directExecutor());
        }
    }
}

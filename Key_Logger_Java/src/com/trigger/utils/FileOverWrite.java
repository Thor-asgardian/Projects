package com.trigger.utils;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

public class FileOverWrite implements FileContract {
    private BufferedWriter writer;

    @Override
    public void initWriter(String fileName) {
        try {
            writer = new BufferedWriter(new FileWriter(fileName, true)); // true for append mode
        } catch (IOException e) {
            System.err.println("Error initializing writer: " + e.getMessage());
        }
    }

    @Override
    public void writeToFile(String content) {
        try {
            if (writer != null) {
                writer.write(content);
                writer.flush();
            }
        } catch (IOException e) {
            System.err.println("Error writing to file: " + e.getMessage());
        }
    }

    @Override
    public void closeWriter() {
        try {
            if (writer != null) {
                writer.close();
            }
        } catch (IOException e) {
            System.err.println("Error closing writer: " + e.getMessage());
        }
    }
}

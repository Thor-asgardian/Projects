package com.trigger.utils;

public interface FileContract {
    void initWriter(String fileName);
    void writeToFile(String content);
    void closeWriter();
}

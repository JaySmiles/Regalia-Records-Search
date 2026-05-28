package com.jaysmiles.regaliarecords.export;

import android.content.ContentResolver;
import android.content.ContentValues;
import android.net.Uri;
import android.os.Environment;
import android.util.Base64;

import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.PluginMethod;

import android.provider.MediaStore;

import java.io.OutputStream;

@CapacitorPlugin(name = "FileExporter")
public class FileExporterPlugin extends Plugin {

    @PluginMethod
    public void saveFile(PluginCall call) {

        String base64 = call.getString("base64");
        String filename = call.getString("filename");
        String folder = call.getString("folder");

        try {

            byte[] data = Base64.decode(base64, Base64.DEFAULT);

            ContentValues values = new ContentValues();
            values.put(MediaStore.MediaColumns.DISPLAY_NAME, filename);
            values.put(MediaStore.MediaColumns.MIME_TYPE,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");

            if ("documents".equals(folder)) {
                values.put(MediaStore.MediaColumns.RELATIVE_PATH,
                        Environment.DIRECTORY_DOCUMENTS);
            } else {
                values.put(MediaStore.MediaColumns.RELATIVE_PATH,
                        Environment.DIRECTORY_DOWNLOADS);
            }

            ContentResolver resolver = getContext().getContentResolver();

            Uri uri = resolver.insert(
                    MediaStore.Files.getContentUri("external"),
                    values
            );

            OutputStream output = resolver.openOutputStream(uri);
            output.write(data);
            output.close();

            call.resolve();

        } catch (Exception e) {
            call.reject("File save failed: " + e.getMessage());
        }
    }
}

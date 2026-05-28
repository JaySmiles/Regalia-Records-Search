package com.jaysmiles.regaliarecords;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;
import com.jaysmiles.regaliarecords.export.FileExporterPlugin;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(FileExporterPlugin.class);
        super.onCreate(savedInstanceState);
    }

}

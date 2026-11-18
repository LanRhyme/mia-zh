package dev.lanrhyme.miazh;

import net.fabricmc.api.ClientModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class MiaZhClient implements ClientModInitializer {
    public static final Logger LOG = LoggerFactory.getLogger("mia-zh");

    @Override
    public void onInitializeClient() {
        Translator.get().bootstrap();
    }
}

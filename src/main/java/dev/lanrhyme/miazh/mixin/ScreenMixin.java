package dev.lanrhyme.miazh.mixin;

import dev.lanrhyme.miazh.Translator;
import net.minecraft.client.gui.screen.Screen;
import net.minecraft.text.Text;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 容器 / 菜单标题 */
@Mixin(Screen.class)
public class ScreenMixin {

    @Inject(method = "getTitle", at = @At("RETURN"), cancellable = true)
    private void miazh$getTitle(CallbackInfoReturnable<Text> cir) {
        cir.setReturnValue(Translator.get().translate(cir.getReturnValue()));
    }
}

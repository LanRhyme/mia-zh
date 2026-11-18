package dev.lanrhyme.miazh.mixin;

import dev.lanrhyme.miazh.Translator;
import net.minecraft.client.gui.hud.InGameHud;
import net.minecraft.text.Text;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** 屏幕中央大标题 / 副标题 / 动作栏 */
@Mixin(InGameHud.class)
public class InGameHudMixin {

    @ModifyVariable(method = "setTitle(Lnet/minecraft/text/Text;)V", at = @At("HEAD"), argsOnly = true)
    private Text miazh$setTitle(Text title) {
        return Translator.get().translate(title);
    }

    @ModifyVariable(method = "setSubtitle(Lnet/minecraft/text/Text;)V", at = @At("HEAD"), argsOnly = true)
    private Text miazh$setSubtitle(Text subtitle) {
        return Translator.get().translate(subtitle);
    }

    @ModifyVariable(method = "setOverlayMessage(Lnet/minecraft/text/Text;Z)V", at = @At("HEAD"), argsOnly = true, index = 1)
    private Text miazh$setOverlay(Text message) {
        return Translator.get().translate(message);
    }
}

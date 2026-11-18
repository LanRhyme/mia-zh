package dev.lanrhyme.miazh.mixin;

import dev.lanrhyme.miazh.Translator;
import net.minecraft.entity.boss.BossBar;
import net.minecraft.text.Text;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** BOSS 血条标题 */
@Mixin(BossBar.class)
public class BossBarMixin {

    @Inject(method = "getName", at = @At("RETURN"), cancellable = true)
    private void miazh$getName(CallbackInfoReturnable<Text> cir) {
        cir.setReturnValue(Translator.get().translate(cir.getReturnValue()));
    }
}

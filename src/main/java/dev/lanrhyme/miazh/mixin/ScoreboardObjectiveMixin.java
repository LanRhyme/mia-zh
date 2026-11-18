package dev.lanrhyme.miazh.mixin;

import dev.lanrhyme.miazh.Translator;
import net.minecraft.scoreboard.ScoreboardObjective;
import net.minecraft.text.Text;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 计分板目标标题 */
@Mixin(ScoreboardObjective.class)
public class ScoreboardObjectiveMixin {

    @Inject(method = "getDisplayName", at = @At("RETURN"), cancellable = true)
    private void miazh$getDisplayName(CallbackInfoReturnable<Text> cir) {
        cir.setReturnValue(Translator.get().translate(cir.getReturnValue()));
    }
}

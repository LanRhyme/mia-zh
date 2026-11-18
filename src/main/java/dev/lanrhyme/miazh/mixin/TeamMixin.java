package dev.lanrhyme.miazh.mixin;

import dev.lanrhyme.miazh.Translator;
import net.minecraft.scoreboard.Team;
import net.minecraft.text.MutableText;
import net.minecraft.text.Text;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 计分板侧栏：标题（队伍前后缀 + 内容整行） */
@Mixin(Team.class)
public class TeamMixin {

    @Inject(method = "getDisplayName", at = @At("RETURN"), cancellable = true)
    private void miazh$getDisplayName(CallbackInfoReturnable<Text> cir) {
        cir.setReturnValue(Translator.get().translate(cir.getReturnValue()));
    }

    @Inject(method = "getPrefix", at = @At("RETURN"), cancellable = true)
    private void miazh$getPrefix(CallbackInfoReturnable<Text> cir) {
        cir.setReturnValue(Translator.get().translate(cir.getReturnValue()));
    }

    @Inject(method = "getSuffix", at = @At("RETURN"), cancellable = true)
    private void miazh$getSuffix(CallbackInfoReturnable<Text> cir) {
        cir.setReturnValue(Translator.get().translate(cir.getReturnValue()));
    }

    @Inject(method = "decorateName", at = @At("RETURN"), cancellable = true)
    private void miazh$decorateName(Text name, CallbackInfoReturnable<MutableText> cir) {
        Text translated = Translator.get().translate(cir.getReturnValue());
        cir.setReturnValue(translated instanceof MutableText mutable ? mutable : Text.empty().append(translated));
    }
}

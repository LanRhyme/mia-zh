package dev.lanrhyme.miazh.mixin;

import dev.lanrhyme.miazh.Translator;
import net.minecraft.entity.Entity;
import net.minecraft.text.Text;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 生物名牌 / 实体显示名 */
@Mixin(Entity.class)
public class EntityMixin {

    @Inject(method = "getDisplayName", at = @At("RETURN"), cancellable = true)
    private void miazh$getDisplayName(CallbackInfoReturnable<Text> cir) {
        cir.setReturnValue(Translator.get().translate(cir.getReturnValue()));
    }
}

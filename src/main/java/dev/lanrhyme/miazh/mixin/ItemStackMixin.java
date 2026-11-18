package dev.lanrhyme.miazh.mixin;

import dev.lanrhyme.miazh.Translator;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.item.tooltip.TooltipType;
import net.minecraft.text.Text;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.List;

/** 物品名 + tooltip（名称、lore、属性行） */
@Mixin(ItemStack.class)
public class ItemStackMixin {

    @Inject(method = "getName", at = @At("RETURN"), cancellable = true)
    private void miazh$getName(CallbackInfoReturnable<Text> cir) {
        cir.setReturnValue(Translator.get().translate(cir.getReturnValue()));
    }

    @Inject(method = "getTooltip", at = @At("RETURN"))
    private void miazh$getTooltip(Item.TooltipContext context, PlayerEntity player, TooltipType type,
                                  CallbackInfoReturnable<List<Text>> cir) {
        List<Text> lines = cir.getReturnValue();
        if (lines == null || lines.isEmpty()) {
            return;
        }
        List<Text> translated = Translator.get().translate(lines);
        if (translated == lines) {
            return;
        }
        try {
            lines.clear();
            lines.addAll(translated);
        } catch (UnsupportedOperationException e) {
            cir.setReturnValue(translated);
        }
    }
}

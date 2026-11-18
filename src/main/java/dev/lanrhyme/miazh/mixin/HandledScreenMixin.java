package dev.lanrhyme.miazh.mixin;

import dev.lanrhyme.miazh.Translator;
import net.minecraft.client.gui.screen.ingame.HandledScreen;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.item.tooltip.TooltipType;
import net.minecraft.screen.slot.Slot;
import net.minecraft.text.Text;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 兜底采集：打开背包 / 箱子 / 末影箱等容器时，把里面所有物品的名称与 lore
 * 以英文原文写进 harvest，这样不用逐个悬停也能把库存里的文案一次性收集齐。
 */
@Mixin(HandledScreen.class)
public class HandledScreenMixin {

    @Inject(method = "init", at = @At("RETURN"))
    private void miazh$scanContainer(CallbackInfo ci) {
        try {
            Translator translator = Translator.get();
            HandledScreen<?> self = (HandledScreen<?>) (Object) this;
            translator.beginRecording();
            try {
                for (Slot slot : self.getScreenHandler().slots) {
                    try {
                        ItemStack stack = slot.getStack();
                        if (stack == null || stack.isEmpty()) {
                            continue;
                        }
                        translator.recordRaw(stack.getName().getString());
                        for (Text line : stack.getTooltip(Item.TooltipContext.DEFAULT, null, TooltipType.BASIC)) {
                            translator.recordRaw(line.getString());
                        }
                    } catch (Throwable ignored) {
                        // 单个物品失败不影响其它格子
                    }
                }
            } finally {
                translator.endRecording();
            }
        } catch (Throwable ignored) {
            // 采集失败绝不能影响界面
        }
    }
}

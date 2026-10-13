package zako.opt.mixin.block;

import net.caffeinemc.mods.sodium.client.render.frapi.render.AbstractBlockRenderContext;
import net.caffeinemc.mods.sodium.client.world.LevelSlice;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import zako.opt.block.LeafCulling;
import zako.opt.feature.Features;

// NeoForge 1.21.1 variant: Sodium 0.8 for 1.21.1 keeps the context in frapi.render and calls the check isFaceCulled
@Mixin(value = AbstractBlockRenderContext.class, remap = false)
public abstract class SodiumLeafCullMixin {
	@Shadow
	protected LevelSlice slice;
	@Shadow
	protected BlockState state;
	@Shadow
	protected BlockPos pos;

	@Inject(require = 0, method = "isFaceCulled", at = @At("HEAD"), cancellable = true)
	private void zakoopt$innerLeaves(Direction facing, CallbackInfoReturnable<Boolean> cir) {
		if (Features.LEAF_CULL.on && facing != null && slice != null && LeafCulling.hidden(state, slice, pos, facing)) {
			cir.setReturnValue(true);
		}
	}
}

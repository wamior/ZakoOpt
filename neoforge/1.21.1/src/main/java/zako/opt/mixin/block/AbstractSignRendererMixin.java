package zako.opt.mixin.block;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import net.minecraft.client.renderer.blockentity.SignRenderer;
import net.minecraft.client.resources.model.Material;
import net.minecraft.world.level.block.state.properties.WoodType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import zako.opt.feature.Features;

import java.util.IdentityHashMap;
import java.util.Map;

// NeoForge 1.21.1 variant: there is no AbstractSignRenderer here, SignRenderer holds the code.
// Only the material lookup is cached (the rest of the 1.21.4 sign work has no matching call sites in 1.21.1).
@Mixin(SignRenderer.class)
public abstract class AbstractSignRendererMixin {
	@Unique
	private final Map<WoodType, Material> zakoopt$materials = new IdentityHashMap<>();

	@WrapOperation(method = "renderSign", at = @At(value = "INVOKE", target = "Lnet/minecraft/client/renderer/blockentity/SignRenderer;getSignMaterial(Lnet/minecraft/world/level/block/state/properties/WoodType;)Lnet/minecraft/client/resources/model/Material;"))
	private Material zakoopt$material(SignRenderer renderer, WoodType wood, Operation<Material> original) {
		if (!Features.SIGN_CACHE.on) {
			return original.call(renderer, wood);
		}
		return zakoopt$materials.computeIfAbsent(wood, w -> original.call(renderer, w));
	}
}

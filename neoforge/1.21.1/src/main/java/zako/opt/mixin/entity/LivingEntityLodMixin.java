package zako.opt.mixin.entity;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import zako.opt.entity.EntityLod;

// NeoForge 1.21.1 variant: no render states, so the distance is taken from the entity itself
@Mixin(LivingEntityRenderer.class)
public abstract class LivingEntityLodMixin {
	// far entities skip their layers: armour, held items, eyes, cape, elytra, stuck arrows
	@WrapOperation(method = "render(Lnet/minecraft/world/entity/LivingEntity;FFLcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/client/renderer/MultiBufferSource;I)V",
			at = @At(value = "INVOKE", target = "Lnet/minecraft/client/renderer/entity/layers/RenderLayer;render(Lcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/client/renderer/MultiBufferSource;ILnet/minecraft/world/entity/Entity;FFFFFF)V"))
	private void zakoopt$farLayers(RenderLayer<?, ?> layer, PoseStack pose, MultiBufferSource buffers, int light, Entity entity,
								   float a, float b, float c, float d, float e, float f, Operation<Void> original) {
		double dist = Minecraft.getInstance().gameRenderer.getMainCamera().getPosition().distanceToSqr(entity.getX(), entity.getY(), entity.getZ());
		if (entity instanceof Player ? EntityLod.farPlayer(dist) : EntityLod.far(dist)) {
			return;
		}
		original.call(layer, pose, buffers, light, entity, a, b, c, d, e, f);
	}
}

package zako.opt.mixin;

import net.minecraft.client.gui.screens.TitleScreen;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import zako.opt.ZakoOptConfig;
import zako.opt.bench.Bench;

@Mixin(TitleScreen.class)
public class TitleScreenUpdateMixin {
	@Inject(method = "tick", at = @At("HEAD"))
	private void zakoopt$welcome(CallbackInfo ci) {
		if (!ZakoOptConfig.welcomed) {
			ZakoOptConfig.welcomed = true;
			ZakoOptConfig.save();
			Bench.welcome((TitleScreen) (Object) this);
		}
	}
}

package zako.opt;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.client.gui.IConfigScreenFactory;

// the NeoForge entry point: Fabric starts the mod through fabric.mod.json's entrypoints, here FML finds this class
@Mod(value = "zakoopt", dist = Dist.CLIENT)
public final class ZakoOptMod {
	public ZakoOptMod(ModContainer container) {
		// the same screen Mod Menu opens on Fabric: the mod list's "Config" button
		container.registerExtensionPoint(IConfigScreenFactory.class, (mod, parent) -> new ZakoOptScreen(parent));
	}
}

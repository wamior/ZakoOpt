package zako.opt.loader;

import net.neoforged.fml.ModList;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.fml.loading.LoadingModList;

import java.nio.file.Path;
import java.util.Optional;

/**
 * NeoForge stand-in for the small part of Fabric Loader's API that the shared ZakoOpt sources use.
 * The build rewrites {@code import net.fabricmc.loader.api.FabricLoader} to this class, so upstream files stay untouched.
 */
public final class FabricLoader {
	private static final FabricLoader INSTANCE = new FabricLoader();

	private FabricLoader() {
	}

	public static FabricLoader getInstance() {
		return INSTANCE;
	}

	// Mixin plugins run before ModList exists, so the early LoadingModList answers until it does
	public boolean isModLoaded(String id) {
		ModList mods = ModList.get();
		if (mods != null) {
			return mods.isLoaded(id);
		}
		LoadingModList early = LoadingModList.get();
		return early != null && early.getModFileById(id) != null;
	}

	public Path getConfigDir() {
		return FMLPaths.CONFIGDIR.get();
	}

	public Optional<ModContainer> getModContainer(String id) {
		ModList mods = ModList.get();
		if (mods != null) {
			return mods.getModContainerById(id).map(c -> new ModContainer(c.getModInfo().getDisplayName(), c.getModInfo().getVersion().toString()));
		}
		LoadingModList early = LoadingModList.get();
		if (early != null && early.getModFileById(id) != null) {
			var info = early.getModFileById(id).getMods().stream().filter(m -> m.getModId().equals(id)).findFirst();
			return info.map(m -> new ModContainer(m.getDisplayName(), m.getVersion().toString()));
		}
		return Optional.empty();
	}

	public static final class ModContainer {
		private final Metadata metadata;

		ModContainer(String name, String version) {
			this.metadata = new Metadata(name, version);
		}

		public Metadata getMetadata() {
			return metadata;
		}
	}

	public static final class Metadata {
		private final String name;
		private final Version version;

		Metadata(String name, String version) {
			this.name = name;
			this.version = new Version(version);
		}

		public String getName() {
			return name;
		}

		public Version getVersion() {
			return version;
		}
	}

	public static final class Version {
		private final String text;

		Version(String text) {
			this.text = text;
		}

		public String getFriendlyString() {
			return text;
		}
	}
}

package zako.opt.block;

import lombok.experimental.UtilityClass;
import net.caffeinemc.mods.sodium.client.world.LevelSlice;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.state.BlockState;

// NeoForge 1.21.1 variant: BlockState.isSolidRender takes the level and position here
@UtilityClass
public class LeafCulling {
	public boolean hidden(BlockState self, LevelSlice slice, BlockPos pos, Direction dir) {
		if (!(self.getBlock() instanceof LeavesBlock)) {
			return false;
		}
		int x = pos.getX() + dir.getStepX(), y = pos.getY() + dir.getStepY(), z = pos.getZ() + dir.getStepZ();
		if (!(slice.getBlockState(x, y, z).getBlock() instanceof LeavesBlock)) {
			return false;
		}
		int bx = x + dir.getStepX(), by = y + dir.getStepY(), bz = z + dir.getStepZ();
		BlockState beyond = slice.getBlockState(bx, by, bz);
		return beyond.getBlock() instanceof LeavesBlock || beyond.isSolidRender(slice, new BlockPos(bx, by, bz));
	}
}

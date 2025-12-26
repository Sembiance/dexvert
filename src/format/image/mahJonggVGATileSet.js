import {Format} from "../../Format.js";

export class mahJonggVGATileSet extends Format
{
	name           = "Mah Jonngg -V-G-A- Tile Set";
	website        = "http://fileformats.archiveteam.org/wiki/Mah_Jongg_-V-G-A-_tile_set";
	ext            = [".tis", ".til", ".icn", ".cfg"];
	forbidExtMatch = true;
	magic          = ["Mah Jongg -V-G-A-/Windows TileSet", "deark: mjvga"];
	auxFiles       = (input, otherFiles) =>
	{
		// .tis can convert on it's own, but .icn and .til can optionally use a pal.cfg file
		const otherFile = otherFiles.find(file => file.base.toLowerCase()===`pal.cfg`);
		return otherFile ? [otherFile] : false;
	};
	converters = dexState => [`deark[module:mjvga]${dexState.f.aux ? `[file2:${dexState.f.aux.base}]` : ""}`];
}

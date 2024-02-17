import {Format} from "../../Format.js";

const _COMPACT_PRO_MAGIC = ["Mac Compact Pro archive", "Compact Pro"];
export {_COMPACT_PRO_MAGIC};

export class compactPro extends Format
{
	name       = "Mac Compact Pro Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Compact_Pro";
	ext        = [".cpt"];
	magic      = _COMPACT_PRO_MAGIC;
	priority   = this.PRIORITY.LOW;
	converters = ["unar[mac]", "macunpack"];
}

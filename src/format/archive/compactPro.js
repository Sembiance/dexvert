import {Format} from "../../Format.js";

export class compactPro extends Format
{
	name       = "Mac Compact Pro Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Compact_Pro";
	ext        = [".cpt"];
	magic      = ["Mac Compact Pro archive", "Compact Pro"];
	idMeta     = ({macFileType}) => macFileType==="PACT";
	priority   = this.PRIORITY.LOW;
	converters = ["unar[type:Compact Pro][mac]", "macunpack"];
}

import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class ybm extends Format
{
	name           = "Bennet Yee's Face Format";
	website        = "http://fileformats.archiveteam.org/wiki/YBM";
	ext            = [".bm", ".ybm"];
	forbidExtMatch = [".bm"];
	magic          = ["Bennet Yee's face format bitmap", "deark: ybm"];
	forbiddenMagic = TEXT_MAGIC;
	converters     = ["ybmtopbm[matchType:magic]", "deark[module:ybm][strongMatch]"];
	verify         = ({meta}) => meta.height>1 && meta.width>1 && (meta.width/meta.height)<14 &&(meta.height/meta.width)<14;
}

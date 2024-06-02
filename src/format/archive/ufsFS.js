import {Format} from "../../Format.js";

export class ufsFS extends Format
{
	name       = "Unix Fast File system (UFS)";
	website    = "http://fileformats.archiveteam.org/wiki/UFS";
	magic      = ["Unix Fast File system", "UFS file system"];
	converters = ["old", "ufs2", "44bsd", "5xbsd", "sun", "sunx86", "sunos", "hp", "nextstep", "openstep"].map(fmt => `uniso[type:ufs][options:ufstype=${fmt}]`);
}

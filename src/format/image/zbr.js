import {Format} from "../../Format.js";

export class zbr extends Format
{
	name       = "Zoner Zebra";
	website    = "http://fileformats.archiveteam.org/wiki/ZBR_(Zoner_Zebra)";
	ext        = [".zbr"];
	magic      = ["Zebra metafile", "deark: zbr"];
	notes      = "reaConverter is the only program I know of that can convert to SVG but it fails to do so with QEMU WinXP 32bit (used to work in wine). So for now, we just convert to PNG.";
	trustMagic = true;
	converters = ["nconvert", "deark[module:zbr][matchType:magic][hasExtMatch]"];
	verify     = ({meta}) => meta.colorCount>2;
}

import {Format} from "../../Format.js";

export class a2gsPreferred extends Format
{
	name       = "Apple IIGS Preferred Format";
	website    = "http://fileformats.archiveteam.org/wiki/Apple_II_graphics_formats";
	ext        = [".gs", ".iigs", ".pnt", ".shr"];
	filename   = [/#C0000[012]$/];	// eslint-disable-line unicorn/better-regex
	magic      = ["Apple IIGS Preferred Format"];
	converters = ["recoil2png[format:SHR.ApfShr,GS,PNT.ApfShr,32K,PNT.Paintworks,IIGS,PNT.AppleIIShr]"];
	priority   = ({magicMatch}) => (magicMatch ? this.PRIORITY.STANDARD : this.PRIORITY.LOW);
	verify     = ({meta}) => meta.colorCount>1;
}

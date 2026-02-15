import {Format} from "../../Format.js";

export class a2gsSHStar extends Format
{
	name       = "Apple IIGS SH3/SHR";
	website    = "http://fileformats.archiveteam.org/wiki/Apple_II_graphics_formats";
	ext        = [".sh3", ".shr"];
	filename   = [/#C0000[012]$/];	// eslint-disable-line unicorn/better-regex
	fileSize   = {".sh3" : 38400, ".shr" : [38400, "*"]};
	safeExt    = dexState =>
	{
		let ext = (Object.entries({"#C00000" : ".pnt", "#C00001" : ".shr", "#C00002" : ".shr"}).find(([suffix]) => dexState.f.input.base.endsWith(suffix))?.[1] || null);
		ext ||= ({"PNT" : ".pnt"})[dexState.original.input?.meta?.proDOSTypeCode] || null;
		ext ||= ({"PIC" : ".pic"})[dexState.original.input?.meta?.proDOSTypeCode] || null;
		return ext;
	};
	idMeta     = ({proDOSTypeCode}) => ["PIC", "PNT"].includes(proDOSTypeCode);
	converters = ["recoil2png[format:SHR.AppleIIShr,SHR.Sh3,SH3.Sh3,SH3.ApfShr]"];
	notes      = "Suffix #C00002 is usually captured by a2gsPreferred magic, but is here just in case it isn't.";
	verify     = ({meta}) => meta.colorCount>1;
}

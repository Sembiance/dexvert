import {Format} from "../../Format.js";

export class a2gsSHStar extends Format
{
	name       = "Apple IIGS SH3/SHR";
	ext        = [".sh3", ".shr"];
	filename   = [/#C0000[012]$/];	// eslint-disable-line unicorn/better-regex
	fileSize   = {".sh3" : 38400, ".shr" : 38400};
	safeExt    = dexState => (Object.entries({"#C00000" : ".pnt", "#C00001" : ".shr", "#C00002" : ".shr"}).find(([suffix]) => dexState.f.input.base.endsWith(suffix))?.[1] || null);
	converters = ["recoil2png"];
	notes      = "Suffix #C00002 is usually captured by a2gsPreferred magic, but is here just in case it isn't.";
	verify     = ({meta}) => meta.colorCount>1;
}

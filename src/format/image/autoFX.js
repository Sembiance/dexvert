import {Format} from "../../Format.js";

export class autoFX extends Format
{
	name       = "Auto/FX Image";
	ext        = [".afx"];
	idMeta     = ({macFileType}) => [".AFX"].includes(macFileType);
	magic      = ["Auto/FX Image", "Auto F/X :afx:"];
	converters = ["nconvert[format:afx]"];
}

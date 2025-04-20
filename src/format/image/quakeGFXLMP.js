import {Format} from "../../Format.js";

export class quakeGFXLMP extends Format
{
	name         = "Quake 2D Graphic LMP";
	website      = "https://quakewiki.org/wiki/.lmp";
	ext          = [".lmp"];
	auxFiles     = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()==="palette.lmp");
	metaProvider = ["image"];
	converters   = ["lmp2ppm", "wuimg", "noesis[type:image]"];
}

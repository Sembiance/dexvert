import {Format} from "../../Format.js";

export class commandSimulationsGameGraphic extends Format
{
	name       = "Command Simulations game graphic";
	magic      = ["Command Simulations game graphics"];
	converters = ["deark[module:cs_ilbm][renameOut] -> dexvert[asFormat:image/iffILBM]", "wuimg[format:ilbm]"];
}


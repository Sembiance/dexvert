import {xu} from "xu";
import {Format} from "../../Format.js";

export class masterCook extends Format
{
	name        = "MasterCook Cookbook";
	ext         = [".mcf"];
	magic       = ["MasterCook Cookbook File"];
	unsupported = true;
	notes       = xu.trim`
		Was able to open samples with sandbox/app/MasterCook7.iso in WinXP, but couldn't find an easy way to export all recipes to text or PDF.
		I could write a script that would manually open every recipe, select all the text and copy it and save to disk, like I do with MacroMedia, but meh, overkill for recipes.`;
}

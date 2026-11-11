import {Format} from "../../Format.js";

export class thomasHermann extends Format
{
	name          = "Thomas Hermann Module";
	ext           = [".thm", ".smp"];
	matchPreExt   = true;
	keepFilename  = true;
	metaProvider  = ["musicInfo"];

	// Both .thm and .smp are required and are often prefix extensions
	auxFiles = (input, otherFiles) =>
	{
		const pre = this.ext.includes(input.preExt.toLowerCase());
		const exts = (pre ? input.preExt : input.ext).toLowerCase()===".smp" ? this.ext.filter(ext => ext!==".smp") : [".smp"];
		return otherFiles.filter(file => (pre ? file.preName : file.name).toLowerCase()===(pre ? input.preName : input.name).toLowerCase() && exts.includes((pre ? file.preExt : file.ext).toLowerCase()));
	};

	// Don't do anything with .smp files
	untouched       = ({f}) => (this.ext.includes(f.input.preExt.toLowerCase()) ? f.input.preExt : f.input.ext).toLowerCase()===".smp";
	verifyUntouched = false;

	converters = ["uade123[player:ThomasHermann]"];
}

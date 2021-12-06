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
		const preExtMatch = this.ext.some(ext => ext.toLowerCase()===input.preExt.toLowerCase());
		const otherExt = this.ext.find(ext => ext!==(preExtMatch ? input.preExt : input.ext));
		return otherFiles.filter(file => (preExtMatch ? file.preName.toLowerCase()===input.preName.toLowerCase() : file.name.toLowerCase()===input.name.toLowerCase()) && otherExt===(preExtMatch ? file.preExt : file.ext));
	};

	// Don't do anything with .smp files
	untouched = ({f}) => (f.input.ext.toLowerCase() || f.input.preExt.toLowerCase())===".smp";

	converters = ["uade123[player:ThomasHermann]"];
}
